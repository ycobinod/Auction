from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .models import User, Listing, User


def index(request):
    return render(request, "index.html")

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("index"))
            else:
                return render(request, "login.html", {
                    "message": "Invalid username and/or password."
                })
        else:
            return render(request, "login.html", {
                "message": "Please fill out both fields."
            })
    else:
        return render(request, "login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")

        # Check if all fields are provided
        if not username or not email or not password or not confirmation:
            return render(request, "register.html", {
                "message": "All fields are required."
            })

        # Ensure password matches confirmation
        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)  # Automatically login the user after registration
            return HttpResponseRedirect(reverse("login"))
        except IntegrityError:
            return render(request, "register.html", {
                "message": "Username already taken."
            })
    else:
        return render(request, "register.html")
    

@login_required
def create_listing(request):
    if request.method == "POST":
        name = request.POST["name"]
        category = request.POST['category']
        starting_bid = request.POST["starting_bid"]       
        description = request.POST["description"]
        url = request.POST["url"]
        owner = request.POST['owner']
        user_owner = User.objects.get(username=owner)
        try:
            Listings_created = Listing(name=name, category=category, starting_bid=starting_bid, description=description, url=url, owner=user_owner)
            Listings_created.save()
            return HttpResponseRedirect(reverse("index"))
        except IntegrityError:
            return render(request, "create_listing.html", {
                "message": "Listing not created."
            })        
    return render(request, "create_listing.html")


