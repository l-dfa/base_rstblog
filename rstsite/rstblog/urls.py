# rstblog/urls.py

from django.urls import include
from django.urls import path

from . import views


app_name = 'rstblog'

# https://hostname/rst/show/path ...

urlpatterns = [
    path('', views.index, name='index'),
    path('load-article', views.load_article, name='load_article'),
    path('reset-article-table', views.reset_article_table, name='reset_article_table'),
    path('show/<slug>', views.show, name='show'),
]