#!/usr/bin/python
import requests
import json
import sys
import math

url_mainnet = 'https://rpcapi.fantom.network/'
url_testnet = 'https://rpc.testnet.fantom.network/'
url = ''

cache = {}

def get_block_by_number(block):
  payload = json.dumps({
    'method': 'eth_getBlockByNumber',
    'params': [block, False],
    'id': 1,
    'jsonrpc': '2.0',
    })
  headers = {'Content-Type': 'application/json'}

  response = requests.request('POST', url, headers=headers,
                data=payload)

  try:
    j = json.loads(response.text)
  except:
    raise Exception('Invalid JSON: ', response.text)
  return j

def load_epoch(blk):
  block = hex(blk)
  if block in cache:
    return cache[block]
  j = get_block_by_number(block)
  res = j['result']
  if res == None:
    raise Exception('ERROR block: ', int(block, 16),
            " doesn't exists.")
  r = int(res['epoch'], 16)
  cache[block] = r
  return r

def find_first(epoch, min, max):
  last_low = -1
  last_high = -1

  while True:
    # choosing the bigger block in middle of the interval
    half = math.ceil((max - min) / 2) + min
    e = load_epoch(half)
    if max - min <= 1:
      if epoch != e:
        raise Exception(e, ' != ', epoch)
      if e - 1 != load_epoch(half - 1):
        raise Exception('FIRST internal error')
      return (half, last_low, last_high)
    elif e < epoch:
      min = half
    else:
      # labeling the boundries of last block
      # first time when the epoch is correct then the last block is in between half and max
      if e == epoch and last_low == -1:
        last_low = half
        last_high = max
      max = half


def find_last(epoch, min, max):
  while True:
  # choosing the smaller block in the middle of the interval
    half = math.floor((max - min) / 2) + min
    e = load_epoch(half)
    if max - min <= 1:
      if epoch != e:
        raise Exception(e, ' != ', epoch)
      if e + 1 != load_epoch(half + 1):
        raise Exception('LAST internal error')
      return half
    if e <= epoch:
      min = half
    else:
      max = half

def load_block(epoch):
  j = get_block_by_number('latest')
  max = int(j['result']['number'], 16)
  current_epoch = int(j['result']['epoch'], 16)
  if current_epoch <= epoch:
    raise Exception('ERROR epoch: ', epoch,
            " isn't finished. Lastest finished epoch is: ",
            current_epoch - 1)
  r = find_first(epoch, 1, max)
  l = find_last(epoch, r[1], r[2])
  return [r[0], l]

try:
  # testnet switch
  if sys.argv[2] == 't' or sys.argv[3] == 't':
    url = url_testnet
  else:
    url = url_mainnet
except:
  url = url_mainnet 

if sys.argv[1] == 'b':
  # load epoch from block
  r = load_epoch(int(sys.argv[2], 10))
elif sys.argv[1] == 'e':
  # load block from epoch
  r = load_block(int(sys.argv[2], 10))
elif sys.argv[1] == 'i': 
  # block info
  r = get_block_by_number(hex(int(sys.argv[2], 10)))['result']
elif sys.argv[1] == 'l':
  # last block and epoch
  res = get_block_by_number('latest')['result']
  r = "block: " + str(int(res['number'],16)) + " epoch: " + str(int(res['epoch'],16))
else:
  r = load_block(int(sys.argv[1], 10))
print(r)
