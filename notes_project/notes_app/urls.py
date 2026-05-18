from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_note, name='add_note'),
    path('delete/<str:note_id>/', views.delete_note, name='delete_note'),
    path('note/<str:note_id>/', views.note_detail, name='note_detail'),
    path('signup/', views.signup, name='signup'),  # Add this line
]