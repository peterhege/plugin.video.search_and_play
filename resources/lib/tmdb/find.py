# -*- coding: utf-8 -*-

"""
tmdbsimple.find
~~~~~~~~~~~~~~~
This module implements the Find functionality of tmdbsimple.

Created by Celia Oakley on 2013-10-31.

:copyright: (c) 2013-2022 by Celia Oakley
:license: GPLv3, see LICENSE for more details
"""

from tmdbsimple.base import TMDB


class Trending(TMDB):
    """
    Trending functionality.

    See: https://developers.themoviedb.org/3/trending
    """
    BASE_PATH = 'trending'
    URLS = {
        'info': '/{media_type}/{time_window}',
    }

    def __init__(self, media_type='all', time_window='day'):
        super(Trending, self).__init__()
        self.media_type = media_type
        self.time_window = time_window

    def info(self, **kwargs):
        """
        Get the daily or weekly trending items. The daily trending list tracks
        items over the period of a day while items have a 24 hour half life.
        The weekly list tracks items over a 7 day period, with a 7 day half
        life.

        Valid Media Types
            'all': Include all movies, TV shows and people in the results as a
                   global trending list.
            'movie': Show the trending movies in the results.
            'tv': Show the trending TV shows in the results.
            'people': Show the trending people in the results.

        Valid Time Windows
            'day': View the trending list for the day.
            'week': View the trending list for the week.

        Args:
            None

        Returns:
            A dict respresentation of the JSON returned from the API.
        """
        path = self._get_media_type_time_window_path('info')

        response = self._GET(path, kwargs)
        self._set_attrs_to_values(response)
        return response

    def _get_media_type_time_window_path(self, key):
        return self._get_path(key).format(
            media_type=self.media_type, time_window=self.time_window)
