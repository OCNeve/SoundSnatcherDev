import ctypes
import locale
from Front.Desktop.locales.strings import *


def getString(string_family, key):
    windll = ctypes.windll.kernel32
    loc = locale.windows_locale[ windll.GetUserDefaultUILanguage() ]
    if 'fr' in loc.lower():
        return eval(f"{string_family}.French.{key}")
    elif 'en' in loc.lower():
        return eval(f"{string_family}.English.{key}")
