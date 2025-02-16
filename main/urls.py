from django.urls import include, path
from . import views

urlpatterns = [
    path('get_n30/', views.ProcessDataApiView.as_view()),
]