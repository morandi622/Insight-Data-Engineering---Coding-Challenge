

import numpy as np, pandas as pd, sys

if len(sys.argv) <4:
    print 'Syntax: python ./src/donation-analytics.py ./input/itcont.txt ./input/percentile.txt ./output/repeat_donors.txt'
    exit()



def f_zip_code(str): #parse zip codes
    _str=str[:5] if ((len(str)>=5) & str.isdigit()) else np.nan
    return _str

def repeat_donor(group): #find repeat donors
    t=group.TRANSACTION_DT.values
    group['repeat_donors'] = (t > t[0])
    return group

q=pd.read_csv(sys.argv[2],header=None).values[0][0] #reading percentile q of running percentile
unames = ['CMTE_ID','NAME','ZIP_CODE','TRANSACTION_DT','TRANSACTION_AMT','OTHER_ID'] #column to fetch

dateparse = lambda x: pd.to_datetime(x, format='%m%d%Y',errors='coerce')  #date parser

pieces = []
_df=pd.read_table(sys.argv[1],sep='|',header=None,engine='python',names=unames, usecols=[0,7,10,13,14,15],converters={'ZIP_CODE':f_zip_code},parse_dates=['TRANSACTION_DT'],date_parser=dateparse,iterator=True,chunksize=100000) #data set is split into "pieces" of chunksize rows and via a iterator

while True:
        try:
            df=next(_df) # the sub-dataframe obtained from iterating over sequence
            df.dropna(subset=['NAME','ZIP_CODE','TRANSACTION_DT','CMTE_ID','TRANSACTION_AMT'],inplace=True) #dropping NAN values
            df=df[df.OTHER_ID.isnull()] # keeping rows with empty OTHER_ID
            df.drop(['OTHER_ID'],axis=1,inplace=True)
            pieces.append(df)  #appending sub-dataframes
        except StopIteration:
            break  # Iterator exhausted: stop the loop

df = pd.concat(pieces,ignore_index=True) #concatenating sub-dataframes
df['ID']=df['NAME'].values+'_'+df['ZIP_CODE'].values  # creating unique IDs based on NAME and ZIP_CODE
df.drop(['NAME'],axis=1,inplace=True)
df=df[df.duplicated(subset=['ID'],keep=False)] #removing single-entry lines which cannot clearly contains repeat donors
df=df.groupby(by='ID').apply(repeat_donor)  # finding repeat donors
df=df[df.repeat_donors]  # selecting only rows corresponding to repeat donors
df['year'] = df.TRANSACTION_DT.apply(lambda x: x.year) #extracting year from the date
df.drop(['TRANSACTION_DT','repeat_donors'],axis=1,inplace=True)

df.sort_values(by=['CMTE_ID', 'ZIP_CODE', 'year'],inplace=True)  #sorting dataframe by 'CMTE_ID', 'ZIP_CODE', 'year'
df['total_number_contributions'] = 1; df['total_dollar_amount']=np.nan
df[['total_dollar_amount','total_number_contributions']]=df.groupby(['CMTE_ID', 'ZIP_CODE', 'year'])['TRANSACTION_AMT','total_number_contributions'].cumsum().values  #total number of transactions and contributions received by recipient from the contributor's zip code streamed in so far this calendar year from repeat donors

df['percentile_contribution'] = df.groupby(['CMTE_ID', 'ZIP_CODE', 'year']).TRANSACTION_AMT.\
    expanding(min_periods=1).\
    apply(func=np.percentile,args=(q,None,None,None,'nearest'))\
    .round().astype(int).values #running percentile of contributions received from repeat donors to a recipient streamed in so far for this zip code and calendar year


df.loc[:,['CMTE_ID', 'ZIP_CODE', 'year','percentile_contribution','total_dollar_amount','total_number_contributions']].to_csv(sys.argv[3],sep='|', index=False, header=False) #writing output


