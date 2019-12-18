from sqlite3 import connect
from influxdb import InfluxDBClient
import sys
import time
import json
import requests

row = None
last_id = None
query = "SELECT * FROM queries WHERE id = (SELECT MAX(id) FROM queries)"
client = InfluxDBClient(host='influxdb', port=8086, database='pihole-FTL')

while True:
	try:
		client.create_database('pihole-FTL')
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
					json_body = [
						{
							"measurement": "pihole-FTL",
							"tags": {
								"type": item[2],
								"status": item[3],
								"domain": item[4],
								"client": item[5],
								"forward": item[6]
							},
							"time": time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(item[1])),
							"fields": {
								"id": item[0]
							}
						}
					]
					client.write_points(json_body)
			else:
				time.sleep(5)
	except KeyboardInterrupt:
		break
