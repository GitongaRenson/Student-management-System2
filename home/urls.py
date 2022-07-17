from django.urls import re_path, include
from . import views


urlpatterns = [
re_path(r'^simulate-adding-students/',views.simulate_adding_students,name='simulate_adding_students'), 
  
 re_path(r'^students/',views.StudentsView.as_view(),name='get_create_students'), 
 re_path(r'^fetch-quote/',views.fetch_quote,name='fetch_quote'),
 re_path(r'^update-students/(?P<id>[\w-]+)/$',views.StudentsUpdateView.as_view(),name='update_delete_students'), 

 re_path(r'^add-students/',views.add_students,name='add_students'), 
 re_path(r'^update-student/(?P<id>[\w-]+)/$',views.update_student,name='update_student'),
 re_path(r'^delete-students/(?P<id>[\w-]+)/$',views.delete_student,name='delete_student'),
 re_path(r'^search-student/',views.search_student,name='search_student'), 
 re_path(r'^$',views.index,name='index'),
 
]

#This is the url config for the home application. This is where all the views are connected to the url