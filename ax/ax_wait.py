#!/usr/bin/env python

import os
import sys
import time

import acos_client

sys.path.append(os.environ['HOME'])

import config

d = config.devices['ax-lsi']

TIME_TO_WAIT=6 #00
SLEEP_INTERVAL=0.1

start=time.time()
e = 1
while time.time() - start < TIME_TO_WAIT:
    try:
        c = acos_client.Client(d['host'], d['api_version'],
                               d['username'], d['password'],
                               d['port'])
        print(c.system.information())
        e = 0
        break
    except Exception as e:
        print(e)
        time.sleep(SLEEP_INTERVAL)

sys.exit(e)
