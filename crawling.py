import pandas as pd
import numpy as np
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def beer_crawl(driver, beer, data, k):
 data = pd.DataFrame(data=[], columns=['맥주정보', '검색이름', '맥주이름'])

 print('url_open... {0} 맥주 데이터 수집'.format(beer))
 driver = webdriver.Chrome(chromedriver)
 driver.get(url)
 driver.set_window_size(900, 900)

 time.sleep(2)
 element = driver.find_element_by_xpath('//*[@id="root"]/div[2]/header/div[2]/div[1]/div[2]/div/div/input')
 time.sleep(2)
 element.click()
 time.sleep(2)
 element.send_keys(beer)
 time.sleep(2)

 driver.find_element_by_xpath('//*[@id="root"]/div[2]/header/div[2]/div[1]/div[2]/div/div[2]/a[1]/div/div[2]').click()
 time.sleep(2)
 beer_name = driver.find_element_by_css_selector('.MuiTypography-root.Text___StyledTypographyTypeless-bukSfn.pzIrn.text-500.colorized__WrappedComponent-hrwcZr.hwjOn.mt-3.MuiTypography-h4').text
 error_cnt = 0

 while 1:
  try:
   time.sleep(2)
   string = driver.find_element_by_class_name('MuiTypography-root.Text___StyledTypographyTypeless-bukSfn.pzIrn.text-500.colorized__WrappedComponent-hrwcZr.hwjOn.MuiTypography-h6').text

   extract = re.compile('[0-9]*,*[0-9]+')
   str_num = extract.findall(string)
   str_num = str_num[0]

   print('성공.')
   break
  except:
   print('오류 발생. 재시작.')

   error_cnt += 1

   if error_cnt == 5:
    print('연속된 오류. 다음 맥주로 넘어감.')
    return

 if ',' in str_num:
  str_num = str_num.split(',')
  str_num = int(str_num[0] + str_num[1])
  num = str_num
 else:
  num = int(str_num)

 time.sleep(2)
 element = driver.find_element_by_xpath('//*[@id="root"]/div[2]/div[2]/div/div/div/div[2]/div[4]/div/div[2]/div[1]/div[2]')
 time.sleep(2)
 driver.execute_script("arguments[0].click();", element)
 page_num = num // 15 + 1

 for i in range(page_num):
  print(i + 1, '번째 페이지.')

  time.sleep(2)
  beer_info = driver.find_elements_by_css_selector('.px-4.fj-s.f-wrap')

  tmp = []

  for i in range(len(beer_info)):
   tmp.append(beer_info[i].text)

  tmp = pd.DataFrame(data=tmp, columns=['맥주정보'])
  tmp['맥주이름'] = beer_name
  tmp['검색이름'] = beer
  data = pd.concat([data, tmp])

  try:
   element = driver.find_element_by_xpath('//button[@title="Next page"]/span[@class="MuiIconButton-label"]')
   time.sleep(3)
   driver.execute_script("arguments[0].click();", element)
  except:
   print('마지막 페이지.')

 if num != len(data):
  data = data[:num]

 print('리뷰수 : ', num, '수집된 리뷰수 : ', len(data))

 result = pd.merge(data, beer_list, on='검색이름', how='left')
 result.to_csv("beer_n_" + str(k) + ".csv", encoding='utf-8-sig')
 result.to_excel("beer_n_" + str(k) + ".xlsx")

 driver.quit()

 return result

beer_list = ['Goose Island Goose IPA', 'Goose Island 312 Urban Wheat Ale', 'Edelweiss Weissbier Hefetrüb',
             'Somersby Apple Cider', 'Apple Fox', 'Desperados', 'Egger Grapefruit Radler', 'Egger Radler',
             'Stella Artois', 'Hoegaarden', 'Hoegaarden Rosée', 'Budweiser', 'Patagonia Bohemian Pilsener',
             'Kronenbourg 1664 Blanc', 'Erdinger Weissbier', 'Paulaner Hefe-Weissbier', 'Paulaner Hefeweissbier Dunkel',
             'Tiger Beer', 'Guinness Draught', 'Carlsberg Pilsner', 'Heineken', 'San Miguel Pale Pilsen',
             'Tsingtao', 'Tsingtao Draft Beer 11º (Pure Draft Beer)', 'Cass Fresh', 'Hite Beer', 'Kloud Original Gravity',
             'Terra', 'Max Cream', 'FiLite', 'Jeju Wit Ale', 'Jeju Pellong Ale', 'Jeju Baengnokdam Ale', 'HiteJinro Isul Tok Tok',
             'Kabrew Gyeongbokgung Royal Pride IPA', 'ARK Seoulite Ale', 'Hop House 13 Lager', 'Blue Moon Belgian White',
             'Volfas Engelman Pasaulio Skoniai IPA', 'Pilsner Urquell', 'Kozel Černý (Dark) 10°',
             'Sapporo Premium Beer', 'Kirin Ichiban', 'Suntory The Premium', 'Sapporo Yebisu', 'Asahi Super Dry',
             'Kabrew Kumiho Peach Ale', 'Cafri', 'Becks']

beer_list = pd.DataFrame(data=beer_list, columns=['검색이름'])
data = pd.DataFrame(data=[], columns=['맥주정보', '검색이름', '맥주이름'])
chromedriver = 'chromedriver.exe'
url = 'https://www.ratebeer.com/search?tab=beer'

driver = webdriver.Chrome(chromedriver)
driver.get(url)
driver.set_window_size(900, 900)
time.sleep(1)

for k in range(len(beer_list)):
    result = beer_crawl(driver, beer_list['검색이름'].iloc[k], data, k)