from django.shortcuts import render
from django.http import JsonResponse
from analysis.tasks import run_analysis
from analysis.models import Match
# Create your views here.