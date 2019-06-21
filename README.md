# Google-analytics-and-search-console
These script can scrape Google analytics and the Google search console for info about your websites.

# Usage

## NewDownloads.py
~~~~
usage: NewDownloads.py [-h] [-t {image,video,web}] [-d DIMENSIONS] [-n NAME]
                       [-g GOOGLEACCOUNT]
                       start_date end_date

positional arguments:
  start_date            start date in format yyyy-mm-dd or 'yesterday'
                        '7DaysAgo'
  end_date              start date in format yyyy-mm-dd or 'today'

optional arguments:
  -h, --help            show this help message and exit
  -t {image,video,web}, --type {image,video,web}
                        Search types for the returned data, default is web
  -d DIMENSIONS, --dimensions DIMENSIONS
                        The dimensions are the left hand side of the table,
                        default is page
  -n NAME, --name NAME  File name for final output, default is finaloutput +
                        the current date. You do NOT need to add file
                        extension.
  -g GOOGLEACCOUNT, --googleaccount GOOGLEACCOUNT
                        Name of a google account; does not have to literally
                        be the account name but becomes a token to access that
                        particular set of secrets. Client secrets will have to
                        be in this a file that is this string concatenated
                        with client_secret.json
~~~~
## GACombined2.py      

This script download from Google Analytics but ***ONLY*** views which are marked as starred/fav

~~~~
usage: GACombined2.py [-h] [-f FILTERS] [-d DIMENSIONS] [-m METRICS] [-n NAME]
                      [-g GOOGLEACCOUNT]
                      start_date end_date

positional arguments:
  start_date            start date in format yyyy-mm-dd or 'yesterday'
                        '7DaysAgo'
  end_date              start date in format yyyy-mm-dd or 'today'

optional arguments:
  -h, --help            show this help message and exit
  -f FILTERS, --filters FILTERS
                        Minimum number for metric, default is 2
  -d DIMENSIONS, --dimensions DIMENSIONS
                        The dimensions are the left hand side of the table,
                        default is pagePath
  -m METRICS, --metrics METRICS
                        The metrics are the things on the left, default is
                        pageviews
  -n NAME, --name NAME  File name for final output, default is finaloutput +
                        the current date. You do NOT need to add file
                        extension.
  -g GOOGLEACCOUNT, --googleaccount GOOGLEACCOUNT
                        Name of a google account; does not have to literally
                        be the account name but becomes a token to access that
                        particular set of secrets. Client secrets will have to
                        be in this a file that is this string concatenated
                        with client_secret.json. OR if this is the name of a
                        text file then every line in the text file is
                        processed as one user and all results appended
                        together into a file file
~~~~
#pip commands
copy and paste these into the terminal

~~~~
pip install argparse
pip install datetime
pip install win_unicode_console
pip install google-api-python-client
pip install pandas
pip install openpyxl
pip install progress
pip install oauth2client
~~~~

You need a Oauth2 account and put clients_secrets.json in same folder as script
https://developers.google.com/webmaster-tools/search-console-api-original/v3/quickstart/quickstart-python 

If you are using multiple google accounts then for every google account "email@example.com" create a secrets file called email@example.com-clients_secrets.json

# Detailed instructions for creating google client secrets

Navigate to:

https://console.developers.google.com/start/api?id=webmasters&credential=client_key

If promoted for agreement then:

Click I agree
Choose country
Say yes or no to emails
Click "Agree and continue"

Otherwise just click continue

**Wait patiently** until it says "The API is enabled".

You now have an empty project called "My Project", which you may rename.

Turn on the required APIs by going to:

https://console.developers.google.com/apis/library

If you have more than one project the select above.

Search for the two apis you need:

* Google Analytics API   (careful, *not* the "Google Analytics Reporting API")
* Google Search Console API  (should already be enabled)

For the first one click "Enable"

For the second one, it should already be enabled and you will have a "Manage" button

Now go back to your credentials screen:

https://console.developers.google.com/apis/credentials

Select the project if you have more than one

Click the button Create Credentials.

Choose "OAuth client ID" 

Click "Configure consent screen"

Specify a name such as "GA and GSC downloader"

Click Save

You are now back at the "Create OAuth client ID" page.

Choose Other

Specify a name "Python script" or leave default

Click "Create"

See the warning about 100 sensitive scope logins.

Click OK.

A single line of credentials is now created.

Click on the download icon to the far right.

rename the file either client_secrets.json for a single user or [string]-client_secrets.json where you will use the [string] value as an input for the -g arg

Create the .dat authenticatin files ahead of time by running authenticateoneuser.py

Run it twice to get both done.  Accept that the appication is not verified.
