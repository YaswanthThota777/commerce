from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import AuctionListingForm, BidForm, CommentForm
from .models import User, AuctionListing,Bid, Comment, Watchlist,Category

def categories_view(request):
    categories = Category.objects.all()
    return render(request, 'auctions/categories.html', {
        'categories': categories
    })

def category_listings_view(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    listings = AuctionListing.objects.filter(category=category, is_active=True)
    return render(request, 'auctions/category_listings.html', {
        'category': category,
        'listings': listings
    })



@login_required
def watchlist_view(request):
    user = request.user
    watchlist_items = Watchlist.objects.filter(user=user).select_related('auction')
    return render(request, 'auctions/watchlist.html', {
        'watchlist_items': watchlist_items
    })


def listing_view(request, listing_id):
    listing = get_object_or_404(AuctionListing, id=listing_id)
    user = request.user
    is_in_watchlist = user.is_authenticated and Watchlist.objects.filter(user=user, auction=listing).exists()
    is_owner = user == listing.owner
    is_winner = user.is_authenticated and listing.highest_bidder == user

    if request.method == 'POST':
        if 'bid' in request.POST:
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                new_bid = bid_form.cleaned_data['amount']
                current_price = listing.get_current_price()
                if new_bid > current_price:
                    bid = bid_form.save(commit=False)
                    bid.bidder = user
                    bid.auction = listing
                    bid.save()
                    listing.highest_bidder = user
                    listing.save()
                    messages.success(request, 'Your bid was placed successfully!')
                    return redirect('listing_view', listing_id=listing_id)
                else:
                    messages.error(request, 'Your bid must be higher than the current price.')
        elif 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.commenter = user
                comment.auction = listing
                comment.save()
                messages.success(request, 'Your comment was added successfully!')
                return redirect('listing_view', listing_id=listing_id)
        elif 'watchlist' in request.POST:
            if is_in_watchlist:
                Watchlist.objects.filter(user=user, auction=listing).delete()
                messages.success(request, 'Removed from your watchlist.')
            else:
                Watchlist.objects.create(user=user, auction=listing)
                messages.success(request, 'Added to your watchlist.')
            return redirect('listing_view', listing_id=listing_id)
        elif 'close' in request.POST and is_owner:
            listing.is_active = False
            listing.save()
            messages.success(request, 'The auction has been closed.')
            return redirect('listing_view', listing_id=listing_id)

    bid_form = BidForm()
    comment_form = CommentForm()
    comments = listing.comments.all()
    return render(request, 'auctions/listing.html', {
        'listing': listing,
        'is_in_watchlist': is_in_watchlist,
        'is_owner': is_owner,
        'is_winner': is_winner,
        'bid_form': bid_form,
        'comment_form': comment_form,
        'comments': comments,
    })


@login_required
def create_listing(request):
    if request.method == 'POST':
        form = AuctionListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user  # Set the owner to the currently logged-in user
            listing.save()
            return redirect('index')  # Adjust as needed
    else:
        form = AuctionListingForm()

    return render(request, 'auctions/create_listing.html', {'form': form})


def index(request):
    listings = AuctionListing.objects.filter(is_active=True)
    return render(request, 'auctions/index.html', {'listings': listings})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
