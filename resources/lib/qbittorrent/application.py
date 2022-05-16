# -*- coding: utf-8 -*-
import json

from .base import Qbittorrent
from .model import BuildInfo, Preferences

CACHE = {}


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

        Returns:
            The response is a string with the application version, e.g. v4.1.3
        """
        if 'version' not in CACHE:
            path = self._get_path('version')
            CACHE['version'] = self._GET(path, None, {})
        return CACHE['version']

    def webapi_version(self):  # type: () -> str
        """
        Get API version

        Returns:
            The response is a string with the WebAPI version, e.g. 2.0
        """
        if 'webapi_version' not in CACHE:
            path = self._get_path('webapiVersion')
            CACHE['webapi_version'] = self._GET(path, None, {})
        return CACHE['webapi_version']

    def build_info(self):  # type: () -> BuildInfo
        """
        Get build info
        """
        if 'build_info' not in CACHE:
            path = self._get_path('buildInfo')
            CACHE['build_info'] = BuildInfo(**self._GET(path, None))
        return CACHE['build_info']

    def preferences(self, preferences=None):  # type: (Preferences) -> Preferences
        if not preferences:
            return self.get_preferences()
        return self.set_preferences(preferences)

    def get_preferences(self):  # type: () -> Preferences
        """
        Get application preferences

        Returns:
            The response is a JSON object with several fields (key-value) pairs representing the application's settings.
            The contents may vary depending on which settings are present in qBittorrent.ini.
        """
        path = self._get_path('preferences')
        return Preferences(**self._GET(path, None))

    def set_preferences(self, preferences):  # type: (Preferences) -> Preferences
        """
        Set application preferences
        """
        path = self._get_path('setPreferences')
        kwargs = {k: v for k, v in preferences.__dict__.items() if v is not None}
        params = {'json': json.dumps(kwargs)}
        self._GET(path, params)
        return self.get_preferences()

    def default_save_path(self):  # type: () -> str
        """
        Get default save path

        Returns:
            The response is a string with the default save path, e.g. C:/Users/Dayman/Downloads.
        """
        path = self._get_path('defaultSavePath')
        return self._GET(path, None, {})
