import argparse
import datetime
import win_unicode_console
from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import pandas as pd
from pandas import ExcelWriter
import openpyxl

win_unicode_console.enable()

# copied from original
def get_service(api_name, api_version, scope, client_secrets_path):
  """Get a service that communicates to a Google API.

  Args:
    api_name: string The name of the api to connect to.
    api_version: string The api version to connect to.
    scope: A list of strings representing the auth scopes to authorize for the
      connection.
    client_secrets_path: string A path to a valid client secrets file.

  Returns:
    A service that is connected to the specified API.
  """
  # Parse command-line arguments.
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser])
  flags = parser.parse_args([])

  # Set up a Flow object to be used if we need to authenticate.
  flow = client.flow_from_clientsecrets(
      client_secrets_path, scope=scope,
      message=tools.message_if_missing(client_secrets_path))

  # Prepare credentials, and authorize HTTP object with them.
  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to a file.
  storage = file.Storage(api_name + '.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, flags)
  http = credentials.authorize(http=httplib2.Http())

  # Build the service object.
  service = build(api_name, api_version, http=http)

  return service

scope = ['https://www.googleapis.com/auth/analytics.readonly']
# Authenticate and construct service.
service = get_service('analytics', 'v3', scope, 'client_secrets.json')
profiles = service.management().profiles().list(
accountId='~all',
webPropertyId='~all').execute()
#profiles is now list    

print("Total results:" + profiles['totalResults'])

parser = argparse.ArgumentParser()

#when doing argument parsing in command terminal put python before file name. No idea why, so just do it.


#parser.add_argument("viewProfileID",type=int, help="GA View (profile) ID as a number") !!!already got this from loop!!!
parser.add_argument("start_date", help="start date in format yyyy-mm-dd or 'yesterday' '7DaysAgo'")
parser.add_argument("end_date", help="start date in format yyyy-mm-dd or 'today'")
parser.add_argument("-f","--filters",default=2,type=int, help="Minimum number for metric, default is 2")
parser.add_argument("-d","--dimensions",default="pagePath", help="The dimensions are the left hand side of the table, default is pagePath")
parser.add_argument("-m","--metrics",default="pageviews", help="The metrics are the things on the left, default is pageviews")
parser.add_argument("-n","--name",default='finaloutput' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),type=str, help="File name for final output, default is finaloutput + the current date. You do NOT need to add file extension.")
#parser.add_argument("-c", "--clean", action="count", default=0, help="clean output skips header and count and just sends csv rows")

args = parser.parse_args()

start_date = args.start_date
end_date = args.end_date
filters = args.filters
dimensions = args.dimensions
metrics = args.metrics
name = args.name

# command line options record
options = [[start_date,end_date,filters,dimensions,metrics,name]]
optionsdf = pd.DataFrame(options, columns=["start_date","end_date","filters","dimensions","metrics","name"])
#print(optionsdf)

if dimensions == "pagePath":
    bigdf = pd.DataFrame(columns=['viewid','Url',dimensions,metrics])
else:
    bigdf = pd.DataFrame(columns=['viewid',dimensions,metrics])

for item in profiles['items']:
    if 'starred' in item:
        smalldf = pd.DataFrame()
        #print(item['id'] + ',' + start_date + ',' + end_date)
        
        try:
          results = service.data().ga().get(
          ids='ga:' + str(item['id']),
          start_date=start_date,
          end_date=end_date,
          filters='ga:pageviews>' + str(filters),
          #sort='-ga:pageviews',
          max_results='1000',
          dimensions='ga:' + dimensions,
          metrics='ga:' + metrics).execute()
        except:
            print("GA call failed for " + item['websiteUrl'])
            results['totalResults'] = 0

        if results['totalResults'] > 0:
            #print(results['rows'])
            #print(smalldf)
            smalldf = smalldf.append(results['rows'])
            #print(smalldf)
            smalldf.columns = [dimensions,metrics]
            #print(smalldf)
        
            smalldf.insert(0,'viewid',item['id'])
            #print(smalldf)

            smalldf.insert(1,'websiteUrl',item['websiteUrl'])
            if dimensions == "pagePath":
                smalldf['Url'] = smalldf['websiteUrl'] + smalldf[dimensions]
               

            bigdf = pd.concat([bigdf,smalldf])
            #print(bigdf)

bigdf.reset_index()

with ExcelWriter(name + '.xlsx') as writer:
  bigdf.to_excel(writer, sheet_name='data')
  optionsdf.to_excel(writer,sheet_name="Options")
print("finished and outputed to excel file")

