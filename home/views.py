import argparse
import email
import re
from unicodedata import name
from urllib import request
from django.shortcuts import redirect, render
from .models import StudentNames
from .tables import StudentTable
from django_tables2 import RequestConfig
from django.core.paginator import Paginator
from .forms import AddStudentForms, UpdateStudentForm
from django.template.context_processors import csrf
from django.contrib import messages
from django.db.models import Q
from datetime import datetime
from django.contrib.auth.decorators import login_required
from .utils import send_confirmation_email
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import authentication,permissions
from rest_framework import status,generics,filters
from .serializers import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from django.conf import settings
import requests
from .utils import generate_jwt_token,generate_excel_csv,generate_excel_xlsx,generate_pdf
import json
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from rest_framework.decorators import action
from drf_yasg.utils import swagger_serializer_method
from drf_yasg import openapi
import csv
from django.http import HttpResponse


# Create your views here.

#This is the default root index for the application and should be accessed from the browser.
def index(request):
   

#queryset fetchinh all the data for studentnames
    student_names = StudentNames.objects.all().order_by('-reported_on')

#Django tables module
    student_table = StudentTable(student_names)
    RequestConfig(request,paginate={'per_page':3}).configure(student_table)

#custom table pagination module
    paginator = Paginator(student_names,10)
    page_number = request.GET.get('page')
    paginator_module = paginator.get_page(page_number)

#Dictionary containing all the variables we want to pass and show on the HTML
    args = {'student_names':student_names,'student_table':student_table,'paginator_module':paginator_module}
    return render(request,'home/index.html',args)


@login_required(login_url='/sign-in/')
def add_students(request):
    if request.method == 'POST':
        form = AddStudentForms(request.POST)
        if form.is_valid():
            form_instance = form.save(commit=False)
            name = form.cleaned_data['name']
            form.instance.name = name.upper()
            form_instance.save()
            messages.add_message(request, messages.SUCCESS, 'Data added Successfully.')
            return redirect('index')
        else:
            args = {'form':form}
            return render(request,'home/add-student.html',args)
    else:
        form = AddStudentForms()
        args = {'form':form}
        args.update(csrf(request))
        return render(request,'home/add-student.html',args)



@login_required(login_url='/sign-in/')
def update_student(request,id):
    instance = StudentNames.objects.get(id=id)
    if request.method == 'POST':
        form = UpdateStudentForm(request.POST,instance=instance)
        if form.is_valid():
            form_instance = form.save(commit=False)
            name = form.cleaned_data['name']
            form.instance.name = name.upper()
            form.instance.email = form.cleaned_data['email']
            form.instance.phone_number = form.cleaned_data['phone_number']
            form.instance.course = form.cleaned_data['course']
            form.instance.gpa = form.cleaned_data['gpa']
            form_instance.save()
            messages.add_message(request, messages.SUCCESS, form.cleaned_data['name']+' Data Updated Successfully.')
            email = form.cleaned_data['email']
            message = 'Hello, '+name+ ' Your details have been updated in your student portal. If you have not triggered this please visit your department for further assistance.'
            subject = 'Student Details Update'
            request = request
            mail_data = {'email':email,'message':message,'subject':subject}
            mail = send_confirmation_email(mail_data)
            messages.add_message(request, messages.INFO, mail)
            return redirect('index')

        else:
            args = {'form':form}
            return render(request, 'home/update-student.html',args)
    else:
        form = UpdateStudentForm(instance=instance)
        args = {'form':form}
        args.update(csrf(request))
        return render(request,'home/update-student.html',args)




@login_required(login_url='/sign-in/')
def delete_student(request,id):
    instance = StudentNames.objects.get(id=id)
    email = instance.email
    name = instance.name
    message = 'Hello ' +name+' Your details have been deleted from the Student database. If you did not request for this please contant the head of department'
    subject = 'student Data Removed!'
    mail_data = {'email':email,'message':message,'subject':subject}
    mail = send_confirmation_email(mail_data)
    messages.add_message(request, messages.INFO, mail)



    instance.delete()
    messages.add_message(request, messages.INFO, 'Student Deleted Successfully.')
    return redirect('index')




def search_student(request):
    search_keyword = request.GET['student_search']
    if search_keyword !='':
        searched_queryset = StudentNames.objects.all().filter(
        Q(name__icontains=search_keyword) |  Q(email__icontains=search_keyword) |  Q(gender__iexact=search_keyword) |  Q(phone_number__icontains=search_keyword) | Q(course__icontains=search_keyword)| Q(gpa__icontains=search_keyword)
        ).order_by('-reported_on')


        if 'csv-format' in request.GET:
            return generate_excel_csv(searched_queryset)

        if 'xlsx-format' in request.GET:
            return generate_excel_xlsx(searched_queryset)

        if 'pdf-format' in request.GET:
            return generate_pdf(request,searched_queryset)
            # return generate_reportlab_pdf(searched_queryset)
      
         
        #custom table pagination module
        paginator = Paginator(searched_queryset,10)
        page_number = request.GET.get('page')
        paginator_module = paginator.get_page(page_number)
        args = {'paginator_module':paginator_module,'search_keyword':search_keyword}
        
        return render(request,'home/index.html',args)
    else:
        return redirect('index')
    
