#!/usr/bin/env python

import subprocess
import tempfile

import config

class AxSSH(object):

    def __init__(self, host, user, password):
        self.host = host
        self.user = user
        self.password = password

    def _ssh(self, commands):
        t = tempfile.TemporaryFile()
        ssh = subprocess.Popen(['sshpass', '-p', self.password,
                                'ssh', "%s@%s" % (self.user, self.host)],
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

        lines = self._ssh(commands)
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
            'erase preserve-management preserve-accounts\r\n',
            'y\r\n',
        ]
        self.config_gets(commands)

    def show_run(self):
        return self.config_gets(['show run\r\n'])


c = config.devices['ax-lsi']
ax = AxSSH(c['host'], c['username'], c['password'])
ax.erase()
print ax.show_run()
