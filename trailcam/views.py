from django.shortcuts import render, HttpResponse, HttpResponseRedirect

import datetime

# Create your views here.

def main(request):
    return HttpResponseRedirect("/classify/")