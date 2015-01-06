#!/usr/bin/env python

import os

from ax_ssh import AxSSH

import sys
sys.path.append(os.environ['HOME'])

import config


if __name__ == "__main__":
    c = config.devices['ax-lsi']
    ax = AxSSH(c['host'], c['username'], c['password'])
    z = ax.partition_list()
    ax.partition_delete(z)
