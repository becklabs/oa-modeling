import pandas as pd

data =  pd.read_csv("../data/MWRA_TA_DIC_2017_to_2022.csv")
data['PROF_DATE_TIME_LOCAL'] = pd.to_datetime(data['PROF_DATE_TIME_LOCAL'])

ph = data[(data['pH ()'].notnull()) 
          & (data['VAL_QUAL'].isnull())
          & (data['PROF_DATE_TIME_LOCAL'].notnull())
          & (data['DEPTH (m)'] < 3)]

ph2 = data[(data['pH ()'].notnull()) 
          & (data['VAL_QUAL'].isnull())
          & (data['PROF_DATE_TIME_LOCAL'].notnull())
          & (data['SAMPLE_DEPTH_CODE'] == 'A')]       

print(pd.concat([ph, ph2]).drop_duplicates(keep=False))
#print(ph[~ph.apply(tuple,1).isin(ph2.apply(tuple,1))])
#ph['BIN_FIELD'] = [f'{date.month}/{date.year}' for date in ph['PROF_DATE_TIME_LOCAL']]

#for name, group in ph.groupby('BIN_FIELD', sort = False):
    #group.plot(x = 'LATITUDE', y = 'LONGITUDE', kind = 'scatter', title = f'{name} (A)')
    #print(f'{name}: {len(group["STAT_ID"].unique())}')
#shallow = ph[ph['DEPTH (m)'] < 3]

#deep = ph[ph['DEPTH (m)'] > 19]

#shallow.to_csv('shallow_concat.csv')

#deep.to_csv('deep_concat.csv')




