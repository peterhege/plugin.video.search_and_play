from .base import Qbittorrent, to_snake_case


class Transfer(Qbittorrent):
    BASE_PATH = 'transfer'
    URLS = {
        'info': '/info',
    }

    def info(self):
        """https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)#get-global-transfer-info"""
        path = self._get_path('info')
        params = {k: v for k, v in locals().iteritems() if v is not None and k != 'self'}
        return Info(**self._GET(path, params))


class Info(object):
    dl_info_speed = None  # type: int
    dl_info_data = None  # type: int
    up_info_speed = None  # type: int
    up_info_data = None  # type: int
    dl_rate_limit = None  # type: int
    up_rate_limit = None  # type: int
    dht_nodes = None  # type: int
    connection_status = None  # type: str

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, to_snake_case(k), v)
