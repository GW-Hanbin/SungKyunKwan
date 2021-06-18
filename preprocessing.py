import pandas as pd
import re

data = pd.read_csv('pre_data.csv', encoding='utf-8-sig', index_col = 0)
reg = re.compile('[0-9]+.+[0-9]+[A-Za-z0-9]*')

tmp = data.copy()
tmp['맥주정보'] = tmp['맥주정보'].str.split('\n')

ttmp = tmp.copy()

ttmp['맥주정보'] = ttmp['맥주정보'].apply(lambda x: x if x[-2] =='Overall' else x[:-1])
ttmp['맥주정보'] = ttmp['맥주정보'].apply(lambda x: x[:4] + x[:-11:-1])

ttmp['ID'] = ttmp['맥주정보'].apply(lambda x: x[0])
ttmp['Aroma'] = ttmp['맥주정보'].apply(lambda x: x[-2])
ttmp['Appearance'] = ttmp['맥주정보'].apply(lambda x: x[-4])
ttmp['Flavor'] = ttmp['맥주정보'].apply(lambda x: x[-6])
ttmp['Mouthfeel'] = ttmp['맥주정보'].apply(lambda x: x[-8])
ttmp['Overall'] = ttmp['맥주정보'].apply(lambda x: x[-10])

ttmp['맥주정보'] = ttmp['맥주정보'].apply(lambda x: x[1:4])
ttmp['길이'] = ttmp['맥주정보'].apply(lambda x: len(x))

ttmp['맥주정보'] = ttmp['맥주정보'].apply(lambda x: x[0] if reg.match(x[0]) else (x[1] if reg.match(x[1]) else x[2]))

ttmp['평점'] = ttmp['맥주정보'].apply(lambda x : x[:3])
ttmp['날짜'] = ttmp['맥주정보'].apply(lambda x : x[3:])

# 컬럼명 변경
ttmp.columns = ['맥주이름', '맥주정보', '아이디', 'Aroma', 'Appearance', 'Flavor',
       'Mouthfeel', 'Overall', '길이', '평점', '날짜']

# 필요한 컬럼만 추출
ttmp = ttmp[['아이디', '맥주이름', '날짜', '평점', 'Aroma', 'Appearance', 'Flavor',
       'Mouthfeel', 'Overall']]

ttmp = ttmp[ttmp['Aroma'] != '-']
ttmp = ttmp[ttmp['Appearance'] != '-']
ttmp = ttmp[ttmp['Flavor'] != '-']
ttmp = ttmp[ttmp['Mouthfeel'] != '-']
ttmp = ttmp[ttmp['Overall'] != '-']
ttmp[ttmp['Aroma'] == '-']
ttmp['평점'] = pd.to_numeric(ttmp['평점'])
ttmp['Aroma'] = pd.to_numeric(ttmp['Aroma'])
ttmp['Appearance'] = pd.to_numeric(ttmp['Appearance'])
ttmp['Flavor'] = pd.to_numeric(ttmp['Flavor'])
ttmp['Mouthfeel'] = pd.to_numeric(ttmp['Mouthfeel'])
ttmp['Overall'] = pd.to_numeric(ttmp['Overall'])
ttmp.drop_duplicates(keep='first', inplace=True)

ttmp.to_csv('afterPreprocessing.csv', encoding = 'utf-8-sig')