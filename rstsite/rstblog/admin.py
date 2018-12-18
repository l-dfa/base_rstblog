# rstsite/rstblog/admin.py

from django.contrib import admin


from rstblog.models import Category, CategoryAdmin
from rstblog.models import Author, AuthorAdmin
from rstblog.models import Article, ArticleAdmin


admin.site.register(Category, CategoryAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Article, ArticleAdmin)

