from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.http import  HttpResponseRedirect,Http404,HttpResponseBadRequest
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .models import User, Listing, User,Watchlist,Bid,Comment
from django import forms
from django.db.models import Max
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError


#bid form ----
class Bid_form(forms.Form):
    bid_form = forms.IntegerField(required=True, label='Create your bid')
    bid_form.widget.attrs.update({'class': 'form-control'})

#comment form -----
class Comment_form(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(), label='Leave a comment')
    comment.widget.attrs.update({
        'class': 'form-control',
        'rows': '3'
    })

#index-------
def index(request):
    all_listings = Listing.objects.all()
    #Get unique values from category query
    all_categories = Listing.objects.values('category').distinct().exclude(category__exact='')
    return render(request, "index.html", {
                    "all_categories": all_categories,     
                    "listings": all_listings})



#login_view -----
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
    
#log_out view
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

#register_view
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "register.html", {
                "message": "Username already taken."
            })
        return HttpResponseRedirect(reverse("login"))
    else:
        return render(request, "register.html")


#create listing
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

#active listing view start
def active_listing(request, listing_id):
    try:
        listing = Listing.objects.get(id=listing_id)
        curent_user = request.user.id  
        bid_count = Bid.objects.filter(item_bid=listing_id).count()
        if bid_count > 0:
            max_bid = Bid.objects.filter(item_bid=listing_id).aggregate(Max('bid'))
            max_bid = max_bid['bid__max']
        else:
            max_bid = listing.starting_bid
        if Watchlist.objects.filter(user_watchlist = curent_user, listing_item = listing_id).exists():
            watchlist_state = False
        else:
            watchlist_state = True
    except Listing.DoesNotExist:
        raise Http404("Listing not found.")
    
    # Get comments 
    comments = Comment.objects.filter(listing_comment = listing_id)
    
    if request.method == 'POST':
        form = Bid_form(request.POST)
        curent_user = request.user.id
        listing_id = request.POST["listing_id"]
        listing_item = Listing.objects.get(id = listing_id)
        user_bid = User.objects.get(id = curent_user)
        if form.is_valid():
            curent_bid = form.cleaned_data['bid_form']
            bid_count = Bid.objects.filter(item_bid=listing_id).count()
            if bid_count > 0:
                max_bid = Bid.objects.filter(item_bid=listing_id).aggregate(Max('bid'))
                max_bid = max_bid['bid__max']
            else:
                max_bid = listing_item.starting_bid
            if curent_bid > max_bid: 
                bid = Bid(user_bid=user_bid, item_bid_id=listing_item.id, bid=curent_bid)
                bid.save()
                return render(request, "active_listing.html", {
                    "listing": listing_item,
                    'comments': comments,
                    'max_bid': curent_bid,
                    'bid_count': bid_count + 1,
                    'form': Bid_form(),
                    'comment_form': Comment_form(),
                    "succ_message": f"You made a successful bid for {curent_bid} !"
                    })
            else:
                return render(request, "active_listing.html", {
                    "listing": listing_item,
                    'comments': comments,
                    'max_bid': max_bid,
                    'bid_count': bid_count,                        
                    'form': Bid_form(),
                    'comment_form': Comment_form(),
                    "err_message": "Bid can not be less than curent max bid"
                    })
        else:           
            return HttpResponseBadRequest("Form is not valid")
    #End bid block
    return render(request, "active_listing.html", {
        "listing": listing,
        'comments': comments,
        'watchlist_state': watchlist_state,
        'bid_count': bid_count,
        'max_bid': max_bid,
        'form': Bid_form(),
        'comment_form': Comment_form()
        })



#watchlist    
@login_required
def watchlist(request):
    curent_user = request.user.id      
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        watching_user = User.objects.get(id = curent_user)
        listing_item = Listing.objects.get(id = listing_id)
        watchlist = Watchlist(user_watchlist=watching_user, listing_item=listing_item)
        # Check if user already have that item in watchlist
        curent_item = Watchlist.objects.filter(user_watchlist = curent_user, listing_item = listing_item)
        if curent_item.exists():
            curent_item.delete()
        else:
            watchlist.save()
    curent_watch_id = Watchlist.objects.filter(user_watchlist=curent_user)
    curent_watchlist = curent_watch_id.all()
    return render(request, "watchlist.html", {
        "all_watchlists": curent_watchlist
        })

def category(request, category):
    listing_category = Listing.objects.filter(category=category)
    return render(request, "category.html", {
        'category': category,
        'listing_category': listing_category
    })
 

#close_bid---
@login_required
def close_bid(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        active_listing = Listing.objects.get(id=listing_id)
        active_listing.active = False
        bid_count = Bid.objects.filter(item_bid=listing_id).count()
        if bid_count > 0:
            max_bid = Bid.objects.filter(item_bid=listing_id).aggregate(Max('bid'))
            max_bid = max_bid['bid__max']
            bid_winner = Bid.objects.get(item_bid=listing_id, bid=max_bid)
            active_listing.winner = bid_winner.user_bid
        else:
            active_listing.winner = None
        active_listing.save()
        return HttpResponseRedirect(reverse('index'))

#comment
@login_required
def comment(request):
    curent_user = request.user.id
    curent_user = User.objects.get(id = curent_user)
    comment_form = Comment_form(request.POST)
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        listing_item = Listing.objects.get(id = listing_id)
        if comment_form.is_valid():
            curent_comment = comment_form.cleaned_data['comment']
            create_comment = Comment(user_comment=curent_user, listing_comment=listing_item, comment=curent_comment)
            create_comment.save()
            return HttpResponseRedirect(reverse('active_listing', args=(listing_id,)))
        else:
            raise forms.ValidationError(comment_form.errors)