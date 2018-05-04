from django.shortcuts import render, HttpResponse, HttpResponseRedirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger # for paginator
from django.core.urlresolvers import reverse, reverse_lazy # can get URL for redirect from namespace

from django.contrib.auth.decorators import login_required # nice decorator for restricting access

from django.contrib.auth.admin import Group # allows access to a user's group

from datetime import datetime as dt
from django.views import generic # pretty much not using this method for objects, but required

from . import models

def set_cookie(response, key, value, days_expire = 7):
    # sets a cookie
    # set_cookie(response, 'mykeyname', 'mykeyvalue', days_expire=1)
    # request.COOKIES.get('mykeyname') 
    
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  #one year
    else:
        max_age = days_expire * 24 * 60 * 60 
    expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=max_age), "%a, %d-%b-%Y %H:%M:%S GMT")
    response.set_cookie(key, value, max_age=max_age, expires=expires, domain=settings.SESSION_COOKIE_DOMAIN, secure=settings.SESSION_COOKIE_SECURE or None)

def demo(request):
    return render(request, 'classify/demo.html', {})

def index(request):
    return render(request, 'classify/main.html', {})

# ############################################
# GENERIC VIEWS
class ImageListView(generic.ListView):
    model = models.Image
    
class ImageDetailView(generic.DetailView):
    model = models.Image
    
class ImageCreateView(generic.CreateView):
    model = models.Image
    
class SiteListView(generic.ListView):
    model = models.Site

class SiteDetailView(generic.DetailView):
    model = models.Site
    
    def get_context_data(self, **kwargs):
        context = super(SiteDetailView, self).get_context_data(**kwargs)
        # additional context items go here
        return context
    
class SiteCreateView(generic.CreateView):
    model = models.Site
    
class SiteDeleteView(generic.DeleteView):
    model = models.Site

class ObservationListView(generic.ListView):
    model = models.Observation
    
class ObservationDetailView(generic.DetailView):
    model = models.Observation
    
    def get_context_data(self, **kwargs):
        # adding extra context to the observation view
        # Call the base implementation first to get a context
        context = super(ObservationDetailView, self).get_context_data(**kwargs)
        # can_edit is based on the request.user being the same person that made the original observation
        context['can_edit'] = self.object.person == self.request.user
        return context    
    
# ############################################
# NON GENERIC VIEWS ARE BELOW IN THE CODE    

def all_images(request):
    image_list = models.Image.objects.all()
    paginator = Paginator(image_list, 25) # Show 25 images per page
    
    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        images = paginator.page(paginator.num_pages)
    return render(request, 'classify/image_list_pagination.html', {'images': images})
    
def site_images(request,pk):
    # show all the images associated with the site identified by pk (primary key)
    site = get_object_or_404(models.Site, pk=pk)
    images = models.Image.objects.filter(site=site)
    context = {'site':site, 'images':images}
    return render(request,'classify/site_images.html', context)

def image_observations(request, pk):
    image = get_object_or_404(models.Image, pk=pk)
    observations = models.Observation.objects.filter(image=image)
    context = {'image': image, 'observations': observations}
    return render(request, 'classify/image_observations.html', context)

def handle_todo_navigation(request,image, done=False):
    # handle todo items in request user's list
    # image is the location of where we are in the current list.
    todo = models.ToDo.objects.filter(user=request.user)
    if todo:
        for idx in range(0,todo.count()):
            if todo[idx].image == image:
                break
        _curr = todo[idx].image.id
        if done:
            # mark that it is done
            todo[idx].done = True
            todo[idx].save()
        
        if idx > 0:
            _prev = todo[idx-1].image.id
        else:
            _prev = todo[0].image.id
        if idx < todo.count()-1:
            _next = todo[idx+1].image.id
        else:
            _next = todo[idx].image.id
            
        request.session['current_todo'] = _curr
        request.session['prev_todo'] = _prev
        request.session['next_todo'] = _next
    return todo

