# -*- coding: utf-8 -*-

class Collection(object):
    list = []  # type: list

    def __init__(self, data_list, callback=None):  # type: (list,callable) -> None
        if callback is not None:
            data_list = [callback(**data) for data in data_list]
        self.list = data_list

    def first(self):
        return self.list[0]

    def last(self):
        return self.list[-1]

    def get(self, i):
        return self.list[i]

    def search(self, callback):
        for data in self.list:
            if callback(data):
                return data
        return None

    def filter(self, callback):
        return filter(callback, self.list)

    def is_empty(self):
        return len(self.list) == 0
