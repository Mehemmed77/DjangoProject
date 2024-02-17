from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render,redirect
from django.http import HttpRequest, HttpResponse
from django.db.models import Q
from .models import Room,Topic, Message
from .forms import RoomForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from datetime import datetime,timedelta
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView
from django.views.generic.list import ListView

class MyLogoutView(TemplateView):
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        logout(request)
        return redirect("login")

def logout_view(request):
    logout(request)

    return redirect("login")

def login_view(request):
    context = {'page':'login'}

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get("username").lower()
        password = request.POST.get("password")

        user = authenticate(request, username = username, password = password)

        if user:
            login(request, user)
            return redirect('home')
        
        else:
            messages.error(request, "Username or Password is incorrect")

    return render(request,"login_register.html",context)

def register_view(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit = False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        
        else:
            messages.error(request, "Not Successful")


    context = {'form':form}
    return render(request,"login_register.html",context)


class Myindex(ListView):
    template_name = "index.html"
    model = Topic
    context_object_name = "topics"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        print(context.keys())

        q = self.request.GET.get('q') if self.request.GET.get('q') != None else ''

        topic = self.request.GET.get('topic') if self.request.GET.get('topic') != None else ''

        if topic:
            room_list = Room.objects.filter(topic__name = topic)
    
        else:
            room_list = Room.objects.filter(
                Q(topic__name__icontains = q) |
                Q(name__icontains = q) |
                Q(description__icontains = q)
            )

        # now = datetime.utcnow()
        # delta = now - timedelta(hours = 1)
        recent_messages = Message.objects.all()
        # topics = Topic.objects.all()

        room_count = Room.objects.count()
        context['rooms'] = room_list
        context['recent_messages'] = recent_messages
        context['room_count'] = room_count

        return context

def index(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    topic = request.GET.get('topic') if request.GET.get('topic') != None else ''

    if topic:
        room_list = Room.objects.filter(topic__name = topic)
    
    else:
        room_list = Room.objects.filter(
            Q(topic__name__icontains = q) |
            Q(name__icontains = q) |
            Q(description__icontains = q)
        )

    now = datetime.utcnow()
    delta = now - timedelta(hours = 1)
    recent_messages = Message.objects.filter(
        Q(created__range = (delta,now)) |
        Q(updated__range = (delta,now))
    )[::-1]

    topics = Topic.objects.all()

    room_count = Room.objects.count()
    context = {"rooms" : room_list,"topics": topics,"room_count":room_count,"recent_messages": recent_messages}
    return render(request, "index.html",context)

def user_profile(request,id):
    topic = request.GET.get('topic') if request.GET.get('topic') != None else ''
    user = User.objects.get(id = id)
    
    room_list = user.room_set.filter(host = user, topic__name__icontains = topic)
    topics = Topic.objects.all()

    recent_activity = user.message_set.all()

    context = {"user":user, "rooms":room_list,
               "topics":topics,"room_count":room_list.count(),
               "recent_messages":recent_activity
            }

    return render(request, "user_profile.html",context)

def rooms(request, id):
    room = Room.objects.get(id = id)
    participants = room.participants.all()
    room_messages = room.message_set.all().order_by("-created")[:10]


    if request.method == "POST":
        obj = Message.objects.create(user = request.user, room = room, body = request.POST.get("body"))
        obj.save()

        room.participants.add(request.user)

    context = {"room_messages": room_messages,"room":room,"participants": participants,}

    return render(request, "room.html",context = context)

@login_required(login_url = 'login/')
def create_room(request):
    context = {"form": RoomForm(),"action":"Create"}

    if request.method=="POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.instance.host = request.user
            form.save()
            return redirect("rooms", id = form.instance.id)

    return render(request, "room_form.html",context)

@login_required(login_url = 'login/')
def update_room(request, pk):
    instance = Room.objects.get(id = pk)

    if request.user != instance.host:
        return HttpResponse('You are not allowed')

    form = RoomForm(instance = instance)

    if request.method == 'POST':
        form = RoomForm(request.POST,instance = instance)
        if form.is_valid():
            form.save()
            return redirect("rooms",pk)

    context = {'form': form,"action":"Update"}

    return render(request,'room_form.html',context)

@login_required(login_url = 'login/')
def delete_room(request,pk):
    obj = Room.objects.get(id = pk)

    if request.user != obj.host:
        return HttpResponse('You are not allowed')

    if request.method == "POST":
        obj.delete()
        return redirect("home")
    
    return render(request, 'delete_room.html',{"obj":obj})

@login_required()
def delete_message(request, pk, room_id):
    context = {}

    if request.method == "POST":
        room = Room.objects.get(id = room_id)
        room_count = Message.objects.filter(user = request.user, room = room).count()

        if(room_count==1):
            room.participants.remove(request.user)

        obj = Message.objects.get(id = pk)
        obj.delete()
        return redirect('rooms',room_id)
    
    return render(request,"delete_message.html",context)
