"""
URL configuration for config project.

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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("birth/", views.search_birth_records, name="search_birth_records"),
    path("death/", views.search_death_records, name="search_death_records"),
    path("marriage/", views.search_marriage_records, name="search_marriage_records"),
    path("birth_results/", views.search_birth_records, name="birth_results"),
    path("death_results/", views.search_death_records, name="death_results"),
    path("marriage_results/", views.search_marriage_records, name="marriage_results"),
    path("person/<str:person_id>/", views.record_details, name="record_details"),
    path(
        "submit_comment/<str:person_id>/", views.submit_comment, name="submit_comment"
    ),
    path("person/<str:person_id>/export/csv/", views.export_csv, name="export_csv"),
    path("person/<str:person_id>/export/pdf/", views.export_pdf, name="export_pdf"),
    path("", views.home, name="home"),
    path("our-mission/", views.our_mission, name="our_mission"),
    path("glossary/", views.glossary, name="glossary"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
