# -*- coding: utf-8 -*-

import time


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
