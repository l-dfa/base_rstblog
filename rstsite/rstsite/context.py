# rstsite/rstsite_context.py

from django.conf      import settings


def siteconf(request):
    '''site configuration params availabe to templates'''
    
    return { 'ABSTRACT': settings.RSTSITE.get('ABSTRACT', ''), }

