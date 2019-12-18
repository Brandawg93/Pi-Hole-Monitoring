from sqlite3 import connect
from datetime import datetime
import sys
import time
import json
import requests

row = None
last_id = None
query = "SELECT * FROM queries WHERE id = (SELECT MAX(id) FROM queries)"
url = "http://influxdb:8086/write?db=pihole-FTL"

while True:
	try:
		data = {'q': 'CREATE DATABASE "pihole-FTL"'}
		requests.post("http://influxdb:8086/query", data=data)
		break
	except requests.exceptions.ConnectionError:
		print('Could not connect. Retrying...')
		time.sleep(5)
	except KeyboardInterrupt:
		sys.exit(0)

while True:
	try:
		con = connect('/etc/pihole/pihole-FTL.db')
		with con:
			if last_id:
				query = "SELECT * FROM queries WHERE id > {}".format(last_id)
			cur = con.cursor()
			cur.execute(query)

			if row:
				last_id = row[0]
			rows = cur.fetchall()

			if len(rows) > 0:
				row = rows[-1]
				id = row[0]

			if row and id != last_id:
				for item in rows:
					data = 'pihole-FTL,domain="{}",client="{}" id={},timestamp={},type={},status={},domain="{}",client="{}",forward="{}"'.format(item[4], item[5], item[0], item[1], item[2], item[3], item[4], item[5], item[6])
					r = requests.post(url, data=data)
			else:
				time.sleep(5)
	except KeyboardInterrupt:
		break
