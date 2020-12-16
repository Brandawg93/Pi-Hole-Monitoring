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
types = [
    'A (IPv4)',
    'AAAA (IPv6)',
    'ANY',
    'SRV',
    'SOA',
    'PTR',
    'TXT',
    'NAPTR',
    'MX',
    'DS',
    'RRSIG',
    'DNSKEY',
    'OTHER',
]
statuses = [
    'Unknown',
    'blocklist',  # Gravity Database
    'localhost',
    'cache',
    'blocklist',  # Regex Blacklist
    'blocklist',  # Exact Blacklist
    'blocklist',  # Upstream Server
    'blocklist',  # Upstream Server
    'blocklist',  # Upstream Server
    'blocklist',  # Deep CNAME Gravity Database
    'blocklist',  # Deep CNAME regex blacklist
    'blocklist',  # Deep CNAME exact blacklist
    'retired',  # https://github.com/pi-hole/FTL/pull/901
    'retired_dnssec',  # https://github.com/pi-hole/FTL/pull/901
]


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
                        try:
                            status_type = statuses[item[3]]
                        except IndexError:
                            # If this message appears, consult https://docs.pi-hole.net/database/ftl
                            print(f"Invalid Status Type: {item[3]}")
                            continue
                        try:
                            query_type = types[item[2] - 1]
                        except IndexError:
                            # If this message appears, consult https://docs.pi-hole.net/database/ftl
                            print(f"Invalid Query Type: {item[2] - 1}")
                            continue
                        json_body = [
                            {
                                "measurement": "pihole-FTL",
                                "tags": {
                                    "uniq": item[0] % 1000,
                                    "type": query_type,
                                    "status": status_type,
                                    "domain": item[4],
                                    "client": item[5],
                                    "forward": item[6]
                                },
                                "time": time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(item[1])),
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
