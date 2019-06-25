
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
