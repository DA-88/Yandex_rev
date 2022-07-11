import mysql.connector as connection
import pandas as pd
import datetime

mydb = connection.connect(host="localhost", database='tno_rev', user="dima", passwd="d817", use_pure=True)
query = "SELECT \
        org.url AS `url`,\
        org.org_name AS `org_name`,\
        org.org_address AS `org_address`,\
        tno_rev.official.code AS `tno_code`, \
        org.org_rate AS `org_rate`,\
        org.org_num_rate AS `org_num_rate`,\
        org.org_num_rev AS `org_num_rev`,\
        org.updated AS `updated`,\
        reviews.rev_date AS `rev_date`,\
        reviews.add_date AS `add_date`,\
        reviews.rating AS `rating`,\
        reviews.rev_text AS `rev_text`,\
        reviews.deleted AS `deleted` \
    FROM \
        org \
    RIGHT JOIN reviews ON org.url = reviews.url \
    LEFT JOIN tno_rev.official \
    ON tno_rev.org.idofficial = tno_rev.official.idofficial \
    WHERE org.deleted = 0 and reviews.rev_date >= '2022-06-01'"

df = pd.read_sql(query, mydb)
mydb.close()  # close the connection

df.to_excel(f"reviews/ya_{datetime.datetime.today().strftime('%d-%m-%Y')}.xls", engine='openpyxl')

a = 1


