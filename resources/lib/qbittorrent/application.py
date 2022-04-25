# -*- coding: utf-8 -*-
import json

from .base import Qbittorrent


class Application(Qbittorrent):
    BASE_PATH = 'app'
    URLS = {
        'version': '/version',
        'webapiVersion': '/webapiVersion',
        'buildInfo': '/buildInfo',
        'shutdown': '/shutdown',
        'preferences': '/preferences',
        'setPreferences': '/setPreferences',
        'defaultSavePath': '/defaultSavePath'
    }

    def version(self):  # type: () -> str
        """
        Get application version

        Args:

        Returns:
            The response is a string with the application version, e.g. v4.1.3
        """
        path = self._get_path('version')
        return self._GET(path, None, {})

    def webapi_version(self):  # type: () -> str
        """
        Get API version

        Args:

        Returns:
            The response is a string with the WebAPI version, e.g. 2.0
        """
        path = self._get_path('webapiVersion')
        return self._GET(path, None, {})

    def build_info(self):  # type: () -> dict
        """
        Get build info

        Args:

        Returns:
            A dict e.g. {"libtorrent": "1.2.14.0", "qt": "5.15.2", "zlib": "1.2.11", "openssl": "1.1.1l", "bitness": 64, "boost": "1.76.0"}
        """
        path = self._get_path('buildInfo')
        return self._GET(path, None)

    def preferences(self, **kwargs):
        if not kwargs:
            return self.get_preferences()
        return self.set_preferences(**kwargs)

    def get_preferences(self):
        """
        Get application preferences

        Args:

        Returns:
            The response is a JSON object with several fields (key-value) pairs representing the application's settings.
            The contents may vary depending on which settings are present in qBittorrent.ini.
        """
        path = self._get_path('preferences')
        return self._GET(path, None)

    def set_preferences(self, **kwargs):  # type: (...) -> None
        """
        Set application preferences

        Args:
            locale: Currently selected language (e.g. en_GB for English)
            max_active_torrents: Maximum number of active simultaneous downloads and uploads
        Returns:
            The response is a JSON object with several fields (key-value) pairs representing the application's settings.
            The contents may vary depending on which settings are present in qBittorrent.ini.
        """
        path = self._get_path('setPreferences')
        return self._GET(path, {'json': json.dumps(kwargs)})

    def default_save_path(self):  # type: () -> str
        """
        Get default save path

        Args:

        Returns:
            The response is a string with the default save path, e.g. C:/Users/Dayman/Downloads.
        """
        path = self._get_path('defaultSavePath')
        return self._GET(path, None, {})
