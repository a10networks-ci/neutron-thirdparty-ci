
import subprocess
import tempfile

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

    def config_get(self, acos_commands, verbose=True):
        commands = ['en\r\n',
                    '\r\n',
                    'terminal length 0\r\n']
        commands += acos_commands
        commands += ['exit\r\n',
                     'exit\r\n',
                     'y\r\n']

        print commands if verbose
        lines = self._ssh(commands)
        print lines if verbose
        trim = []
        for line in lines:
            x = line.strip()
            if x == '' or x[0] == '!':
                continue
            trim.append(line)
        return trim

    def config_gets(self, commands, verbose=True):
        return ''.join(self.config_get(commands, verbose))

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

    def license(self, sn, id):
        commands = [
            'config\r\n',
            'license-manager host 54.201.247.34 port 443 use-mgmt-port\r\n',
            "license-manager sn %s\r\n" % sn,
            'license-manager interval 3\r\n',
            "license-manager instance_name openstack-ci-%s\r\n" % id,
            'license-manager bandwidth_unrestricted\r\n',
            'license-manager connect\r\n',
            'write mem\r\n',
            'end\r\n',
        ]
        self.config_gets(commands, verbose=False)

    def partition_list(self):
        commands = [
            'config\r\n',
            'show partition\r\n',
            'end\r\n',
        ]
        z = self.config_get(commands)
        print("Z = %s" % z)
        print("len = %d" % len(z))
        print("split = %s" % map(lambda x: x.split(), z))
        return map(lambda x: x.split()[0], z[7:-2])

    def partition_delete(self, partitions):
        commands = [
            'config\r\n',
        ]
        for p in partitions:
            commands += [
                "no partition %s\r\n" % p,
                'yes\r\n',
            ]
        commands += [
            'write mem\r\n',
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
