# rstsite/rstsite_context.py

from django.conf      import settings


def siteconf(request):
    '''site configuration params availabe to templates'''
    cont = { 
        'ABSTRACT': settings.RSTSITE.get('ABSTRACT', ''),
        'WTITLE':   settings.RSTSITE.get('WTITLE', ''),
        'WSUBTITLE': settings.RSTSITE.get('WSUBTITLE', ''),
        }
    return cont

