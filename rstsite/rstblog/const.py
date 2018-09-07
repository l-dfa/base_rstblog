# rstblog/const.py

from pathlib       import Path

from django.conf      import settings

try:
    ARTICLES_DIR = Path(settings.RSTBLOG['ARTICLES_DIR'])
except:
    ARTICLES_DIR = Path(settings.BASE_DIR) / 'contents/articles'

try:
    PAGES_DIR = Path(settings.RSTSITE['PAGES_DIR'])
except:
    PAGES_DIR = Path(settings.BASE_DIR) / 'contents/pages'

try:
    START_CONTENT_SIGNAL = settings.RSTBLOG['START_CONTENT_SIGNAL']
except:
    START_CONTENT_SIGNAL = '.. hic sunt leones'
    
try:
    LANGUAGES = settings.RSTBLOG['languages']
except:
    LANGUAGES = { 'en': 'english',
                  'it': 'italian', }

try:
    TYPES = settings.RSTBLOG['types']
except:
    LANGUAGES = { 'article': 'article',
                  'page':    'page', }

class SUFFIX(object):
    reST = '.rst'
    markdown = '.md'
    html = '.html'
    text = '.txt'
