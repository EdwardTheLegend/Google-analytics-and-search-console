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
from pandas import ExcelWriter
import openpyxl
from googleAPIget_service import get_service
from progress.bar import IncrementalBar
#import sys

win_unicode_console.enable()

debugvar = False

parser = argparse.ArgumentParser()

#when doing argument parsing in command terminal put python before file name. No idea why, so just do it.


#parser.add_argument("viewProfileID",type=int, help="GA View (profile) ID as a number") !!!already got this from loop!!!
parser.add_argument("start_date", help="start date in format yyyy-mm-dd or 'yesterday' '7DaysAgo'")
parser.add_argument("end_date", help="start date in format yyyy-mm-dd or 'today'")
parser.add_argument("-f","--filters",default=2,type=int, help="Minimum number for metric, default is 2")
parser.add_argument("-d","--dimensions",default="ga:pagePath", help="The dimensions are the left hand side of the table, default is pagePath. YOU HAVE TO ADD 'ga:' before your dimension")
parser.add_argument("-m","--metrics",default="ga:pageviews", help="The metrics are the things on the left, default is pageviews. YOU HAVE TO ADD 'ga:' before your metric")
parser.add_argument("-n","--name",default='analytics-' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),type=str, help="File name for final output, default is analytics- + the current date. You do NOT need to add file extension.")
parser.add_argument("-t","--test",type=int,help="Test option which makes the script output only n results, default is 3.")
#parser.add_argument("-c", "--clean", action="count", default=0, help="clean output skips header and count and just sends csv rows")

parser.add_argument("-g","--googleaccount",type=str, default="", help="Name of a google account; does not have to literally be the account name but becomes a token to access that particular set of secrets. Client secrets will have to be in this a file that is this string concatenated with client_secret.json.  OR if this is the name of a text file then every line in the text file is processed as one user and all results appended together into a file file")

args = parser.parse_args()

start_date = args.start_date
end_date = args.end_date
filters = args.filters
dimensions = args.dimensions
metrics = args.metrics
name = args.name
test = args.test
googleaccountstring = args.googleaccount

options = [[start_date,end_date,filters,dimensions,metrics,name,googleaccountstring]]
optionsdf = pd.DataFrame(options, columns=["start_date","end_date","filters","dimensions","metrics","name","Google Account"])
if debugvar: print(optionsdf)

scope = ['https://www.googleapis.com/auth/analytics.readonly']

try:
    googleaccountslist = open(googleaccountstring).read().splitlines()
    # remove empty lines
    googleaccountslist = [x.strip() for x in googleaccountslist if x.strip()]
except:
    googleaccountslist = [googleaccountstring]

if debugvar: print(googleaccountslist)

if dimensions == "pagePath":
    combinedDF = pd.DataFrame(columns=['viewid','Url',dimensions,metrics])
else:
    combinedDF = pd.DataFrame(columns=['viewid',dimensions,metrics])
    

for thisgoogleaccount in googleaccountslist:
    if debugvar: print(thisgoogleaccount)
    if dimensions == "pagePath":
        bigdf = pd.DataFrame(columns=['viewid','Url',dimensions,metrics])
    else:
        bigdf = pd.DataFrame(columns=['viewid',dimensions,metrics])
    

    # Authenticate and construct service.
    service = get_service('analytics', 'v3', scope, 'client_secrets.json', thisgoogleaccount)

    profiles = service.management().profiles().list(
    accountId='~all',
    webPropertyId='~all').execute()
    #profiles is now list    

    if debugvar: print("Processing: " + thisgoogleaccount)
    if debugvar: print("Total profiles: " + str(profiles['totalResults']))

    bar = IncrementalBar('Processing',max=profiles['totalResults'])

    itemcounter = 0

    for item in profiles['items']:
        if test is not None:
            if itemcounter == test:
                break
        bar.next()
        if 'starred' in item:
            smalldf = pd.DataFrame()
            if debugvar: print(item['id'] + ',' + start_date + ',' + end_date)
            
            if debugvar: print("Try querying: "+ str(item['id'])+":"+  item['websiteUrl'])
            try:
                results = service.data().ga().get(
                ids='ga:' + str(item['id']),
                start_date=start_date,
                end_date=end_date,
                filters='ga:pageviews>' + str(filters),
                #sort='-ga:pageviews',
                max_results='1000',
                dimensions= dimensions,
                metrics= metrics).execute()
            except:
                if debugvar: print("GA call failed for " + item['websiteUrl'])
                results['totalResults'] = 0

            if results['totalResults'] > 0:
                if debugvar: print("returned rows: " + str(results['rows']))
                if debugvar: print(smalldf)
                smalldf = smalldf.append(results['rows'])
                if debugvar: print(smalldf)
                smalldf.columns = [dimensions,metrics]
                if debugvar: print(smalldf)
            
                smalldf.insert(0,'viewid',item['id'])
                if debugvar: print(smalldf)

                smalldf.insert(1,'websiteUrl',item['websiteUrl'])
                if dimensions == "pagePath":
                    smalldf['Url'] = smalldf['websiteUrl'] + smalldf[dimensions]
                

                bigdf = pd.concat([bigdf,smalldf],sort=True)
                if debugvar: print(bigdf)
        itemcounter = itemcounter + 1
    bar.finish()

    # Got the bigdf now of all the data from this account, so add it into the combined
    combinedDF = pd.concat([combinedDF,bigdf],sort=True)

    # Probably not necessary to actually delete them, but makes the code easier for me to understand
    #del smalldf
    del bigdf
    del profiles
    del service

# Finished collecting everything, time to output to a file
if googleaccountstring > "" :
    name = googleaccountstring + "-" + name 

combinedDF['ga:pageviews'] = combinedDF['ga:pageviews'].astype(int)

combinedDF.reset_index()

with ExcelWriter(name + '.xlsx') as writer:
  combinedDF.to_excel(writer, sheet_name='data')
  optionsdf.to_excel(writer,sheet_name="Options")
print("finished and outputed to excel file")

