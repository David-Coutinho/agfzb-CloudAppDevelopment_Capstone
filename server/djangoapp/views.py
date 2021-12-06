from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related model
from .models import CarModel
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
# def about(request):
# ...
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
#def contact(request):
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
# def login_request(request):
# ...
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
# ...
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = dict()
    if request.method == "GET":
        url = "https://a44733b1.eu-gb.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context['dealership_list'] = dealerships
        # Concat all dealer's short name
        #dealer_names = [dealer.short_name for dealer in dealerships]
        #context = {'dealer_names': dealer_names}
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)
        # return HttpResponse(dealer_names)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealerId):
    context = dict()
    if request.method == "GET":
        url = "https://a44733b1.eu-gb.apigw.appdomain.cloud/api/review"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url, dealerId)
        context['reviews_list'] = reviews
        context['dealerId'] = dealerId
        # Concat all dealer's short name
        """
        review_names = ' '.join([review.name for review in reviews])
        review_reviews = ' '.join([review.review for review in reviews])
        review_sentiments = ' '.join([review.sentiment for review in reviews])
        context = {"review_names": reviews}
        """
        # Return a list of dealer short name
        # return HttpResponse([review_names, review_reviews, review_sentiments], context)
        return render(request, 'djangoapp/dealer_details.html', context)
# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
"""
def add_review(request, dealerId):
    context = dict()
    # check if user is authenticated
    #if user.is_authenticated:
    if request.method == "POST":
        url = "https://a44733b1.eu-gb.apigw.appdomain.cloud/api/review"

        review = dict()
        review["id"] = car.id #int
        review["name"] = car.name #string
        review["review"] = car.review #string
        review["purchase"] = car.purchase #bool
        review["purchase_date"] = car.year.strftime("%Y")
        review["car_make"] = car.make
        review["car_model"] = car.model
        review["car_year"] = car.year
        
        json_payload = dict()
        json_payload['review'] = review

        json_result = post_request(url, json_payload, dealerId=dealerId)
        redirect("djangoapp:dealer_details", dealerId=dealerId)
    elif request.method == "GET": 
        # query the cars with the dealer id to be reviewed
        # the queried cars will be used in the <select> dropdown
        context['cars'] = {}
        context['dealerId'] = dealerId
        return render(request, 'djangoapp/add_review.html', context)
"""
# Create a `add_review` view to submit a review
def add_review(request, dealerId):
    context = dict()
    if request.method == 'GET':
        context['dealerId'] = dealerId
        context['cars'] = CarModel.objects.filter(dealer_id=dealerId)
        url = "https://a44733b1.eu-gb.apigw.appdomain.cloud/api/dealership"
        dealer = get_dealer_by_id_from_cf(url, dealerId)
        if dealer:
            context['dealer'] = dealer[0]
        else:
            context['dealer'] = {'full_name': 'No dealer'}
        return render(request, 'djangoapp/add_review.html', context)
    if request.method == "POST":
        user = request.user
        if user.is_authenticated:
            content = request.POST['content']
            car_id = int(request.POST['car'])
            car = get_object_or_404(CarModel, pk=car_id)
            purchase_date = request.POST['purchasedate']
            
            review = dict()
            review["id"] = 0 #change id
            if 'purchasecheck' in request.POST:
                review["purchase"] = True
            else:
                review["purchase"] = False
            review["dealership"] = dealerId
            review["review"] = content
            review["name"] = user.get_full_name()
            review['car_make'] = car.car_id.name
            review['car_model'] = car.name
            review['car_year'] = car.year.strftime("%Y")
            review['purchase_date'] = purchase_date
            
            json_payload = dict()
            json_payload["review"] = review
            url = 'https://a44733b1.eu-gb.apigw.appdomain.cloud/api/review'
            post_request(url, json_payload, dealerId=dealerId)
            return redirect("djangoapp:dealer_details", dealerId=dealerId)