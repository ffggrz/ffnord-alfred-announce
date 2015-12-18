#!/usr/bin/env python3

import json
import argparse
import codecs
import os
import socket
import subprocess
import re
import netifaces as netif
from cpuinfo import cpuinfo

# Force encoding to UTF-8
import locale                                  # Ensures that subsequent open()s
locale.getpreferredencoding = lambda _=None: 'UTF-8'  # are UTF-8 encoded.

import sys
#sys.stdin = open('/dev/stdin', 'r')
#sys.stdout = open('/dev/stdout', 'w')
#sys.stderr = open('/dev/stderr', 'w')

# Utility functions for the announce.d files
def toUTF8(line):
  return line.decode("utf-8")

def call(cmdnargs):
  output = subprocess.check_output(cmdnargs)
  lines = output.splitlines()
  lines = [toUTF8(line) for line in lines]
  return lines

# Local used functions
def setValue(node,path,value):
  ''' Sets a value inside a complex data dictionary.
      The path Array must have at least one element.
  '''
  key = path[0]
  if len(path) == 1:
    node[key] = value;
  elif key in node:
    setValue(node[key],path[1:],value)
  else:
    node[path[0]] = {}
    setValue(node[key],path[1:],value)

def gateway(batadv_dev):
  output = subprocess.check_output(["batctl","-m",batadv_dev,"gwl","-n"])
  output_utf8 = output.decode("utf-8")
  lines = output_utf8.splitlines()
  gw = None

  for line in lines:
    gw_line = re.match(r"^=> +([0-9a-f:]+) ", line)
    if gw_line:
      gw = gw_line.group(1)

  return gw

def clients(batadv_dev):
  output = subprocess.check_output(["batctl","-m",batadv_dev,"tl","-n"])
  output_utf8 = output.decode("utf-8")
  lines = output_utf8.splitlines()

  count = 0

  for line in lines:
    client_line = re.match(r"^\s\*\s[0-9a-f:]+\s+-\d\s\[[W\.]+\]", line)
    if client_line:
      count += 1

  return count
 
def addresses(bridge_dev):
  ip_addrs = netif.ifaddresses(bridge_dev)
  ip_list = []

  try:
    for ip6 in netif.ifaddresses(bridge_dev)[netif.AF_INET6]:
      raw6 = ip6['addr'].split('%')
      ip_list.append(raw6[0])
  except:
    pass

  return ip_list

def mac_mesh(fastd_dev,meshmode=False):
  interface = netif.ifaddresses(fastd_dev)
  mesh = []
  mac = None

  try:
    mac = interface[netif.AF_LINK]
    mesh.append(mac[0]['addr'])
  except:
    KeyError

  if meshmode:
    return mesh
  else:
    return mac[0]['addr']

def mesh_interfaces(batadv_dev):
  output = subprocess.check_output(["batctl","-m",batadv_dev,"if"])
  output_utf8 = output.decode("utf-8")
  lines = output_utf8.splitlines()
  mesh = []

  for line in lines:
    dev_line = re.match(r"^(\w*)", line)
    interface = netif.ifaddresses(dev_line.group(0))
    mac = interface[netif.AF_LINK]
    mesh.append(mac[0]['addr'])

  return mesh

def bat0_mesh(batadv_dev):
  output = subprocess.check_output(["batctl","-m",batadv_dev,"if"])
  output_utf8 = output.decode("utf-8")
  lines = output_utf8.splitlines()
  mesh = {"tunnel" : []}

  for line in lines:
    dev_line = re.match(r"^(\w*)", line)
    interface = netif.ifaddresses(dev_line.group(0))
    mac = interface[netif.AF_LINK]
    mesh["tunnel"].append(mac[0]['addr'])

  return mesh

def node_id(dev):
  if 'node_id' in config:
    return config['node_id']
  else:
    return mac_mesh(dev).replace(':','')

def hostname():
  if 'hostname' in config:
    return config['hostname']
  else:
    return socket.gethostname()

def cpu_info():
  info = cpuinfo.get_cpu_info()
  return info['brand']

parser = argparse.ArgumentParser()

parser.add_argument('-d', '--directory', action='store',
                  help='structure directory',required=True)

#parser.add_argument('-c', '--cfg', action='store',
#                  help='config file',required=True)

args = parser.parse_args()

options = vars(args)

try:
  with open("config.json", 'r') as cfg_handle:
    config = json.load(cfg_handle)
except IOError:
  raise

batadv_dev = config['network']['batman']
fastd_dev =  config['network']['fastd']
bridge_dev = config['network']['bridge']

data = {}

for dirname, dirnames, filenames in os.walk(options['directory']):
  for filename in filenames:
    if filename[0] != '.':
      relPath = os.path.relpath(dirname + os.sep + filename,options['directory']);
      fh = open(dirname + os.sep + filename,'r', errors='replace')
      source = fh.read()
      fh.close()
      value = eval(source)
      setValue(data,relPath.rsplit(os.sep),value)
#print(json.dumps(data, sort_keys=True, indent=4))
print(json.dumps(data))

