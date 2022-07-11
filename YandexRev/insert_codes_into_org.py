import mysql.connector as connection
import pandas as pd
import numpy as np
import datetime

mydb = connection.connect(host="localhost", database='tno_rev', user="dima", passwd="d817", use_pure=True)
# df = pd.read_excel('C:/Users/DQ/Downloads/official2_org_main.xlsx', engine='openpyxl')

dt = {'https://yandex.ru/profile/1001804428': '1421',
'https://yandex.ru/profile/1003554817': '2040',
'https://yandex.ru/profile/1010378977': '1970',
'https://yandex.ru/profile/1029561602': '1915',
'https://yandex.ru/profile/105691711803': '1768',
'https://yandex.ru/profile/1061112740': '1380',
'https://yandex.ru/profile/1080033739': '1970',
'https://yandex.ru/profile/1106044138': '1696',
'https://yandex.ru/profile/1119406213': '1380',
'https://yandex.ru/profile/1166051527': '1746',
'https://yandex.ru/profile/1224814182': '1380',
'https://yandex.ru/profile/1254833856': '2071',
'https://yandex.ru/profile/1298577101': '2072',
'https://yandex.ru/profile/1319356074': '1915',
'https://yandex.ru/profile/1345744023': '1746',
'https://yandex.ru/profile/1365534513': '1548',
'https://yandex.ru/profile/1325472107': '1428',
'https://yandex.ru/profile/1817506751': '1685',
'https://yandex.ru/profile/1684331596': '1768',
'https://yandex.ru/profile/1819726093': '1397',
'https://yandex.ru/profile/1392863858': '1397',
'https://yandex.ru/profile/19940193748': '1746',
'https://yandex.ru/profile/240302143021': '1449',
'https://yandex.ru/profile/54463196659': '1702',
'https://yandex.ru/profile/1333224885': '2068',
'https://yandex.ru/profile/1759585104': '1380',
'https://yandex.ru/profile/1783047232': '1380',
'https://yandex.ru/profile/1742296059': '1702',
'https://yandex.ru/profile/1329856885': '1558',
'https://yandex.ru/profile/1794103243': '1836',
'https://yandex.ru/profile/1770398011': '1380',
'https://yandex.ru/profile/1779944484': '1746',
'https://yandex.ru/profile/204274118081': '1432',
'https://yandex.ru/profile/1762573335': '1380',
'https://yandex.ru/profile/1746131028': '1419',
'https://yandex.ru/profile/1729666209': '1380',
'https://yandex.ru/profile/1804993650': '1380',
'https://yandex.ru/profile/1711882253': '1910',
'https://yandex.ru/profile/149294765360': '1970',
'https://yandex.ru/profile/57349974228': '2063'}


rq = []
# df.columns = ['code', 'name', 'post_index', 'district', 'sub_district', 'city', 'sub_city', \
#               'street', 'h_num1', 'h_num2', 'h_num3']
# df.fillna("", inplace=True)
# for i, row in df.iterrows():
#     if row['idofficial'] != "":
#         rq.append(f"UPDATE `tno_rev`.`org` SET `idofficial` = '{int(row['idofficial'])}' WHERE (`idya_org` = '{row['idya_org']}');")

for i in dt:
    rq.append(
        f"UPDATE `tno_rev`.`org` SET `idofficial` = '{dt[i]}' WHERE (`url` = '{i}');")


cursor = mydb.cursor()
for i in rq:
    cursor.execute(i)
mydb.commit()
cursor.close()

pass