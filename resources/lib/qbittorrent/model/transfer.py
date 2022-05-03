# -*- coding: utf-8 -*-

from ..functions import to_snake_case


class TransferInfo(object):
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
