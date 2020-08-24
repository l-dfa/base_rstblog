"""rstsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf    import settings
from django.conf.urls.static import static
#from django.conf.urls.i18n   import i18n_patterns
from django.conf.urls        import url
from django.contrib import admin
from django.contrib.auth     import views as auth_views
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps.views import sitemap
from django.urls    import include
from django.urls    import path

from . import views
from .sitemap import IndexSitemap
#from .sitemap import PagesSitemap
from .sitemap import MediaSitemap
from .sitemap import PlainSitemap
from rstblog.models import Article
from rstblog.models import Category

# this to create urls about search articles by categories
#    to pass to IndexSitemap in sitemaps section
search_by_category = []
try:
    categories = Category.objects.values_list('name', flat=True)
    for category in categories:
        search_by_category.append(['rstblog:index_category', category[:], 'article',])
except:
    pass
  


articles_dict = {
    # the next line is valid for articles AND pages
    #    so PageSitemap is no more needed
    'queryset': Article.objects.filter(published=True).exclude(title='banner').order_by('-created'),
    'date_field': 'modified',
}

sitemaps= {
    'blog':  GenericSitemap(articles_dict, protocol='https', priority=0.5),
    'indexes': IndexSitemap(['rstblog:index',
                             'rstblog:show_stats',
                             ['rstblog:index_all_categories', 'article',],
                             *search_by_category,
                             ]),
    #'pages': PagesSitemap(['author.rst',
    #                       'formazione.rst',]),
    'media': MediaSitemap(['pdfs/CV_luciano_de_falco_alfano-public.pdf',
                           'pdfs/ds-sinossi.pdf',
                           'pdfs/cios_cmds.pdf',
                           'pdfs/cios_cmds_study.pdf',
                           'pdfs/common_criteria/cc-p1.pdf',
                          ]),
    'plain': PlainSitemap(['robots.txt',
                           'sitemap.xml',
                           
                           'general-algebra/index.html',
                           'general-algebra/genindex.html',
                           'general-algebra/1-operazioni_tra_insiemi.html',
                           'general-algebra/2.0-algebra_di_boole.html',
                           
                           'csd-appunti/index.html',
                           'csd-appunti/01_regular_expressions.html',
                           'csd-appunti/03_bisimulation.html',
                           'csd-appunti/04_ccs.html',
                           'csd-appunti/05_pc.html',
                           'csd-appunti/06_fifo.html',
                           'csd-appunti/07_pipe.html',
                           'csd-appunti/08_buff.html',
                           'csd-appunti/09_model_checking.html',
                           'csd-appunti/95_cwbnc.html',
                           'csd-appunti/96_cwb.html',
                           'csd-appunti/97_base_concepts.html',
                           'csd-appunti/98_references.html',
                           'csd-appunti/genindex.html',
                           
                           'ds-appunti/index.html',
                           'ds-appunti/01_definizione.html',
                           'ds-appunti/02_categorie.html',
                           'ds-appunti/03_architetture.html',
                           'ds-appunti/04_esempi_di_domande.html',
                           'ds-appunti/05_processi.html',
                           'ds-appunti/06_client_server.html',
                           'ds-appunti/07_rpc.html',
                           'ds-appunti/08_naming.html',
                           'ds-appunti/09_sincronizzazione.html',
                           'ds-appunti/11_sincronizzazione-2.html',
                           'ds-appunti/12_consistenza.html',
                           'ds-appunti/13_consistenza-2.html',
                           'ds-appunti/14_paxos.html',
                           'ds-appunti/15_bizantini.html',
                           'ds-appunti/97_osservazioni.html',
                           'ds-appunti/98_riferimenti.html',
                           
                           'nf-appunti/index.html',
                           'nf-appunti/01_explore.html',
                           'nf-appunti/02_configure.html',
                           'nf-appunti/03_protocols.html',
                           'nf-appunti/04_access.html',
                           'nf-appunti/P2_01_routing.html',
                           'nf-appunti/P2_02_static_routing.html',
                           'nf-appunti/P2_03_dynamic_routing.html',
                           'nf-appunti/P2_04_switched_networks.html',
                           'nf-appunti/P2_05_switch_config.html',
                           'nf-appunti/P2_06_vlan.html',
                           'nf-appunti/P2_07_acl.html',
                           'nf-appunti/P2_08_dhcp.html',
                           'nf-appunti/P2_09_nat.html',
                           'nf-appunti/P2_10_discovery.html',
                           'nf-appunti/98_terminology.html',
                           'nf-appunti/99_references.html',

                           'itsf-appunti/index.html',
                           'itsf-appunti/01_introduzione.html',
                           'itsf-appunti/02_crittografia_convenzionale',
                           'itsf-appunti/03_crittografia_moderna',
                           'itsf-appunti/04_confidenzialita',

                           ]),
    
}


urlpatterns = [
    path('blog/', include('rstblog.urls', namespace='rstblog')),
    path('load-page', views.load_page, name='load_page'),
    path('show/<path:path>', views.show, name='show'),
    path('sitemap.xml',
        sitemap,
        {'sitemaps': sitemaps, },
        name='django.contrib.sitemaps.views.sitemap', ),
    path('', views.index, name='index'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    #path('login/', auth_views.login, {'template_name': 'login.html',}, name='login'), #-chg ldfa @2018-11-27
    #path('logout/', auth_views.logout, {'next_page': '/login'}, name='logout'), #-chg ldfa @2018-11-27
    path('login/', auth_views.LoginView.as_view(), name='login'),                #+chg ldfa @2018-11-27
    path('logout/', auth_views.LogoutView, {'next_page': settings.LOGIN_REDIRECT_URL}, name='logout'),  #+chg ldfa @2018-11-27
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    