@login_required
def observation_post(request, image=None, observation=None):
    # handle observation post request
    # if called with image, this is a NEW observation
    if request.method != "POST":
        return HttpResponse("critical WTF -- Illegal method 'GET'")
    
    
    if image:
        # fill in a new observation instance
        observation = models.Observation()
        observation.image = image
        observation.person = models.User.objects.get(username=request.user.username)
        observation.site = image.site
        observation.date_str = dt.now().strftime('%Y-%m-%d %H:%M')
    elif observation:
        # this is good call, go past it
        pass
    else:
        return HttpResponse("critical WTF -- how did this get called without image or observation data?")
    
    # now grab the form data
    observation.species = request.POST.get('species','')
    observation.count = request.POST.get('count','')
    observation.females = request.POST.get('females','')
    observation.males = request.POST.get('males','')
    observation.young = request.POST.get('young','')
    observation.unknown = request.POST.get('unknown','')
    
    observation.save()
    
    todo = handle_todo_navigation(request, image, done=True)
    
    # handle PREV or NEXT button scenario
    next_image_id = None
    if 'next' in request.POST:
        next_image_id = request.session.get('next_todo', None)
        
    if 'prev' in request.POST:
        next_image_id = request.session.get('prev_todo', None)
    
    if next_image_id:
        # prev/next returned an id, so service it!
        return HttpResponseRedirect(reverse('classify:image_observation_form', kwargs={'pk':next_image_id}))
        
    return HttpResponseRedirect(reverse('classify:observation_detail_view', kwargs={'pk':observation.id}))
        
@login_required
def observation_edit(request, pk):
    observation = get_object_or_404(models.Observation, pk=pk)
    groups = Group.objects.filter(user=request.user)
    
    can_edit = False
    if observation.person == request.user or 'leader' in groups:
        can_edit = True    
    
    if request.method == 'POST':
        # now grab the form data
        observation.species = request.POST.get('species','')
        observation.count = request.POST.get('count','')
        observation.females = request.POST.get('females','')
        observation.males = request.POST.get('males','')
        observation.young = request.POST.get('young','')
        observation.unknown = request.POST.get('unknown','')
        # save the data
        observation.save()        
        # go back to observation view
        return HttpResponseRedirect(reverse('classify:observation_detail_view', kwargs={'pk':observation.id}))
        
    context = {'object':observation, 'can_edit':can_edit}
    return render(request, 'classify/observation_form.html', context=context)

@login_required    
def image_observation_form(request, pk):
    # make a new observation based on an image pk (primary key)
    image = get_object_or_404(models.Image, pk=pk) # get image from pk
    observation = models.Observation() # new observation instance, fill in image and 
    observation.image = image
    observation.user = models.User.objects.get(username=request.user.username)
    
    if request.method == 'POST':
        return observation_post(request, image=image)
    
    todo = handle_todo_navigation(request, image)
    context = {'object': observation, 'todo': todo}
    return render(request, 'classify/observation_form.html', context)

@login_required
def observation_form(request, pk):
    # this form is for a NEW observation associated with the image and request user
    observation = get_object_or_404(models.Observation, pk=pk)
    if request.method == 'POST':
        return observation_post(request, observation=observation)
    
    context = {'object':observation }
    return render(request, 'classify/observation_form.html', context)

def searchbox(request):
    '''searchbox(request) - responds to a put method including specific data'''
    if request.method != 'POST':
        # only POST requests are processed
        return HttpResponse(status=405)
    search_phrase = request.POST.get('search_phrase','')
    if 'unclass' in search_phrase.lower():
        # search for unclassified images
        images = models.unclassified_images()
        context ={'object_list': images, 'title':'Unclassified Images'}
        return render(request, 'classify/image_list.html', context)
    if 'site=' in search_phrase.lower():
        term_list = search_phrase.split('=')
        for term in term_list:
            term = term.strip().upper()
            if term != 'SITE':
                site = models.Site.objects.filter(name=term).first()
                if site:
                    return HttpResponseRedirect(reverse('classify:site_images', kwargs={'pk':site.id}))
        
    return HttpResponse('No results found for search term "{}"'.format(search_phrase))

