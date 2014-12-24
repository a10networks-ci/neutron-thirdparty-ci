#!/usr/bin/env python

import os
import time

from ax_ssh import AxSSH

import sys
sys.path.append(os.environ['HOME'])

import config

if __name__ == "__main__":
    c = config.devices['ax-lsi']
    ax = AxSSH(c['host'], c['username'], c['password'])
    ax.reboot()
    time.sleep(300)

    c = config.devices['ax-lsi']
    ax = AxSSH(c['host'], c['username'], c['password'])
    print(ax.show_run())
