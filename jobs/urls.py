from django.urls import path
from . import views
from . import api

urlpatterns = [
	path('fetch_resume',api.fetch_resume),
	path('resume_filter', api.resume_filteration)
]