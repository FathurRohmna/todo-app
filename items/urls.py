from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("addItems", views.addItems, name="addItems"),
    path('create-category/', views.create_category, name='create_category'),
    path("statusItems", views.statusItems, name="statusItems"),
    path("deleteItems", views.deleteItems, name="deleteItems"),
    path("updateItems", views.updateItems, name="updateItems"),
]