#!/usr/bin/env python

import time

from ax_reset import AxSSH
import config

if __name__ == "__main__":
    c = config.devices['ax-lsi']
    ax = AxSSH(c['host'], 'admin', 'nopass')
    ax.reboot()
    time.sleep(300)

    c = config.devices['ax-lsi']
    ax = AxSSH(c['host'], 'admin', 'nopass')
    print(ax.show_run())
