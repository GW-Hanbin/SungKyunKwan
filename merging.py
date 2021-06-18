import pandas as pd

data = pd.DataFrame(data=[], columns = ['맥주정보', '검색이름', '맥주이름'])
#csv파일 갯수
files = 49

for k in range(files):
    try:
        tmp = pd.read_csv(r'C:\Users\lhb94\Documents\GitHub\SungKyunKwan\beer_n_'+str(k)+'.csv', index_col = 0)
        data = pd.concat([data, tmp])

    except:
        print(k, '번째에서 오류 발생')

data = data[['맥주이름', '맥주정보']]
data.to_csv('pre_data.csv', encoding = 'utf-8-sig')
