from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

# First page. (List of albums I've bought.)
def index(request):
    return HttpResponse("This is first page. You will see list of albums I have bought.")

# Search albums from database. (by Artist/Album title)
def search(request):
    return HttpResponse("Search album by Artist/Album title.")

# See search result.
def search_result(request):
    return HttpResponse("Search result.")

# Add album from Bugs/Naver music.
def add_album(request):
    return HttpResponse("Add album from Bugs/Naver music.")

# Add result and confirm add this information or cancel.
def add_result(request):
    return HttpResponse("Confirm parsed album information and add it to database.")

# Add album information to database.
def add_action(request):
    return HttpResponse("Add action!")

# See album detail information
def see_album(request):
    return HttpResponse("View detail information of selected album")

# Confirm delete information from database.
def confirm_delete(request):
    return HttpResponse("Confirm to delete album from database")

# Delete album information from database.
def delete(request):
    return HttpResponse("Delete album")