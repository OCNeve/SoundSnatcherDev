from os import name as osname
import locale
from Front.Desktop.locales.strings import *


def getString(string_family, key):
    if osname == "nt":
        import ctypes
        windll = ctypes.windll.kernel32
        loc = locale.windows_locale[ windll.GetUserDefaultUILanguage() ]
    else:
        locale.setlocale(locale.LC_ALL, "")
        loc = locale.getlocale(locale.LC_MESSAGES)[0]
        print(loc)
    if not loc:
        return eval(f"{string_family}.English.{key}")

    if 'fr' in loc.lower():
        return eval(f"{string_family}.French.{key}")
    elif 'en' in loc.lower():
        return eval(f"{string_family}.English.{key}")
