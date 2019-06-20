import argparse
import datetime
import win_unicode_console
from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import argparse
import pandas as pd
import openpyxl
from googleAPIget_service import get_service

win_unicode_console.enable()



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

parser.add_argument("-g","--googleaccount",type=str, default="", help="Name of a google account; does not have to literally be the account name but becomes a token to access that particular set of secrets. Client secrets will have to be in this a file that is this string concatenated with client_secret.json")

args = parser.parse_args()

start_date = args.start_date
end_date = args.end_date
filters = args.filters
dimensions = args.dimensions
metrics = args.metrics
name = args.name
googleaccountstring = args.googleaccount


scope = ['https://www.googleapis.com/auth/analytics.readonly']
# Authenticate and construct service.
service = get_service('analytics', 'v3', scope, 'client_secrets.json', googleaccountstring)
profiles = service.management().profiles().list(
accountId='~all',
webPropertyId='~all').execute()
#profiles is now list    

print(profiles['totalResults'])

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
            print(bigdf)

if googleaccountstring > "" :
    name = googleaccountstring + "-" + name 

bigdf.to_excel(name + '.xlsx', sheet_name='data')
print("finished")

