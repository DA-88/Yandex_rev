import mysql.connector as connection
import requests
import json

mydb = connection.connect(host="localhost", database='tno_rev', user="dima", passwd="d817", use_pure=True)
cursor = mydb.cursor()
cursor.execute("Select * from tno_rev.official")
myresult = cursor.fetchall()
cursor.close()

for k in myresult:
    addr_text = k[3]
    for i in range(4, 12): addr_text =f"{addr_text}, {k[i]}"
    addr_text = addr_text.replace(" ", "+")
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey=eb189787-a246-440b-bb61-4bb3d9b60dfe&geocode={addr_text}&format=json"
    res = requests.get(url)
    if res.status_code == 200:
        try:
            r = json.loads(res.text)
            cor = r['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split(" ")

            cursor = mydb.cursor()
            rq = f"UPDATE tno_rev.official SET latitude = '{cor[0]}', longitude = '{cor[1]}' WHERE (idofficial = '{k[0]}')"
            cursor.execute(rq)
            mydb.commit()
            cursor.close()


        except:
            pass
        print(addr_text)

pass