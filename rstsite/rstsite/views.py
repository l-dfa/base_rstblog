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

from rstblog.views import rstcontent2html 
from rstblog.views import upload_file

try:
    PAGES_DIR = Path(settings.RSTSITE['PAGES_DIR'])
except:
    PAGES_DIR = Path(settings.BASE_DIR) / 'contents/pages'

@login_required(login_url="/login/")
def load_page(request):
    '''load a reST file '''
    
    # load file to MEDIA_ROOT and move it to PAGES_DIR
    # then nothing else to do
    if request.method == 'POST':
        if request.FILES['page']:
            dst = upload_file(request, item_type='page', dirdst=Path(PAGES_DIR))
            msg = 'page {} loaded'.format( dst.name, )
            messages.add_message(request, messages.INFO, msg)
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
        content = rstcontent2html(p)
    except:
        raise Http404()
    #data = { 'content': parts['html_body'],
    #         'path': path,    }
    data = { 'content': content,
             'path':    path,    }
             
    return render( request, 'show.html', data, )

def index(request):
    ''' list articles '''
    
    return redirect ( 'rstblog:index' )
