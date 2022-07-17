from rest_framework import serializers
from .models import StudentNames



class StudentSerializer(serializers.ModelSerializer):
  class Meta:
    model = StudentNames
    fields = ['name','email','gender','phone_number','course','reported_on']


class CreateStudentSerializer(serializers.ModelSerializer):
  
  name = serializers.CharField(required=True)

  class Meta:
    model=StudentNames
    fields = ['name','email','gender','phone_number','course','gpa']

  def validate(self, data):
    phone = data.get('phone_number')
    if len(phone)<10:
      raise serializers.ValidationError("Phone numbers Should be 10 Characters or more")
    if len(phone)>14:
      raise serializers.ValidationError("Phone numbers Should be 14 Characters or less")
    return data

  
  def create(self, validated_data):
    return StudentNames.objects.create(**validated_data)


class UpdateStudentSerializer(serializers.ModelSerializer):
  

  class Meta:
    model =StudentNames
    fields = ['name','email','gender','phone_number','course','gpa']
  
  def validate(self, data):
    phone = data.get('phone_number')
    if len(phone)<10:
      raise serializers.ValidationError("Phone numbers Should be 10 Characters or more")
    if len(phone)>14:
      raise serializers.ValidationError("Phone numbers Should be 14 Characters or less")
    return data

  def update(self, instance, validated_data):
    return super().update(instance, validated_data)




