import gettext
import os
import locale

DOMAIN = 'ztmanager'
LOCALEDIR = '/app/share/locale'
if not os.path.exists(LOCALEDIR):
    LOCALEDIR = os.path.join(os.path.dirname(__file__), '..', '..', 'share', 'locale')

try:
    locale.setlocale(locale.LC_ALL, '')
except Exception:
    pass

gettext.bindtextdomain(DOMAIN, LOCALEDIR)
gettext.textdomain(DOMAIN)
_ = gettext.gettext
