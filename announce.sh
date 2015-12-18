#!/bin/bash

#set -x #echo on

DIR="$(dirname "$0")"
ALFRED=/usr/local/sbin/alfred
ANNOUNCE_OPTS=""

(

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
cd $DIR

while test $# -gt 0; do
  case $1 in
    -u)
      shift
      #alfred-json -z -r 158 -s $1 > /dev/null
      #test $? -ne 0 && exit
      ALFREDSOCKET="-u $1"
      ;;
    -h|--help)
      echo "Usage: $0 [-i <ifname>] [-b <batadv-dev>] [-f <fastd-dev>] [-u <alfred-socket>] [-s <site_code>]"
      exit
      ;;
  esac
  shift
done

#./announce.py -d nodeinfo.d/   ${ANNOUNCE_OPTS}  | python -m json.tool
#./announce.py -d statistics.d/ ${ANNOUNCE_OPTS}  | python -m json.tool
./announce.py -d nodeinfo.d/   ${ANNOUNCE_OPTS} | gzip | $ALFRED $ALFREDSOCKET -s 158
./announce.py -d statistics.d/ ${ANNOUNCE_OPTS} | gzip | $ALFRED $ALFREDSOCKET -s 159

)


