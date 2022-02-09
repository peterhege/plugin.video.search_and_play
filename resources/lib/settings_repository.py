import os

import xbmc
import xbmcaddon
import xbmcgui

try:
    from sqlite3 import dbapi2 as database, OperationalError
except:
    from pysqlite2 import dbapi2 as database, OperationalError

dbfile = os.path.join(xbmc.translatePath(xbmcaddon.Addon().getAddonInfo('profile')).decode('utf-8'), 'setting.db')
dbcon = database.connect(dbfile)
dbcur = dbcon.cursor()

cache = {}


def setting(key, value=None):
    if value is not None:
        set_value(key, value)
    return get_value(key)


def get_value(key):
    if key in cache:
        return cache[key]
    value = None
    try:
        dbcur.execute("SELECT settings_value FROM settings WHERE settings_key = '{key}'".format(key=key))
        match = dbcur.fetchone()

        value = match[0] if match else None
    except OperationalError as e:
        create_table()
    cache[key] = value
    return value


def set_value(key, value):
    cache[key] = value
    if get_value(key):
        sql = "UPDATE settings SET settings_value='{value}' WHERE settings_key='{key}'"
    else:
        sql = "INSERT INTO settings (settings_key, settings_value) VALUES ('{key}','{value}')"
    dbcur.execute(sql.format(key=key, value=value))
    dbcon.commit()


def create_table():
    dbcur.execute('CREATE TABLE IF NOT EXISTS settings (settings_key TEXT PRIMARY KEY, settings_value TEXT)')
    dbcon.commit()
