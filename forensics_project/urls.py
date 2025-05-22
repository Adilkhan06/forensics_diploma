"""
URL configuration for forensics_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from core.views import home_view
from ingest.views import upload_dumps_view, upload_success_view
from reporting import views
from reporting.views import generate_report
from visualization.views import visualize_graph

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('upload/', upload_dumps_view, name='upload_dumps'),
    path('report/', generate_report, name='generate_report'),
    path('graph/', visualize_graph, name='visualize_graph'),
    path('upload/success/', upload_success_view, name='upload_success'),
    path('ai-report/', views.generate_ai_report, name='generate_ai_report'),
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)