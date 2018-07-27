# rstsite/rstblog/tests.py

# MEMO #ppp func(self)

_ENV = '''tests environment
    ...
'''

# WARNING

# DO NOT test for exception with other tests in the same unit test.
#
# ref: `TransactionManagementError “You can't execute queries until the end
#      of the 'atomic' block” while using signals, but only during Unit Testing
#      <https://stackoverflow.com/questions/21458387/transactionmanagementerror-you-cant-execute-queries-until-the-end-of-the-atom>`_    
#
# ... This is caused by a quirk in how transactions are handled in the newer
# versions of Django coupled with a unittest that intentionally triggers an exception ...
# 
# In Django 1.4, this works fine. However, in Django 1.5/1.6, each test
# is wrapped in a transaction, so if an exception occurs, it breaks the
# transaction until you explicitly roll it back. Therefore, any further
# ORM operations in that transaction, will fail with that
# django.db.transaction.TransactionManagementError exception.
    
import pdb
import pytz
import warnings

from datetime import datetime
from pathlib  import Path

from django.contrib.auth.models import User
from django.test import TestCase

from concurrency.exceptions import RecordModifiedError

from rstblog.models import Article
from rstblog.models import Author
from rstblog.models import Category

from rstblog.views import *

current_date = datetime(2018,1,15,tzinfo=pytz.utc)

author = None
category = None
article = None

def setUpModule():
    '''test environment
    
    global _ENV describes it '''
    
    global author
    global article
    global category
    
    User.objects.create_superuser(username='luciano', password='luciano1234', email='email@address.com')
    
    author = Author( username = 'a.biagi', name = 'Antonio Biagi', )
    author.save()
    
    category = Category( name = 'uncategorized', )
    category.save()
    
    article = Article( title = 'un saggio di a.biagi',
        file='saggio_biagi.txt',
        category = category,
        slug='saggio_biagi', )
    article.save()
    article.authors.add(author)
    

def tearDownModule():
    pass

    
from django.db import transaction


class CategoryModelTest(TestCase):

    def setUp(self):
        ''' setup from setUpModule'''
        pass
        
    def test_category_creation_1(self):
        '''test category model creation missing mandatory field'''
        
        # test mandatory field
        with self.assertRaises(Exception) as raised:
            c = Category(name=None)
            c.save()
        self.assertEqual("NOT NULL constraint failed: rstblog_category.name", str(raised.exception))
        
    def test_category_creation_2(self):
        ''' test category creation '''
        
        c = Category( name='categorized', )
        c.save()               # WARN: save before add ManyToMany rels
        self.assertIsInstance(c, Category)
        
        cs = Category.objects.all()
        self.assertEqual(len(cs), 2)

        
class AuthorModelTest(TestCase):

    def setUp(self):
        ''' setup from setUpModule'''
        
        pass
        
    def test_author_creation_1(self):
        '''test author model creation missing mandatory field'''
        
        # test mandatory field
        with self.assertRaises(Exception) as raised:
            a = Author(name=None)
            a.save()
        self.assertEqual("NOT NULL constraint failed: rstblog_author.name", str(raised.exception))
        
    def test_author_creation_2(self):
        ''' test author creation '''
        
        a = Author( name='autore', )
        a.save()               # WARN: save before add ManyToMany rels
        self.assertIsInstance(a, Author)
        
        a_s = Author.objects.all()
        self.assertEqual(len(a_s), 2)

        
class ArticleModelTest(TestCase):

    def setUp(self):
        ''' setup from setUpModule'''
        
        pass
        
    def test_article_creation_1(self):
        '''test article model creation missing mandatory field'''
        
        # test mandatory field
        with self.assertRaises(Exception) as raised:
            t = Article(title=None, file='file', category=category)
            t.save()
        self.assertEqual("NOT NULL constraint failed: rstblog_article.title", str(raised.exception))
        # cannot insert a 2nd test about raise exception. needs a new method

    def test_article_creation_2(self):
        '''test article model creation missing mandatory field'''
        
        # test mandatory field
        with self.assertRaises(Exception) as raised:
            t = Article(title='titolo', file='file', category=None, slug='titolo')
            t.save()
        self.assertEqual("NOT NULL constraint failed: rstblog_article.category_id", str(raised.exception))
        
    def test_article_creation_3(self):
        '''test article model creation missing mandatory field'''
        
        # test mandatory field
        with self.assertRaises(Exception) as raised:
            t = Article(title='titolo', file=None, category=category, slug='titolo')
            t.save()
        self.assertEqual("NOT NULL constraint failed: rstblog_article.file", str(raised.exception))
        
    def test_article_creation_4(self):
        ''' test category creation '''
        
        a = Article( title='articolo', file='file', category=category, slug='articolo')
        a.save()               # WARN: save before add ManyToMany rels
        self.assertIsInstance(a, Article)
        
        a_s = Article.objects.all()
        self.assertEqual(len(a_s), 2)

    def test_article_concurrency(self):
        ''' test course concurrency by  '''
        #pdb.set_trace()
        with self.assertRaises(Exception) as raised:  # top level exception as we want to figure out its exact type
            a1 = Article.objects.get(title='un saggio di a.biagi')
            a2 = Article.objects.get(title='un saggio di a.biagi')
            
            # chg zip => chg uploaded_at
            a1.summary = 'sommario a1'
            a2.summary = 'sommario a2'
            a1.save()
            a2.save()
        self.assertEqual(RecordModifiedError, type(raised.exception))  # if it fails, we'll get the correct type to import
        
        
#from django.contrib.auth.models import User
from django.urls import reverse
from django.test.client import Client
from django.utils.translation import activate
from django.contrib.auth import authenticate
        
        
class ViewsTest(TestCase):
    '''rstblog views tests'''

    def test_load_article(self):
        '''def load_article(request):'''
        #activate('en')
        c = Client()
        login = c.login(username='luciano', password='luciano1234') 
        self.assertTrue(login)
        
        path = reverse(
            'rstblog:load_article',
            kwargs=dict(),
            )

        p = Path('/Dati/Studio/Sviluppi/base_rstblog/ausiliarie') / 'pippo-3.rst'
        with p.open(mode='rb') as fp:
            response = c.post(path, { 'article': fp}, follow=True, )
        #with open('tmp.html', 'w') as f:
        #    f.write(response.content.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('article pippo-3.rst loaded' in response.content.decode('utf-8'))
        
