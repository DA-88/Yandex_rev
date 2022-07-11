import mysql.connector as connection
import pandas as pd
import numpy as np
import datetime

mydb = connection.connect(host="localhost", database='tno_rev', user="dima", passwd="d817", use_pure=True)
df = pd.read_excel('C:/Users/DQ/Downloads/data.xlsx', engine='openpyxl')


rq = []
df.columns = ['code', 'name', 'post_index', 'district', 'sub_district', 'city', 'sub_city', \
              'street', 'h_num1', 'h_num2', 'h_num3']
df.fillna("", inplace=True)
for i, row in df.iterrows():
    row['code']=str(row['code'])
    while len(row['code']) < 4:
        row['code'] = f"0{row['code']}"
    # for ik, k in enumerate(row):
    #     v = row[ik]
    #     if np.isnan(v): row[ik] = ''
    rq.append(f"INSERT INTO tno_rev.official (`code`, `name`, `post_index`, `district`, `sub_district`, `city`, \
              `sub_city`, `street`, `h_num1`, `h_num2`, `h_num3`) VALUES \
              ('{row['code']}', '{row['name']}', '{row['post_index']}', '{row['district']}', '{row['sub_district']}', \
              '{row['city']}', '{row['sub_city']}', '{row['street']}', '{row['h_num1']}', '{row['h_num2']}', \
              '{row['h_num3']}')")

cursor = mydb.cursor()
for i in rq:
    cursor.execute(i)
mydb.commit()
cursor.close()

pass