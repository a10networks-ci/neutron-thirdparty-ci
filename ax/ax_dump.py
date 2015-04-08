#!/usr/bin/env python

import os

from ax_ssh import AxSSH

import sys
sys.path.append(os.environ['HOME'])

import config


if __name__ == "__main__":
    c = config.devices['ax-lsi']
    ax = AxSSH(c['host'], c['username'], c['password'])

    z = ax.show_run()
    f = open('/opt/stack/logs/ax_show_run.txt', 'w')
    f.write(z)
    f.close()

    parts = ax.partition_list()
    for p in parts:
        z = ax.partition_show_run(p)
        f = open('/opt/stack/logs/ax_show_run_%s.txt' % p, 'w')
        f.write(z)
        f.close()
