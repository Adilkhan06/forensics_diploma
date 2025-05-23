from django.shortcuts import render
from django.http import JsonResponse
from ingest.models import File
def home_view(request):
    return render(request, 'core/home.html', {})


