import xbmc
import tmdbsimple as tmdb

from resources.lib import library_driver, youtube_driver, netflix_driver, ncore_driver, context_factory


def load_movie(movie_id):
    movie = tmdb.Movies(int(movie_id))
    data = movie.info(language=xbmc.getLanguage(xbmc.ISO_639_1))
    videos = movie.videos(language=xbmc.getLanguage(xbmc.ISO_639_1))
    data['videos'] = videos['results'] if 'results' in videos else []
    context_menu = {}
    for driver in [library_driver, youtube_driver, netflix_driver, ncore_driver]:
        found = driver.for_movie(data)
        if found:
            context_menu.update(driver.context(found))
    context_factory.show(context_menu, 'movies.load_movie({movie_id})'.format(movie_id=movie_id), True)