def todo_list_create(username, count, site_name, checkboxes):

    user = models.User.objects.filter(username=username).first()
    if not(user):
        # set message no user and return
        return None
    
    count = int(count)
    
    if site_name:
        site = models.Site.objects.filter(name=site_name).first()
    else:
        site = None
        
    # find images to classify
    if 'r' in checkboxes:
        select = 'random'
    else:
        select = ''
        
    if 'u' in checkboxes:
        # only unclassified images
        images = models.pick_images(count, images=models.unclassified_images(site=site), checkboxes=checkboxes)
    else:
        # any images
        images = models.pick_images(count, site=site, checkboxes=checkboxes)
    
    # assign to the user, making sure they are not all ready in their list
    # obsolete logic, the pick_images function now looks at the checkboxes
    #todo_count = 0
    #for image in images:
        #match_todo = models.ToDo.objects.filter(image=image)
        #if not(match_todo):
            #this_todo = models.ToDo(user=user, image=image)
            #this_todo.save()
            #todo_count += 1
            
    for image in images:
        this_todo = models.ToDo(user=user, image=image)
        this_todo.save()
        
    return len(images)

@login_required
def todo_create(request):
    if request.method == 'POST':
        if 'cancel' in request.POST:
            # return to top level
            return HttpResponseRedirect(reverse('classify:index'))
        
        # handle form data
        username = request.POST.get('username','').strip()
        count = request.POST.get('count_input','').strip()
        siteid = request.POST.get('site_input','').strip()
        checkboxes = request.POST.get('checkbox1','') + request.POST.get('checkbox2','').strip() + request.POST.get('checkbox3','').strip()
        # interpret site ID, slightly awkward
        if siteid == '0':
            site_name = ''
        elif siteid == '23':
            site_name = 'WF1'
        elif siteid == '24':
            site_name = 'WF2'
        else:
            site_name = 'PM' + siteid
            
        if not(username):
            # if username was not specified, assume current user request todo list for themselves
            username = request.user.username
            
        tasks = todo_list_create(username=username, count=count, site_name=site_name, checkboxes=checkboxes)
        # messages.info('{} todo items added to list')
        
        if tasks:
            return HttpResponseRedirect(reverse('classify:todo_list', kwargs={'username':username}))
    
    usernames = list(models.User.objects.values_list('username', flat=True))
    context = {'usernames':usernames}
    return render(request, 'classify/todo_list_form.html', context)

@login_required
def todo_clear(request,username=None):
    if not(username):
        # clear your own list
        username = request.user.username
        
    user = models.User.objects.get(username=username)
    todo_items = models.ToDo.objects.filter(user=user)
    todo_items.delete()
    
    return HttpResponseRedirect(reverse('classify:index'))

@login_required
def todo_list(request, username=None):
    # todo list position is maintained by cookie
    if username:
        user = models.User.objects.filter(username=username).first()
    else:
        user = request.user
        username = request.user.username
        
    
    todo_list = models.ToDo.objects.filter(user=user)

    todo_current = request.COOKIES.get('todo_current')
    
    context = {'username':username, 'todo_list':todo_list}
    return render(request, 'classify/todo_list.html', context=context)

def get_todo_cookies(request):
    todo_prev = request.COOKIES.get('todo_prev')
    todo_current = request.COOKIES.get('todo_current')
    todo_next = request.COOKIES.get('todo_next')
    return todo_prev, todo_current, todo_next

def set_todo_cookies(response, todo_prev, todo_current, todo_next):
    set_cookie(response, 'todo_prev', str(todo_prev), 1)
    set_cookie(response, 'todo_current', str(todo_current), 1)
    set_cookie(response, 'todo_next', str(todo_next), 1)    
    
def todo_detail(request, pk):
    html = ''
    todo_prev, todo_current, todo_next = get_todo_cookies(request)
        
    response = HttpResponse('todo detail')
    set_todo_cookies(1,pk,3)
    return response
