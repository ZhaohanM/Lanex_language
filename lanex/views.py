from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse
from lanex.models import Language, LanguageRequest, UserProfile
from lanex.forms import LanguageForm, RequestForm, UserForm, UserProfileForm, CommentForm, LanguageRequestForm, UserFormAdditional
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

'''
Takes in a request and renders the index page.
The intention of conditional statements is to check if a user has registered recently.
If this is the case, the user is redirected to the settings page where they will be
  prompted to input name details and a profile picture.
'''
def index(request):
    if request.user.is_authenticated:
        present_timezone = timezone.now()
        user_join_date = request.user.date_joined
        if present_timezone - user_join_date < timedelta(seconds=10):
            return redirect(reverse('lanex:user_settings', 
                                    kwargs={'user_profile_slug': request.user}))

    language_list = Language.objects.all()[:5]
    request_list = LanguageRequest.objects.order_by('-views')[:5]
    context_dict = {}
    context_dict['languages'] = language_list
    context_dict['requests'] = request_list
    print(context_dict)
    return render(request, 'lanex/index.html', context=context_dict)


'''
Takes in a request and renders the about page.
'''
def about(request):
    context_dict = {}
    return render(request, 'lanex/about.html', context=context_dict)


'''
Takes in a request and renders the explore page.
'''
def explore(request):
    language_list = Language.objects.all()[:5]
    request_list = LanguageRequest.objects.order_by('-views')[:5]
    context_dict = {}
    context_dict['languages'] = language_list
    context_dict['requests'] = request_list
    return render(request, 'lanex/explore.html', context=context_dict)


'''
Takes a request and renders the languages page for the language categories.
'''
def languages(request):
    language_list = Language.objects.all()[:5]
    context_dict = {}
    context_dict['languages'] = language_list
    return render(request, 'lanex/languages.html', context=context_dict)


'''
Takes a request and slug and tries to return a rendered language page with the requests 
  for a specific language.
'''
def show_language(request, language_name_slug):
    context_dict = {}
    try:
        language = Language.objects.get(slug=language_name_slug)
        requests = LanguageRequest.objects.filter(language=language)
        context_dict['requests'] = requests
        context_dict['language'] = language
        language_list = Language.objects.all()[:5]
        request_list = LanguageRequest.objects.order_by('-views')[:5]
        context_dict['languages'] = language_list
        
    except Language.DoesNotExist:
        context_dict['language'] = None
        context_dict['requests'] = None
    return render(request, 'lanex/language.html', context=context_dict)


'''
Takes a request and two slugs and tries to return a rendered request page with details of the 
  language request. Each time a language request is viewed, its view count incremenets
'''
def show_request(request, language_name_slug, request_name_slug):
    context_dict = {}
    
    try:
        language_request = LanguageRequest.objects.get(slug=request_name_slug)
        LanguageRequest.objects.filter(slug=request_name_slug).update(views=language_request.views+1)
        context_dict['request'] = language_request
        comments = language_request.comments.filter(active=True)
        new_comment = None
        
        '''
        By default, no new comment is added; if a user selects to post a comment,
          valid input which the user enters replaces the default.
        '''
        if request.method == 'POST':
            comment_form = CommentForm(data=request.POST)
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.creator = request.user
                new_comment.request = language_request
                new_comment.save()
                context_dict['new_comment'] = new_comment
            else:
                comment_form = CommentForm()
                context_dict['comment_form'] = comment_form
            
            context_dict['comment_form'] = comment_form
        context_dict['comments'] = comments
    
    except LanguageRequest.DoesNotExist:
        context_dict['request'] = None

    #print(context_dict)
    
    return render(request, 'lanex/request.html', context=context_dict)


'''
Superusers who have all permissions can add a language via this route. 
(If a language in the Other-lang category becomes noticeably popular at some point, 
  it could be made more visible and accessible by adding it along with the main languages.)
'''
@login_required
def add_language(request):
    if request.user.is_superuser:
        form = LanguageForm()
    
        if request.method == 'POST':
            form = LanguageForm(request.POST)
            if form.is_valid():
                form.save(commit=True)
                return redirect('/')
            else:
                print(form.errors)
    
        return render(request, 'lanex/add_language.html', {'form': form})
    
    else:
        return redirect('/')


'''
For valid languages, adds a request including the certain language for which it is associated.
  Created language requests are linked to their creators and view count is set to nil originally.
  As part of creating a request, users may upload an image as an addition.
'''
@login_required
def add_language_request(request, language_name_slug):
    try:
        language = Language.objects.get(slug=language_name_slug)
    except Language.DoesNotExist:
        language = None
    
    if language is None:
        return redirect('/')
    
    form = LanguageRequestForm()
    
    if request.method == 'POST':
        form = LanguageRequestForm(request.POST)
    
        if form.is_valid():
            if language:
                language_request = form.save(commit=False)
                language_request.language = language
                language_request.views = 0
                language_request.creator = request.user
    
                if 'picture' in request.FILES:
                    language_request.picture = request.FILES['picture']
    
                language_request.completed = False
                language_request.save()
                return redirect(reverse('lanex:show_request',
                                         kwargs={'language_name_slug': language_name_slug, 
                                        'request_name_slug': language_request.request_id}))
        else:
            print(form.errors)
    
    context_dict = {'form': form, 'language': language}
    return render(request, 'lanex/add_request.html', context=context_dict)


