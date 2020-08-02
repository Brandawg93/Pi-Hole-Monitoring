from sqlite3 import connect
from influxdb import InfluxDBClient
from os import environ
import sys
import time
import requests

PIHOLE_FTL_DB = environ['PIHOLE_FTL_DB']
INFLUXDB_HOST = environ['INFLUXDB_HOST']
INFLUXDB_PORT = environ['INFLUXDB_PORT']

client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, database='pihole-FTL')
types = ['A (IPv4)', 'AAAA (IPv6)', 'ANY', 'SRV', 'SOA', 'PTR', 'TXT','','','','','','UNKN']
statuses = ['Unknown', 'blocklist', 'localhost', 'cache', 'blocklist', 'blocklist', 'blocklist', 'blocklist',
            'blocklist', 'blocklist', 'blocklist', 'blocklist']


def wait_for_connection():
    """wait for a connection from the influxdb"""
    while True:
        try:
            client.create_database('pihole-FTL')
            break
        except requests.exceptions.ConnectionError:
            print('Could not connect. Retrying...')
            time.sleep(5)
        except KeyboardInterrupt:
            sys.exit(0)


def get_last_id():
    """fill existing data from pihole-FTL.db"""
    rs = list(client.query('SELECT last(id) FROM "pihole-FTL";').get_points())
    last_id = 0
    if len(rs) > 0:
        last_id = rs[0]['last']
    return last_id


def add_new_results(last_id):
    """write new results from pihole-FTL.db"""
    row = None
    print('filling data...')
    while True:
        try:
            con = connect(PIHOLE_FTL_DB)
            with con:
                query = "SELECT * FROM queries WHERE id > {} ORDER BY id DESC LIMIT 10000".format(last_id)
                cur = con.cursor()
                cur.execute(query)

                if row:
                    last_id = row[0]
                rows = cur.fetchall()

                if len(rows) > 0:
                    row = rows[0]
                    curr_id = row[0]

                if row and curr_id != last_id:
                    for item in rows:
                        json_body = [
                            {
                                "measurement": "pihole-FTL",
                                "tags": {
                                    "uniq": item[0],
                                    "type": types[item[2] - 1],
                                    "status": statuses[item[3]],
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


if __name__ == "__main__":
    wait_for_connection()
    last = get_last_id()
    add_new_results(last)
