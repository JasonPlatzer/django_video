from django.contrib.messages.api import warning
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models.functions import Lower
from .forms import SearchForm, VideoForm
from .models import Video

def home(request):
    app_name = 'Cat videos'
    return render(request, 'video_collection/home.html', {'app_name': app_name})

def add(request):
    if request.method == 'POST':
        new_video_form = VideoForm(request.POST)
        if new_video_form.is_valid():
            try:
                new_video_form.save()
                return redirect('video_list')
                #messages.info(request, 'New video saved')
            except ValidationError:
                messages.warning(request, 'Invalid youtube url')
            except IntegrityError:
                messages.warning(request, 'You already added that video') 

        
        messages.warning(request, 'Please check the data entered')
        return render(request, 'video_collection/add.html', {'new_video_form': new_video_form} )        
    
    new_video_form = VideoForm
    return render(request, 'video_collection/add.html', {'new_video_form': new_video_form})

def video_list(request):
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        search_term = search_form.cleaned_data['search_term']
        # returns a dictionary
        # the key is field in forms.py
        videos = Video.objects.filter(name__icontains=search_term).order_by(Lower('name'))
    else:
        search_form = SearchForm()
        # searches by keyword, case insensitive
        videos = Video.objects.order_by(Lower('name'))
    return render(request, 'video_collection/video_list.html', {'videos': videos, 'search_form': search_form})
    

def details(request, video_pk):
    video_page = get_object_or_404(Video, pk=video_pk)
    #video = Video.objects.filter('video_id')
    return render(request, 'video_collection/details.html', {'video_page': video_page})




