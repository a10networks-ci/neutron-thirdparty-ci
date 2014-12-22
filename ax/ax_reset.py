#!/usr/bin/env python

import subprocess
import tempfile
import time

import config

class AxSSH(object):

    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    def _ssh(self, commands):
        t = tempfile.TemporaryFile()
        ssh = subprocess.Popen(['ssh', "%s@%s" % (self.user, self.host)],
                               close_fds=True,
                               shell=False,
                               stdin=subprocess.PIPE,
                               stdout=t)

        ssh.stdin.writelines(commands)
        ssh.wait()

        t.flush()
        t.seek(0)
        lines = t.readlines()
        t.close()

        return lines[4:-3]

    def config_get(self, acos_commands):
        commands = ['en\r\n',
                    '\r\n',
                    'terminal length 0\r\n']
        commands += acos_commands
        commands += ['exit\r\n',
                     'exit\r\n',
                     'y\r\n']

        print commands
        lines = self._ssh(commands)
        print lines
        trim = []
        for line in lines:
            x = line.strip()
            if x == '' or x[0] == '!':
                continue
            trim.append(line)
        return trim

    def config_gets(self, commands):
        return ''.join(self.config_get(commands))

    def erase(self):
        commands = [
            'config\r\n',
            'erase preserve-management preserve-accounts reload\r\n',
            'y\r\n',
            '\r\n',
            #'web-service server\r\n',
            #'web-service port 8080\r\n',
            #'web-service secure-server\r\n',
            #'web-service secure-port 8443\r\n',
            #'write mem\r\n',
            'end\r\n',
        ]
        self.config_gets(commands)

    def enable_web(self):
        commands = [
            'config\r\n',
            'web-service server\r\n',
            'web-service port 8080\r\n',
            'web-service secure-server\r\n',
            'web-service secure-port 8443\r\n',
            'write mem\r\n',
            'end\r\n',
        ]
        self.config_gets(commands)

    def partition_list(self):
        commands = [
            'config\r\n',
            'show partition\r\n',
            'end\r\n',
        ]
        z = self.config_gets(commands)
        print("Z = %s" % z)
        print("len = %d" % len(z))
        print("split = %s" % map(lambda x: x.split(), z))
        return map(lambda x: x.split()[0], z[7:-2])

    def partition_delete(self, p):
        commands = [
            'config\r\n',
            "no partition %s\r\n" % p,
            'end\r\n',
        ]
        self.config_gets(commands)

    def write_mem(self):
        commands = [
            'config\r\n',
            'write mem\r\n',
            'end\r\n',
        ]
        self.config_gets(commands)

    def reboot(self):
        commands = [
            'reboot\r\n',
            'yes\r\n',
            'yes\r\n'
        ]
        self.config_gets(commands)

    def show_run(self):
        return self.config_gets(['show run\r\n'])


if __name__ == "__main__":
    c = config.devices['ax-lsi']
    ax = AxSSH(c['host'], 'jenkins', 'nopass')
    z = ax.partition_list()
    for p in z:
        ax.partition_delete(p)
    ax.write_mem()
