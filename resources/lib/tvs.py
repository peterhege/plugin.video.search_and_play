import xbmc
import tmdbsimple as tmdb
import xbmcgui

from resources.lib import library_driver, youtube_driver, netflix_driver, ncore_driver, context_factory


def load_tv(tv_id):
    tv = tmdb.TV(int(tv_id))
    data = tv.info(language=xbmc.getLanguage(xbmc.ISO_639_1))
    videos = tv.videos(language=xbmc.getLanguage(xbmc.ISO_639_1))
    data['videos'] = videos['results'] if 'results' in videos else []
    context_menu = {}
    for driver in [
        library_driver,
        # youtube_driver, netflix_driver, ncore_driver
    ]:
        found = driver.for_tv(data)
        if found:
            context_menu.update(driver.context_tv(found))
    context_factory.show(context_menu, 'tvs.load_tv({tv_id})'.format(tv_id=tv_id), True)
