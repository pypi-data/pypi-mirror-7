import socket
import psutil
from datetime import datetime


def get_disks(all_partitions=False):
    disks = [
        (dp, psutil.disk_usage(dp.mountpoint))
        for dp in psutil.disk_partitions(all_partitions)
    ]
    disks.sort(key=lambda d: d[1].total, reverse=True)
    return disks


def get_users():
    users = []
    for u in psutil.users():
        dt = datetime.fromtimestamp(u.started)
        user = {
            'name': u.name.decode('utf-8'),
            'terminal': u.terminal,
            'started': dt.strftime('%Y-%m-%d %H:%M:%S'),
            'host': u.host.decode('utf-8')
        }

        users.append(user)
    return users


def get_process_environ(pid):
    with open('/proc/%d/environ' % pid) as f:
        contents = f.read()
        env_vars = dict(row.split('=', 1) for row in contents.split('\0') if '=' in row)

    return env_vars


def socket_constants(prefix):
    return dict((getattr(socket, n), n) for n in dir(socket) if n.startswith(prefix))


socket_families = socket_constants('AF_')
socket_types = socket_constants('SOCK_')
