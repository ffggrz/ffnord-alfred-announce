#!/bin/bash

#set -x #echo on


DIR="$(dirname "$0")"
ALFRED=/usr/local/sbin/alfred
ANNOUNCE_OPTS=""

while test $# -gt 0; do
  case $1 in
    -c)
      shift
      ANNOUNCE_OPTS+=" --cfg $1"
      ;;
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

"${DIR}"/announce.py -d "${DIR}"/nodeinfo.d/   ${ANNOUNCE_OPTS}  | python -m json.tool
"${DIR}"/announce.py -d "${DIR}"/statistics.d/ ${ANNOUNCE_OPTS}  | python -m json.tool

"${DIR}"/announce.py -d "${DIR}"/nodeinfo.d/   ${ANNOUNCE_OPTS} | gzip | $ALFRED $ALFREDSOCKET -s 158
"${DIR}"/announce.py -d "${DIR}"/statistics.d/ ${ANNOUNCE_OPTS} | gzip | $ALFRED $ALFREDSOCKET -s 159

