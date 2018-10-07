# rstblog/views.py

import pdb
import xml.etree.ElementTree as ET
from pathlib       import Path

from docutils.core import publish_parts

from django.conf      import settings
from django.contrib   import messages
from django.contrib.auth.decorators import login_required
from django.http      import Http404
from django.http      import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render

from rstblog.views import get_file_content
from rstblog.views import rstcontent2html 
from rstblog.views import upload_file
from rstblog.views import cOu_article_record

try:
    PAGES_DIR = Path(settings.RSTSITE['PAGES_DIR'])
except:
    PAGES_DIR = Path(settings.BASE_DIR) / 'contents/pages'

#@login_required(login_url="/login/")
@login_required()
def load_page(request):
    '''load a reST|markup|html file '''
    
    # load file to MEDIA_ROOT and move it to PAGES_DIR
    # then get fields from file content (docinfo section)
    # and crete/update article record in DB
    if request.method == 'POST':
        if request.FILES['page']:
            try:
                dst = upload_file(request, item_type='page', dirdst=Path(PAGES_DIR))
                #pdb.set_trace()
                page = cOu_article_record(dst, must_be_original='ignore')
                msg = 'page {} loaded'.format( dst.name, )
                messages.add_message(request, messages.INFO, msg)
            except Exception as ex:
                msg = 'error "{}" while trying to load page. action NOT completed'.format(ex)
                messages.add_message(request, messages.ERROR, msg)
        else:
            msg = 'file missing, nothing to upload'
            messages.add_message(request, messages.ERROR, msg)
        return redirect('rstblog:index')
        
    return render( request, 'load_page.html' )

    
def show(request, path=''):
    '''shows a reStructuredText file as html'''

    p = PAGES_DIR / path 
    p = p.with_suffix('.rst')
    #pdb.set_trace()
    try:
        file_content = get_file_content(p)
        content = rstcontent2html(file_content)
    except:
        raise Http404()
    #data = { 'content': parts['html_body'],
    #         'path': path,    }
    data = { 'content': content,
             'path':    path,
             'page_id': f'show {p.name}'}
             
    return render( request, 'show.html', data, )

def index(request):
    ''' list articles '''
    
    return redirect ( 'rstblog:index' )
