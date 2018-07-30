# rstblog/views.py

import os
import pdb
import pytz
import re
import xml.etree.ElementTree as ET
from datetime      import datetime
from pathlib       import Path

from docutils.core import publish_parts
from docutils.core import publish_doctree

from django.conf      import settings
from django.contrib   import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http      import Http404
from django.http      import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import LoadArticleForm
from .models import Article
from .models import Author
from .models import Category


# memo
#    load_article(request) #125
#    index(request)        #176
#    show(request, slug)   #161


try:
    ARTICLES_DIR = Path(settings.RSTBLOG['ARTICLES_DIR'])
except:
    ARTICLES_DIR = Path(settings.BASE_DIR) / 'contents/articles'

try:
    START_CONTENT_SIGNAL = settings.RSTBLOG['START_CONTENT_SIGNAL']
except:
    START_CONTENT_SIGNAL = '.. hic sunt leones'
    
class SUFFIX:
    reST = '.rst'
    markdown = '.md'
    html = '.html'
    text = '.txt'
    

def separate(grand_content):
    ''' return input slitted in two sections, based on the signal START_CONTENT_SIGNAL
    
    parameters:
        - gran_content          str, all the file contents as string
    
    return: a (attributes, content, ) tuple of strings
    
    note. tpical START_CONTENT_SIGNAL is '.. hic sunt leones' string '''
    
    result = None
    #pattern = f"(?P<attributes>.*)^{START_CONTENT_SIGNAL}$(?P<content>.*)"
    #m = re.search(pattern, grand_content, flags=re.M+re.S)
    #if m:
    #    result =  (m.group('attributes'), m.group('content'), )
    #return result
    ndx = grand_content.find(START_CONTENT_SIGNAL)
    if ndx != -1:
        attributes = grand_content[:ndx]
        content = grand_content[ndx+len(START_CONTENT_SIGNAL):]
        result = (attributes, content, )
    
    return result

def get_file_content(p):
    '''get file content as str
    
    parameters:
        - p         Path, of opening file
        
    return: a string
            ValueError if p isn't a file
            
    note: open file in binary mode '''
    
    
    content = None
    if p.is_file():
        # Note mode='rb'. Binary mode necessary to handle accented characters
        with p.open(mode='rb') as f:
            content = f.read()
    else:
        raise ValueError("File {} does not exist".format(path))
    return content
  
  
def upload_file(request, item_type='article', dirdst=Path(ARTICLES_DIR)):
    '''upload file to articles or pages directory
    
    parameters:
        - request     django request
        - type        str, could be article or page
        - dirdst      Path, destination directory (ARTICLES_DIR or PAGE_DIR)
    
    return: destination file as Path
            could raise exception    '''
    
    dst = None
    if request.method == 'POST' and request.FILES[item_type]:
        # loads file to MEDIA_ROOT using FileSystemStorage (could change filename)
        # then moves file from MEDIA_ROOT to ARTICLES_DIR (or PAGES_DIR)
        # eventually adjusting filename to the original value
        try:
            rfile = request.FILES[item_type]
            fs = FileSystemStorage()
            filename = fs.save(rfile.name, rfile)
            src = Path(settings.MEDIA_ROOT) / filename
            dst = dirdst / rfile.name
            os.replace(src, dst)
        except Exception as ex:
            raise
        finally:
            # if something was wrong and uploaded file is there yet
            # remove it
            if src.is_file():
                os.remove(src)
    else:
        raise ValueError('bad http method (must be POST) or without file to upload')
    return dst

    
def get_record(dst):
    '''get fields infos from file
    
    params:
        - dst         Path, of file to elaborate
    
    returns: a (record, autors, ) tuple, with:
        - record      dict, of file attributes
        - authors     tuple, with a SINGLE author
        
    note. get attributes and content splitting file by START_CONTENT_SIGNAL.
        if START_CONTENT_SIGNAL there isn't, create an empty dictionary
        and populate it with default values
    '''
    
    file_content = get_file_content(dst)
    result = separate(file_content.decode('utf-8'))
    if result:
        attributes, content = result
        record = docinfos(attributes)
    else:
        record = dict()
    record['file'] = dst.name
    # get title
    if not record.get('title'):
        record['title'] = dst.name
    #get category
    c = None
    if not record.get('category'):
        record['category'] = 'uncategorized'
    try:
        c = Category.objects.get(name=record.get('category'))
    except:
        c = Category.objects.get(name='uncategorized')
    record['category'] = c
    # get (SINGLE) author
    if record.get('translation_of'):
        original = None
        try:
            original = Article.objects.get(title=record.get('translation_of'))
        except:
            raise ValueError(f'article {record["title"]} is a translation of a non existent article: {record.get("translation_of")}')
        record['translation_of'] = original
    a = None
    authors = tuple()
    if record.get('author'):
        try:
            a = Author.objects.get(name=record.get('author'))
            authors = (a, )
        except:
            pass
        finally:
            del record['author']
    return (record, authors, )