'''
An alternative version for adding requests where in this instances users specifically include the 
  language for which the request is being made by selecting it in the form.
'''
@login_required
def add_request(request):
    form = RequestForm()
    
    if request.method == 'POST':
        form = RequestForm(request.POST)
    
        if form.is_valid():
            language_request = form.save(commit=False)
            language_request.views = 0
            language_request.creator = request.user
    
            if 'picture' in request.FILES:
                    language_request.picture = request.FILES['picture']
    
            language_request.completed = False
            language_request.save()
            return redirect(reverse('lanex:show_request', 
                                    kwargs={'language_name_slug': language_request.language, 
                                    'request_name_slug': language_request.request_id}))
    
        else:
            print(form.errors)

    context_dict = {'form': form}
    return render(request, 'lanex/add_request.html', context=context_dict)


'''
Tries rendering the profile of a user, along with requests they have created. 
'''
def show_user(request, user_profile_slug):
    context_dict = {}
    try:
        user = User.objects.get(username=user_profile_slug)
        user_profile = UserProfile.objects.get(user=user)
        context_dict['user_profile'] = user_profile
        
        try:
            user_requests = LanguageRequest.objects.filter(creator=user)
            context_dict['requests'] = user_requests
        except LanguageRequest.DoesNotExist:
            context_dict['requests'] = None
    
    except User.DoesNotExist:
        context_dict['user_profile'] = None
    
    return render(request, 'lanex/user.html', context=context_dict)


'''
Takes a request and renders the search page, making use of the Bing search and responding based
  on query results, trying to look for information relevant to the search by considering language
  request titles and descriptions. 
'''
def search(request):
    query = request.GET.get('q')
    request_list = None
    
    if query != None:
        request_list = LanguageRequest.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)) 
        return render(request, 'lanex/search.html', {'query': query,'requests': request_list}) 
    
    return render(request, 'lanex/index.html', {'query': query, 'requests': request_list})


'''
Allows users to accept language requests. Checks in the process to ensure that creators of a
  request do not accept their own requests.
'''
@login_required
def accept_request(request, language_name_slug, request_name_slug):
    language_request = LanguageRequest.objects.get(slug=request_name_slug)
    if language_request.creator != request.user:
        LanguageRequest.objects.filter(slug=request_name_slug).update(completed=True)
        return redirect(reverse('lanex:show_user', 
                                kwargs={'user_profile_slug': language_request.creator.username}))
    else:
        return redirect(reverse('lanex:show_request', 
                                kwargs={'language_name_slug': language_request.language, 
                                        'request_name_slug': language_request.request_id}))


'''
For users who are creators of a request, allows the request to be deleted and checks that
 non-creators accessing the URL are not given permission to delete requests not made by them.
'''
@login_required
def delete_request(request, language_name_slug, request_name_slug):
    language_request = LanguageRequest.objects.get(slug=request_name_slug)
    if language_request.creator == request.user:
        LanguageRequest.objects.filter(slug=request_name_slug).delete()
        return redirect(reverse('lanex:show_user', 
                            kwargs={'user_profile_slug': language_request.creator.username}))
    else:
        return redirect(reverse('lanex:show_request', 
                            kwargs={'language_name_slug': language_request.language, 
                                    'request_name_slug': language_request.request_id}))


'''
For the settings page of the user; valid owners of an account should be able to update information
  about their account, including adding or replacing a profile image. Users who access the
  URL settings page of another user should not have the privilege to make modifications to what
  is not their own account.
'''
@login_required
def user_settings(request, user_profile_slug):
    if user_profile_slug == request.user.username:
        user_profile = UserProfile.objects.get(user=request.user)
        
        if request.method == "POST":
            update_user_form = UserFormAdditional(data=request.POST, instance=request.user)
            update_profile_form = UserProfileForm(data=request.POST, instance=user_profile)
        
            if update_user_form.is_valid() and update_profile_form.is_valid():
                user = update_user_form.save()
                profile = update_profile_form.save(commit=False)
                profile.user = user
        
                if 'picture' in request.FILES:
                    profile.picture = request.FILES['picture']
        
                profile.save()
                return redirect(reverse('lanex:show_user', 
                                        kwargs={'user_profile_slug': user_profile_slug}))
            else:
                print(update_user_form.errors, update_profile_form.errors)
        
        else:
            update_user_form = UserFormAdditional(instance=request.user)
            update_profile_form = UserProfileForm(instance=user_profile)
        return render(request, 'lanex/user_settings.html', 
            {'update_user_form': update_user_form, 'update_profile_form': update_profile_form})
    
    else:
        return redirect(reverse('lanex:show_user', 
                                kwargs={'user_profile_slug': user_profile_slug}))


'''
Enables users to delete their account: if successful, returns the user to the index page. 
  Checks to ensure that only account owners can delete their accounts.
'''
@login_required
def user_delete(request, user_profile_slug):
    if user_profile_slug == request.user.username:
        User.objects.filter(username=user_profile_slug).delete()
        return redirect("lanex:index")
    else:
        return redirect(reverse('lanex:show_user', 
                                kwargs={'user_profile_slug': user_profile_slug}))


'''
Like some of the privacy policies included in other websites, renders a page for it.
'''
def privacy(request):
    return render(request, 'lanex/privacy.html')

'''
Takes a request and renders a page mentioning about terms and conditions.
'''
def terms(request):
    return render(request, 'lanex/terms.html')
