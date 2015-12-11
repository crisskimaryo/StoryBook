from django.template.loader import get_template
from django.template import Context
from django.template import RequestContext
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from forms import PageForm
from stories.models import Page, Properties, Book
from django.http import HttpResponseRedirect
from helpers import findPage, findProperties, findUser, goHome, go404
from django.core.exceptions import ObjectDoesNotExist
get_object_or_404


import vimeo

import config


def Vimeo_Upload(video):
    v = vimeo.VimeoClient(
        token=config.TOKEN,
        key=config.CLIENT_ID,
        secret=config.CLIENT_SECRET
    )
    about_me = v.get('/me')
    assert about_me.status_code == 200
    video_uri = v.upload(video.file)
    video_uri = (video_uri.split('s')[0] + video_uri.split('s')[1])
    return video_uri


def home(request, pk):
    book = Book.objects.all().filter(pk=pk)
    rootpages = Page.objects.all().filter(parent=None).filter(book=book)
    return render_to_response("home.html", {'rootpages': rootpages, 'pk': pk}, context_instance=RequestContext(request))

def page(request, pageid):
    page = findPage(pageid)
    if not page:
        return go404()
    page_is_users = not request.user.is_anonymous() and page.author == findUser(request.user)
    nextpages = Page.objects.all().filter(parent=page)
    book = page.book_id
    nextpage1 = None
    nextpage2 = None
    nextpage1_short = None
    nextpage2_short = None
    if len(nextpages)>0:
        nextpage1 = nextpages[0]
        nextpage1_short = nextpage1.short_desc
        if len(nextpage1_short) > 12:
            nextpage1_short = nextpage1_short[:12] + "..."
    if len(nextpages)>1:
        nextpage2 = nextpages[1]
        nextpage2_short = nextpage2.short_desc
        if len(nextpage2_short) > 12:
            nextpage2_short = nextpage2_short[:12] + "..."
    context = {
        'page': page,
        'book': book,
        'page_is_users': page_is_users,
        'nextpage1': nextpage1, 
        'nextpage1_short': nextpage1_short,
        'nextpage2': nextpage2,
        'nextpage2_short': nextpage2_short,
        }
    return render_to_response("page.html", context, context_instance=RequestContext(request))
 
def profile(request):
    if request.user.is_authenticated():
        properties = findProperties(request.user)
        context = {
        'properties': properties,
        } 
        return render_to_response("profile.html", context, context_instance=RequestContext(request))

def editpage(request, pageid):
    page = findPage(pageid)
    if not page:
        return go404()
    if request.user.is_staff or page.author == findUser(request.user):
        already_written = {'short_desc': page.short_desc, 'long_desc': page.long_desc, 'book': page.book}
        files = {'illustration': page.illustration}
        form = PageForm(already_written, files)
        return render_to_response("editingapage.html", {'form': form, 'page': page}, context_instance=RequestContext(request))
    return goHome()

def submiteditedpage(request, pageid):
    if request.user.is_authenticated() and request.method == "POST":
        page = findPage(pageid)
        if not page:
            return go404()
        if request.user.is_staff or page.author == findUser(request.user):
            if request.FILES:
                files = request.FILES
            elif page.illustration:
                files = {'illustration': page.illustration}
            else:
                files = {}
            form = PageForm(request.POST, files)
            if form.is_valid():
                page.short_desc = form.cleaned_data['short_desc']
                page.illustration = files.get('illustration')
                page.long_desc = form.cleaned_data['long_desc']
                if request.FILES.get('video'): 
                    page.video = 'https://player.vimeo.com' + (
                    Vimeo_Upload(request.FILES.get('video'))
                )
                page.save()
                return HttpResponseRedirect("/page:"+str(page.id)+"/") 
            else:
                return render_to_response("editingapage.html", {'form': form, 'page': page}, context_instance=RequestContext(request))
    return goHome()

def writenextpage(request, parentid, *args, **kwargs):
    book = request.path.split('/')[-2]
    if request.user.is_authenticated():
        if (not parentid and user.is_staff()) or parentid:
            form = PageForm
            return render_to_response("writinganewpage.html", {'form': form, 'parentid': parentid, 'book': book}, context_instance=RequestContext(request))
    return goHome()

def submitnewpage(request, parentid, book):
    if request.user.is_authenticated() and request.method == "POST":
        if (not parentid and user.is_staff()) or parentid:    
            form = PageForm(request.POST, request.FILES)
            if form.is_valid():
                page = Page()
                if int(parentid):
                    page.parent = Page.objects.all().get(id=parentid)
                else:
                    page.parent = None
                page.author = request.user
                page.short_desc = form.cleaned_data['short_desc']
                if request.FILES.get('video'): 
                    page.video = 'https://player.vimeo.com' + (
                    Vimeo_Upload(request.FILES.get('video'))
                )
                if request.FILES.get('illustration'):
                    page.illustration = request.FILES.get('illustration')
                    page.video = None
                page.long_desc = form.cleaned_data['long_desc']            
                page.book = get_object_or_404(Book,pk=int(book))
                page.save()
                return HttpResponseRedirect("/page:"+str(page.id)+"/")
            else:
                return render_to_response("writinganewpage.html", {'form': form, 'parentid': parentid, "book": book}, context_instance=RequestContext(request))
    return goHome() 

def deletebranch(request, pageid):
    if request.user.is_staff:
        page = findPage(pageid)
        if page.parent:
            parentpage = page.parent
            page.kill_branch()
            return HttpResponseRedirect("/page:"+str(parentpage.id)+"/")
        else:
            page.kill_branch()
            return HttpResponseRedirect("/")
    return goHome()

def viewtree(request, pageid):
    page = findPage(pageid)
    if not page:
        return go404()
    rootpage = page.get_root()
    array = rootpage.tree_to_array()
        
    context = {
        'rootpage': rootpage,
        'array': array,
        'page': page,
        'current_page_id': page.id,
    }
    return render_to_response("storytree.html", context, context_instance=RequestContext(request))


def page404(request):
    return render_to_response("404page.html", context_instance=RequestContext(request))
