import argparse
import datetime
import time
import win_unicode_console
from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import pandas as pd
from pandas import ExcelWriter
import openpyxl
from progress.bar import IncrementalBar
from googleAPIget_service import get_service
from urllib.parse import urlparse

win_unicode_console.enable()


parser = argparse.ArgumentParser()

#when doing argument parsing in command terminal put python before file name. No idea why, so just do it.


#parser.add_argument("viewProfileID",type=int, help="GA View (profile) ID as a number") !!!already got this from loop!!!
parser.add_argument("start_date", help="start date in format yyyy-mm-dd or 'yesterday' '7DaysAgo'")
parser.add_argument("end_date", help="start date in format yyyy-mm-dd or 'today'")
parser.add_argument("-t", "--type", default="web", choices=("image","video","web"), help="Search types for the returned data, default is web")
#parser.add_argument("-f","--filters",default=2,type=int, help="Minimum number for metric, default is 2")
parser.add_argument("-d","--dimensions",default="page", help="The dimensions are the left hand side of the table, default is page. Options are date, query, page, country, device.  Combine two by specifying -d page,query ")
#parser.add_argument("-m","--metrics",default="pageviews", help="The metrics are the things on the left, default is pageviews")
parser.add_argument("-n","--name",default='search-console-[dimensions]-[datestring]',type=str, help="File name for final output, default is search-console- + the current date. You do NOT need to add file extension")
#parser.add_argument("-c", "--clean", action="count", default=0, help="clean output skips header and count and just sends csv rows")
parser.add_argument("-g","--googleaccount",type=str, default="", help="Name of a google account; does not have to literally be the account name but becomes a token to access that particular set of secrets. Client secrets will have to be in this a file that is this string concatenated with client_secret.json.  OR if this is the name of a text file then every line in the text file is processed as one user and all results appended together into a file file")
parser.add_argument("-w","--wait",type=int, default=0, help="Wait in seconds between API calls to prevent quota problems; default 0 seconds")

args = parser.parse_args()

start_date = args.start_date
end_date = args.end_date
wait_seconds = args.wait

dimensionsstring = args.dimensions
dimensionsarray = dimensionsstring.split(",")
multidimention = len(dimensionsarray) > 1

name = args.name
dataType = args.type
googleaccountstring = args.googleaccount

if name == 'search-console-[dimensions]-[datestring]':
    name = 'search-console-' + dimensionsstring + '-' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

scope = ['https://www.googleapis.com/auth/webmasters.readonly']


try:
    googleaccountslist = open(googleaccountstring).read().splitlines()
    # remove empty lines
    googleaccountslist = [x.strip() for x in googleaccountslist if x.strip()]
except:
    googleaccountslist = [googleaccountstring]

#print(googleaccountslist)

combinedDF = pd.DataFrame()

for thisgoogleaccount in googleaccountslist:
    print("Processing: " + thisgoogleaccount)
    # Authenticate and construct service.
    service = get_service('webmasters', 'v3', scope, 'client_secrets.json', thisgoogleaccount)
    profiles = service.sites().list().execute()
    #profiles is now list    

    #print("Len Profiles siteEntry: " + str(len(profiles['siteEntry'])))

    if 'siteEntry' not in profiles:
        print("No siteEntry found for this profile")
        continue

    bar = IncrementalBar('Processing',max=len(profiles['siteEntry']))


    bigdf = pd.DataFrame()

    for item in profiles['siteEntry']:
        bar.next()
        if item['permissionLevel'] != 'siteUnverifiedUser':

            smalldf = pd.DataFrame()
            if wait_seconds > 0:
                # print("Sleeping %4d seconds" % (wait_seconds))
                time.sleep(wait_seconds)

            #print(item['id'] + ',' + start_date + ',' + end_date)
            results = service.searchanalytics().query(
            siteUrl=item['siteUrl'], body={
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': dimensionsarray,
                'searchType': dataType,
                'rowLimit': 25000
            }).execute()

            if len(results) == 2:
                #print(results['rows'])
                #print(smalldf)
                smalldf = smalldf.append(results['rows'])
                #print(smalldf)

                if multidimention:
                    #solves key1 reserved word problem
                    smalldf[['key-1','key-2']] = pd.DataFrame(smalldf['keys'].tolist(), index= smalldf.index)
                    smalldf['keys']

                rootDomain = urlparse(item['siteUrl']).hostname
                if 'www.' in rootDomain:
                    rootDomain = rootDomain.replace('www.','')

                smalldf.insert(0,'siteUrl',item['siteUrl'])
                smalldf.insert(0,'rootDomain',rootDomain)
                #print(smalldf)
                if len(bigdf.columns) == 0:
                    bigdf = smalldf.copy()
                else:
                    bigdf = pd.concat([bigdf,smalldf])

                #print(bigdf)
    bar.finish()

    bigdf.reset_index()
    #bigdf.to_json("output.json",orient="records")

    if len(bigdf) > 0:
        bigdf['keys'] = bigdf["keys"].str[0]

        # Got the bigdf now of all the data from this account, so add it into the combined
        combinedDF = pd.concat([combinedDF,bigdf],sort=True)

    # clean up objects used in this pass
    del bigdf
    del profiles
    del service


if len(combinedDF) > 0:
    if googleaccountstring > "" :
        name = googleaccountstring + "-" + name 

    options = [[start_date,end_date,dimensionsstring,name,dataType,googleaccountstring]]
    optionsdf = pd.DataFrame(options, columns=["start_date","end_date","dimensions","name","Data Type","Google Account"])

    combinedDF.reset_index()

    with ExcelWriter(name + '.xlsx') as writer:
        combinedDF.to_excel(writer, sheet_name='data')
        optionsdf.to_excel(writer,sheet_name="Options")
        print("finished and outputed to excel file")
else:
    print("nothing found")
