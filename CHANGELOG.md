# Pi-Hole Monitoring Changelog

## 2020-07-30

- Environment variables have been added for `PIHOLE_FTL_DB`, `INFLUXDB_HOST`, `INFLUXDB_PORT`. This allows users to send data to other instances of influxdb and capture data for custom instances of pi-hole.

## 2020-07-31

- Environment variable has been added for `PIHOLE_API_URL` to allow users to exchange `http://pi.hole/admin` with the pihole instance's custom IP address.

## 2020-08-01

- Fixed duplicate data points (closes [#16](https://github.com/Brandawg93/Pi-Hole-Monitoring/issues/16))
