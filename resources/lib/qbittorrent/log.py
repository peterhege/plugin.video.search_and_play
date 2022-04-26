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

    def main_log(self, normal=None, info=None, warning=None, critical=None,
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

    def peers(self):
        pass


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

    NORMAL = 1
    INFO = 2
    WARNING = 4
    CRITICAL = 8

    def __init__(
            self,
            id=None,  # type: int
            message=None,  # type: str
            timestamp=None,  # type: int
            type=None,  # type: int
            **kwargs
    ):
        for k, v in locals().iteritems():
            if k != 'self':
                setattr(self, k, v)
