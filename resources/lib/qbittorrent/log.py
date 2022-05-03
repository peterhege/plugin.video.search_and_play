# -*- coding: utf-8 -*-
from .base import Qbittorrent
from .model import MainLog, PeerLog

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
