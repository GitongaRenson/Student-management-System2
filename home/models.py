from random import choices
from tabnanny import verbose
from django.db import models
from django.forms import BooleanField

# Create your models here.
#we are following rules of django ORM and avoiding writing in SQL


class StudentNames(models.Model):
  COURSE_CHOICES = ( 
    ('MCS','MCS'),
    ('IM','IM'),
    ('AS','AS'),
    ('IC','IC'),
  )
  
  
  GENDER_CHOICES = ( 
    ('Male','Male'),
    ('Female','Female'),
    ('Others','Others'),
  )
  
  
  name = models.CharField(max_length=255,null=True,blank=True)#null tells django whether the field is mandatory or not 
  email = models.EmailField(max_length=150,unique=True)#leaving the rest blank tells django that the field is mandatory'''
  gender = models.CharField(max_length= 20, choices=GENDER_CHOICES)
  phone_number = models.CharField(max_length=20, unique=True)
  course = models.CharField(max_length=20, choices=COURSE_CHOICES)
  gpa = models.FloatField()
  reported_on = models.DateTimeField(auto_now_add=True)

  
  
  class Meta:
    verbose_name = 'Student Name'
    verbose_name_plural = 'Student Names'
  
  
  
  def __str__(self):
    return self.name +' -- '+self.email