@login_required(login_url="/login/")
def reset_article_table(request):
    '''clear and rebuild article table'''
    
    #pdb.set_trace()
    Article.objects.all().delete()
    paths = flatten(ARTICLES_DIR)
    #articles = [str(p.relative_to(ARTICLES_DIR)) for p in paths]
    count = 0
    for p in paths:
        try:
            # read article fields
            record, authors = get_record(p)
            article, created = Article.objects.update_or_create(
                    file=p.name, defaults=record)
            for a in authors:
                article.authors.add(a)
            article.save()
            count += 1
        except Exception as ex:
            msg = 'error "{}" building record for {} article. action NOT completed'.format(ex, p.name, )
            messages.add_message(request, messages.ERROR, msg)
    msg = 'loaded {} articles in DB'.format( count, )
    messages.add_message(request, messages.INFO, msg)
    return redirect('rstblog:index')

    
@login_required(login_url="/login/")
def load_article(request):
    '''load a reST file and add/chg relative record '''
    
    # load file to MEDIA_ROOT and move it to ARTICLES_DIR
    # then get fields from file content (docinfo section)
    # and crete/update article record in DB
    if request.method == 'POST':
        if request.FILES['article']:
            try:
                dst = upload_file(request, item_type='article', dirdst = Path(ARTICLES_DIR))
                # read article fields
                record, authors = get_record(dst)
                #  if the Article already exists, its fields are updated
                article, created = Article.objects.update_or_create(
                        file=dst.name, defaults=record)
                for a in authors:
                    article.authors.add(a)
                article.save()
                msg = 'article {} loaded'.format( dst.name, )
                messages.add_message(request, messages.INFO, msg)
            except Exception as ex:
                msg = 'error "{}" while trying to load article. action NOT completed'.format(ex)
                messages.add_message(request, messages.ERROR, msg)
        else:
            msg = 'file missing, nothing to upload'
            messages.add_message(request, messages.ERROR, msg)
        return redirect('rstblog:index')
        
    return render( request, 'load_article.html' )


def show(request, slug=''):
    '''shows a reStructuredText file as html'''
    #pdb.set_trace()
    article = get_object_or_404(Article, slug=slug)
    
    try:
        p = ARTICLES_DIR / article.file
        #p = p.with_suffix('.rst')
        #content = rstcontent2html(p)
        #pdb.set_trace()
        #scontent = get_content(p)
        #infos = docinfos(scontent)
        file_content = get_file_content(p)
        result = separate(file_content.decode('utf-8'))
        if result:
            content = result[1][:]
        else:
            content = file_content[:]
        if ( article.markup == 'restructuredtext'
             or p.suffix == SUFFIX.reST ):
            content = rstcontent2html(content)
        elif ( article.markup == 'html'
             or p.suffix == SUFFIX.html ):
            pass
        else:
            raise ValueError(f'{article.markup} is a markup language not supported yet')
             
    except:
        raise Http404()
    
    # increments article counter, if fails probably due to concurrent writes:
    #    ignores it
    try:
        article.hit += 1
        article.save()
    except:
        pass

    data = { 'content': content, 
             'infos': article,    }
             
    return render( request, 'show.html', data, )


def index(request):
    ''' list articles '''
    
    articles = Article.objects.filter(translation_of__isnull=True).order_by('-created')
    data = { 'articles': articles, }
    
    return render( request, 'index.html', data )

    
def rstcontent2html(content):
    '''convert rst file content to html
    
    parameters:
        - content        str, to file to convert
        
    return: a string,
            rise ValueError if p isn't file
    '''

    extra_settings = {
        'initial_header_level': 3,
        'doctitle_xform' : 0,
        'syntax_highlight': 'short', }  # Possible values: 'long', 'short', 'none' 
    #pdb.set_trace()
    parts = publish_parts(content, writer_name='html', settings_overrides=extra_settings, )
    # in a previous version was parts['html_body']; but this includes docinfo section
    return parts['body'][:]

