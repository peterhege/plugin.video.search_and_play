import time

from .base import Qbittorrent

try:
    from typing import List
except:
    pass


class Log(Qbittorrent):
    BASE_PATH = 'log'
    URLS = {
        'main': '/main',
        'peers': '/peers'
    }

    def main(self, normal=None, info=None, warning=None, critical=None,
             last_known_id=None):  # type: (bool,bool,bool,bool,int) -> List[MainLog]
        """
        Get log

        Parameters:
            normal (bool): Include normal messages (default: true)
            info (bool): Include info messages (default: true)
            warning (bool): Include warning messages (default: true)
            critical (bool): Include critical messages (default: true)
            last_known_id (int): Exclude messages with "message id" <= last_known_id (default: -1)
        """
        path = self._get_path('main')
        params = {k: v for k, v in locals().iteritems() if v is not None and k != 'self'}
        return [MainLog(**row) for row in self._GET(path, params)]

    def peers(self, last_known_id=None):  # type: (int) -> List[PeerLog]
        """
        Get peer log

        Parameters:
            last_known_id (int): Exclude messages with "message id" <= last_known_id (default: -1)
        """
        path = self._get_path('peers')
        params = {k: v for k, v in locals().iteritems() if v is not None and k != 'self'}
        return [PeerLog(**row) for row in self._GET(path, params)]


class MainLog(object):
    """
    https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#get-log
    
    Parameters:
        id (int): ID of the message
        message (str): Text of the message
        timestamp (int): Milliseconds since epoch
        type (int): Type of the message: Log::NORMAL: 1, Log::INFO: 2, Log::WARNING: 4, Log::CRITICAL: 8
    """
    id = None  # type: int
    message = None  # type: str
    timestamp = None  # type: int
    type = None  # type: int
    type_str = None  # type: str

    NORMAL = 1
    INFO = 2
    WARNING = 4
    CRITICAL = 8

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
            if k == 'type':
                self.set_type_str(v)

    def set_type_str(self, t):
        self.type_str = {
            self.NORMAL: 'normal',
            self.INFO: 'info',
            self.WARNING: 'warning',
            self.CRITICAL: 'critical'
        }[t]
        return self

    def __str__(self):
        return '[{type}] [{time}] [{id}] {message}'.format(
            type=str(self.type_str if self.type_str else self.type).upper(),
            time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timestamp / 1000)),
            id=self.id,
            message=self.message.encode('utf-8')
        )


class PeerLog(object):
    """
    https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#get-peer-log

    Parameters:
        id (int): ID of the peer
        ip (str): IP of the peer
        timestamp (int): Milliseconds since epoch
        blocked (bool): Whether or not the peer was blocked
        reason (str): Reason of the block
    """
    id = None  # type: int
    ip = None  # type: str
    timestamp = None  # type: int
    blocked = None  # type: bool
    reason = None  # type: str

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __str__(self):
        return '[{ip}] [{time}] [{id}]{blocked} {reason}'.format(
            ip=self.ip,
            time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timestamp / 1000)),
            id=self.id,
            blocked=' [BLOCKED]' if self.blocked else '',
            reason=self.reason.encode('utf-8')
        )
