# Pi-Hole Monitoring with Grafana #

## Overview ##
This package was built for the sole purpose of making the installation of grafana, telegraf, and influxdb to monitor a Pi-Hole instance as painless as possible. Typically, a user would need lots of setup to on each package in order to correctly monitor Pi-Hole. This package does as much as possible for you. No installing each package, no exposing ports on your machine, and no searching for hours on how to build and copy grafana dashboards. It's all already included here. Just follow the instructions below and enjoy!

## Notes ##
This project was developed on a raspberry pi 4. As such, some of the commands might be different for different OSes. As an example, the telegraf package used is `arm32v7` and may need to be changed.

## Prerequisites ##
- You need a working copy of Pi-Hole with its `pihole-FTL.db` file located at `/etc/pihole/` (i.e. this doesn't work with Pi-Hole Docker containers or special installations).

## Instructions ##
1. Install Docker

  `curl -sSL https://get.docker.com | sh`
2. Add permission to Pi User to run Docker Commands

  `sudo usermod -aG docker pi`
3. Reboot!
4. Test Docker installation

  `docker run hello-world`
5. Install dependencies

  `sudo apt-get install libffi-dev libssl-dev`

  `sudo apt-get install -y python python-pip`

  `sudo apt-get remove python-configparser`

6. Install Docker Compose

  `sudo pip install docker-compose`

7. Start the stack

  `docker-compose up -d`

8. Go to http://host_ip:3000 (where host_ip is the ip of the machine running the stack)

9. Type `admin` for the username and `admin` for the password

10. Set your new password

11. Done!