def rstcontent2html_0(p):
    '''convert rst file content to html
    
    parameters:
        - p        path, to file to convert
        
    return: a string,
            rise ValueError if p isn't file
    '''
    if p.is_file():
        # Note mode='rb'. Binary mode necessary to handle accented characters
        with p.open(mode='rb') as f:
            content = f.read()
    else:
        raise ValueError("File {} does not exist".format(path))

    extra_settings = {
        'initial_header_level': 3,
        'doctitle_xform' : 0,
        'syntax_highlight': 'short', }  # Possible values: 'long', 'short', 'none' 
    #pdb.set_trace()
    parts = publish_parts(content, writer_name='html', settings_overrides=extra_settings, )
    # in a previous version was parts['html_body']; but this includes docinfo section
    return parts['body'][:]
    
# this is from http://code.activestate.com/recipes/578948-flattening-an-arbitrarily-nested-list-in-python/
#   changing argument from list to pathlib Path directory
def flatten(path):
    '''Given a directory, possibly nested to any level, return it flattened'''
    new_lis = []
    for item in path.iterdir():
        if item.is_dir():
            new_lis.extend(flatten(item))
        else:
            new_lis.append(item)
    return new_lis

    
def docinfos(content):
    '''get docinfo fields from content
    
    params:
        - content    str, reST document
    
    return: a dict with field names as keys and field bodies as values '''
            
    #pdb.set_trace()
    
    infos = dict()
    field_names = []
    field_bodies = []
    
    tree = publish_doctree(content)
    stree = str(tree)
    # INVESTIGATE. about next 4 lines: is there a better method to handle these
    #    characteristics of xml?
    stree = stree.replace('<document source="<string>">', '<document source="string">')
    stree = stree.replace('&', '&amp;')
    stree = stree.replace('["', '[&quot;')
    stree = stree.replace('"]', '&quot;]')

    etree = ET.fromstring(stree) # line 1 col 18 errore
    field_names = etree.findall("./docinfo/field/field_name")
    field_bodies = etree.findall("./docinfo/field/field_body/paragraph")
    authors = etree.findall("./docinfo/author")
    
    if ( len(field_names) > 0 
       and len(field_bodies) > 0
       and len(field_names) == len(field_bodies) ):
        names = [n.text.lower() for n in field_names]
        bodies = [b.text for b in field_bodies]
        # again: a SINGLE author
        if authors:
            names.append('author')
            bodies.append(authors[0].text)
        for name, body in zip(names, bodies):
            # BEWARE: created and modified are date&time fields
            if name == 'created' or name == 'modified':
                body = norm_dt(body)
                # check https://stackoverflow.com/questions/466345/converting-string-into-datetime
                body = datetime.strptime(body, '%Y-%m-%d %H:%M:%S')
                # how use pytz? pytz.timezone(settings.TIME_ZONE)
                #pdb.set_trace()
                body = pytz.timezone(settings.TIME_ZONE).localize(body)
            if type(body) == str:
                body = body.replace('\n', ' ')
            infos[name] = body
    
    return infos

    
def norm_dt(s):
    '''normalize a datetime as string
    
    params:
        - s         str, as %Y-%m-%d %H:%M:%S, maybe without %H:%M:%S

    return: string %Y-%m-%d %H:%M:%S if input has %H:%M:%S
            otherwise appends 12:00:00 to %Y-%m-%d '''
    
    ret = ''
    # yyyy-mm-dd hh:mm:ss ndx:0123-56-89 12-45-78
    if len(s) >= 10 and len(s) < 19:
        ret = s[:10] + ' 12:00:00'
    elif len(s) == 19:
        ret = s[:]
    else:
        raise ValueError('{} is not acceptable as date/time'.format(s))
    return ret
    
##### OLD GLORIES

# original version: use file name (path in arguments)
def show_1(request, path=''):
    '''shows a reStructuredText file as html'''

    p = ARTICLES_DIR / path 
    p = p.with_suffix('.rst')
    
    try:
        content = rstcontent2html(p)
    except:
        raise Http404()
    #data = { 'content': parts['html_body'],
    #         'path': path,    }
    data = { 'content': content,
             'path': path,    }
             
    return render( request, 'show.html', data, )

    
# this is the 1st version of index: file based
def index_1(request):
    ''' list articles '''
    
    paths = flatten(ARTICLES_DIR)
    articles = [str(p.relative_to(ARTICLES_DIR)) for p in paths]
    #pdb.set_trace()
    
    data = {
        'articles': articles,
    }
    return render( request, 'index.html', data )
    