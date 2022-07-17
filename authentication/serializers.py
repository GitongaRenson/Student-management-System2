from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class LoginSerializer(serializers.Serializer):

  username = serializers.CharField(required=True)
  password = serializers.CharField(required=True,write_only=True)
  
  class Meta:
    model = User
    fields = ['username','password']

  def validate(self, data):
        username = data.get('username')
        password = data.get('username')
        user = User.objects.filter(username=username)
        if not user: 
            raise serializers.ValidationError("Invalid username or password")
        if user.first().check_password(password):
            raise serializers.ValidationError("Invalid username or password")
        return data



    