# rstsite/rstsite/sitemap.py

import datetime

from django.contrib import sitemaps
from django.urls import reverse

class PagesSitemap(sitemaps.Sitemap):
    protocol = 'https'
    priority = 0.5
    
    def __init__(self, names):
        self.names = names

    def items(self):
        return self.names

    def location(self, obj):
        return reverse('show', args=[obj])
        

class MediaSitemap(sitemaps.Sitemap):
    protocol = 'https'
    priority = 0.5
    
    def __init__(self, names):
        self.names = names

    def items(self):
        return self.names

    def location(self, obj):
        return '/media/{}'.format(obj)