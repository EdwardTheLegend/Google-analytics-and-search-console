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

 
parser = argparse.ArgumentParser()

# not specifying default default=""  so that this script won't allow an empty account name
parser.add_argument("-g","--googleaccount",type=str, required=True, help="Name of a google account; does not have to literally be the account name but becomes a token to access that particular set of secrets. Client secrets will have to be in this a file that is this string concatenated with client_secret.json")

args = parser.parse_args()

googleaccountstring = args.googleaccount



# Authenticate and construct service.
analytics = get_service('analytics', 'v3', ['https://www.googleapis.com/auth/analytics.readonly'], 'client_secrets.json', googleaccountstring)
webmaster = get_service('webmasters', 'v3', ['https://www.googleapis.com/auth/webmasters.readonly'], 'client_secrets.json', googleaccountstring)

