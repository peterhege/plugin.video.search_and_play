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
        if not self.version_satisfying('2.3.0'):
            raise Exception('Min version 2.3.0')
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

        for k in kwargs.keys():
            if k in [
                'create_subfolder_enabled', 'start_paused_enabled', 'auto_delete_mode', 'preallocate_all',
                'incomplete_files_ext', 'auto_tmm_enabled', 'torrent_changed_tmm_enabled',
                'save_path_changed_tmm_enabled', 'category_changed_tmm_enabled', 'mail_notification_sender',
                'limit_lan_peers', 'slow_torrent_dl_rate_threshold', 'slow_torrent_ul_rate_threshold',
                'slow_torrent_inactive_timer', 'alternative_webui_enabled', 'alternative_webui_path'
            ] and not self.version_satisfying('2.2.0'):
                raise Exception('Min version 2.2.0')
            if k in [
                'piece_extent_affinity', 'web_ui_secure_cookie_enabled', 'web_ui_max_auth_fail_count',
                'web_ui_ban_duration', 'stop_tracker_timeout'
            ] and not self.version_satisfying('2.4.1'):
                raise Exception('Min version 2.4.1')
            if k in ['enable_super_seeding'] and not self.version_satisfying('2.5.0'):
                raise Exception('Min version 2.5.0')

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