class StudentsView(generics.ListAPIView,generics.CreateAPIView):
    authentication_classes = [JWTTokenUserAuthentication]
    permission_classes = [IsAuthenticated]
    
    @method_decorator(
        name='get students endpoint',
        decorator=swagger_auto_schema(
            responses= {200: StudentSerializer(many=True)},
            operation_id='Fetch students',
            operation_description="""This endpoint is supposed to be used to fetch and show student data in the system.It requires a jwt token(generated from the auth endpoint) to get the data """
        ),
    )


    
    def get(self,request):
        user= request.user
        print(user)
        queryset = StudentNames.objects.all()
        serializer = StudentSerializer(queryset,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    @method_decorator(
        name='Add new students endpoint',
        decorator=swagger_auto_schema(
            responses= {200: CreateStudentSerializer(),400: CreateStudentSerializer()},
            operation_id='Add students',
            operation_description="""This endpoint is supposed to be used to create and show student data in the system.It requires a jwt token(generated from the auth endpoint) to use the end point """
        ),
    )


    def post(self, request):
        serializer =CreateStudentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status.HTTP_201_CREATED)



class StudentsUpdateView(generics.UpdateAPIView,generics.DestroyAPIView):
    authentication_classes = [JWTTokenUserAuthentication]
    permission_classes=[IsAuthenticated]
    parser_classes=[JSONParser]


    @method_decorator(
        name='Update new student endpoint',
        decorator=swagger_auto_schema(
            request_body=UpdateStudentSerializer,
            responses= {200: UpdateStudentSerializer(),400: UpdateStudentSerializer()},
            operation_id='Update existing students',
            operation_description="""This endpoint is supposed to be used to update and show existing student data in the system.
            It requires a jwt token(generated from the auth endpoint) to use the endpoint and a student id passed thought the url."""
        ),
    )


    def put(self, request,id):
        object_instance = StudentNames.objects.get(id=id)
        serializer = UpdateStudentSerializer(object_instance,data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_200_OK)
    

    
    @method_decorator(
        name='Delete student endpoint',
        decorator=swagger_auto_schema(
            responses= {204:''},
            operation_id='Delete existing student',
            operation_description="""This endpoint is supposed to be used to delete existing student data in the system.
            It requires a jwt token(generated from the auth endpoint) to use the endpoint and a student id passed thought the url.
            """
        ),
    )

    def delete(self, request, id):
        object_instance = StudentNames.objects.get(id=id)
        email = object_instance.email
        name=object_instance.name
        message = 'Hello  ' +name+' Your details have been deleted from the Student database. If you did not request for this please contant the head of department'
        subject = 'Student Data Removed!'
        mail_data = {'email':email,'message':message,'subject':subject}
        mail = send_confirmation_email(mail_data)
        object_instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



def fetch_quote(request):
    url  = '{}{}'.format(settings.QUOTES_BASE_URL,'qod/')
    response = requests.get(url)
    args = {}
    if response.status_code == 200:        
        data = response.json()['contents']['quotes']
        for item in data:
            quote = item['quote']
            author = item['author']
            args['quote'] = quote
            args['author'] = author
        return render(request,'home/show_quotes.html',args)
    else:
        messages.add_message(request, messages.ERROR, "An error occured fetching the data")
        return redirect('index')



def simulate_adding_students(request):
    # simulate_deleting_student(request)
    # return redirect('index')
    payload = {'name':'michelle obama','email':'michelle@gmail.com','phone_number':'1451366723266',
    'course':'IC','gender':'Female'}
    auth_base_url = 'http://127.0.0.1:8000/'
    url  = '{}{}'.format(auth_base_url,'students/')
    headers= {
    "Authorization": "Token "+  str(generate_jwt_token(request)), 
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=utf-8'
    }
    response = requests.post(url,headers=headers,data=json.dumps(payload))
    if response.status_code == 201:
        messages.add_message(request, messages.SUCCESS, "Simulated student data added successfully!")
        return redirect('index')
    else:
        message = response.json()
        messages.add_message(request, messages.ERROR, message)
        return redirect('index')



def simulate_updating_students(request):
    payload = {'name':'michelle obama','email':'michelle@gmail.com','phone_number':'1451366723266',
    'course':'IC','gender':'Female'}
    auth_base_url = 'http://127.0.0.1:8000/'
    url  = '{}{}'.format(auth_base_url,'update-students/'+str(27)+"/")
    headers= {
    "Authorization": "Bearer "+  generate_jwt_token(request), 
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=utf-8'
    }
    response = requests.put(url,headers=headers,data=json.dumps(payload))
    if response.status_code == 200:
        return messages.add_message(request, messages.INFO, "Simulated student data updated successfully!")
    else:
        message = response.json()
        return messages.add_message(request, messages.ERROR, message)

def simulate_deleting_student(request):
    auth_base_url = 'http://127.0.0.1:8000/'
    url  = '{}{}'.format(auth_base_url,'update-students/'+str(27)+"/")
    headers= {
    "Authorization": "Bearer "+  generate_jwt_token(request), 
    'Accept': 'application/json',
    'Content-Type': 'application/json; charset=utf-8'
    }
    response = requests.delete(url,headers=headers)
    if response.status_code == 204:
        return messages.add_message(request, messages.INFO, "Simulated Student data deleted successfully!")
    else:
        message = response.json()
        return messages.add_message(request, messages.ERROR, message)