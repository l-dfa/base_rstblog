# rstsite/rstsite_context.py

from django.conf      import settings

from rstblog.models import Article
from rstblog.models import Category
from rstblog.const import TYPES



def siteconf(request):
    '''site configuration params availabe to templates'''
    cont = { 
        'ABSTRACT': settings.RSTSITE.get('ABSTRACT', ''),
        'WTITLE':   settings.RSTSITE.get('WTITLE', ''),
        'WSUBTITLE': settings.RSTSITE.get('WSUBTITLE', ''),
        }
    return cont
    
def used_categories(request):
    '''categories used in every atype
    
    return: a dictionary, keys are atypes, values are 
            lists of used categories in that atype
    '''
    
    used_cats = dict()                    # dict {atype1: [cat1, cat2, ...], ...}
    all_cats = Category.objects.all()
    atypes = list(TYPES.keys())
    
    for atype in atypes:
        cats = []
        for category in all_cats:
            if Article.objects.filter(category=category, atype=atype).count() > 0 :
                cats.append(category.name)
        used_cats[atype] = cats.copy()
    categories = dict()
    categories['categories'] = used_cats.copy()
    
    return categories
    


