How to use Combined GSC dimentions.

NewDownloads.py

use multi dimentions in the -d argument separated by comma

-d page,query



import pandas as pd

d1 = {'z': ['a','b','c'],'teams': [['aSF', 'bNYG'],['cSF', 'dNYG'],['eSF', 'fNYG']]}

df2 = pd.DataFrame(d1)
print (df2)

df2[['team1','team2']] = pd.DataFrame(df2.teams.values.tolist(), index= df2.index)
print (df2)
del df2['teams']



