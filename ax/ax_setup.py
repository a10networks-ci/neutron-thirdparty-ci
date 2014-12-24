#!/usr/bin/env python

import os

from ax_ssh import AxSSH

import sys
sys.path.append(os.environ['HOME'])

import config


if __name__ == "__main__":
    c = config.devices['ax-lsi']
    ax = AxSSH(c['host'], c['username'], c['password'])

    sn = open("%s/.license_sn" % os.environ['HOME']).read().strip()
    id = open("%s/.a10-instance-id" % os.environ['HOME']).read().strip()
    ax.license(sn, id)
