# rstsite/mkinitdb.py 

# thanks to https://www.stavros.io/posts/standalone-django-scripts-definitive-guide/

from enum import Enum
import pdb
import os, sys

# CHANGE THIS -  this the project's manage.py directory
proj_path = "/Dati/Studio/Sviluppi/base_rstblog/rstsite"
#proj_path = "/usr/share/nginx/html/ldfa/rstsite"

# CHANGE THIS - This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rstsite.settings")
sys.path.append(proj_path)

# This is so my local_settings.py gets loaded.
os.chdir(proj_path)

# This is so models get loaded.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

################## FROM HERE - your script

from datetime import datetime

import pytz

from django.conf      import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from rstblog.models import Author
from rstblog.models import Category
from rstblog.models import Article


_ENV = '''initial environment

- categories
- authors
- articles

    '''

DT_FORMAT = '%Y-%m-%d %H:%M:%S'  # datetime format year-month-day hour.minute.second

CATEGORIES = [
    {'name': 'information technology', },
    {'name': 'note', },
    {'name': 'opinion', },
    {'name': 'review', },
    {'name': 'science', },
    {'name': 'uncategorized', },
    ]

     
AUTHORS = [
    {'name': 'Luciano De Falco Alfano', },
    {'name': 'Giuseppe Verdi', },
    ]

     
ARTICLES = [
    { 'title': 'Installare una applicazione Django usando Nginx e Gunicorn',
      'file': 'django_deployment.rst',
      'category': 'information technology',
      'authors': ('Luciano De Falco Alfano', 'Giuseppe Verdi', ),
      'summary': ('Non è facile installare una applicazione Django '
                  'in un web server di produzione. '
                  'In questo articolo vedremo i passi necessari per farlo '
                  'in un server CentOs 7, con web server Nginx e middleware '
                  'Gunicorn' ), 
      'slug': 'installare-una-applicazione-django-usando-nginx-e-gunicorn',
      'language': 'it',
      'created': '2018-07-22 12:01:01',
      'modified': '2018-07-22 13:01:01',
      'markup': 'restructuredtext',
      },
    { 'title': 'Installing a Django application using Nginx and Gunicorn',
      'file': 'django_deployment.en.rst',
      'category': 'information technology',
      'authors': ('Luciano De Falco Alfano', 'Giuseppe Verdi', ),
      'summary': ('Installing a Django application in a production '
                  'web server is not easy. '
                  'In this article we will see the necessary steps to made it '
                  'in a CentOs 7 server, with Nginx as web server and '
                  'Gunicorn middleware.' ), 
      'slug': 'Installing-a-Django-application-using-Nginx-and-Gunicorn',
      'language': 'en',
      'created': '2018-07-31 12:01:01',
      'modified': '2018-07-31 13:01:01',
      'translation_of': 'Installare una applicazione Django usando Nginx e Gunicorn',
      'markup': 'restructuredtext',
      },
    { 'title': 'esempio vuoto',
      'file': 'esempio_vuoto.txt',
      'author': 'Luciano De Falco Alfano',
      'summary': 'a very easy summary',
      'slug': 'esempio-vuoti',
      #'language': 'it',
      'created': '2018-07-20 12:01:01',
      'modified': '2018-07-22 13:01:01',
      'markup': 'restructuredtext',
      },
 ]

 
def edit_site():
    '''set site domain and name
    
    luciano.defalcoalfano.it, ldfa's website
    '''
    site = Site.objects.all()[0]
    site.domain = 'luciano.defalcoalfano.it'
    site.name = "ldfa's website"
    site.save()



def add_categories():
    ''' initial categories set '''
    for cd in CATEGORIES:
        c = Category(name=cd.get('name'))
        c.save()


def add_authors():
    ''' initial authors set '''
    for ad in AUTHORS:
        a = Author(name=ad.get('name'))
        a.save()


def add_articles():
    '''starting with one article '''
    
    #pdb.set_trace()
    for ad in ARTICLES:
        c = None
        if ad.get('category'):
            c = Category.objects.get(name=ad.get('category'))
        a = Article( title=ad.get('title'),
            file=ad.get('file'),
            slug=ad.get('slug'),
            summary = ad.get('summary'),
            category=c, )
        a.save()
        if ad.get('markup'):
            a.markup = ad.get('markup')
        if ad.get('language'):
            a.language = ad.get('language')
        if ad.get('created'):
            t = datetime.strptime(ad.get('created'), '%Y-%m-%d %H:%M:%S')
            t = pytz.timezone(settings.TIME_ZONE).localize(t)
            a.created = t
        if ad.get('authors'):
            for auth in ad.get('authors'):
                author = None
                try:
                    author = Author.objects.get(name=auth)
                except:
                    pass
                if author:
                    a.authors.add(author)     # WARN: ManyToMany uses id
        if ad.get('author'):
            author = None
            try:
                author = Author.objects.get(name=ad.get('author'))
            except:
                pass
            if author:
                a.authors.add(author)     # WARN: ManyToMany uses id
        if ad.get('translation_of'):
            original = None
            try:
                original = Article.objects.get(title=ad.get('translation_of'))
            except:
                pass
            if original:
                a.translation_of = original
        a.save()


print("create superuser luciano")
User.objects.create_superuser(username='luciano', password='luciano1234', email='email@address.com')
#User.objects.create_superuser(username='ldfa', password='zJCioxZ2#0', email='ldefalcoalfano@hotmail.com')

print("editing site")
edit_site()

print("adding")

print("    categories")
add_categories()

print("    authors")
add_authors()

print("    articles")
add_articles()


