
from django.urls import re_path, include
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
  re_path(r'^fecth-auth-token/',views.ApiAuthentication.as_view(),name='authentication_view'),

  re_path(r'^password-reset/',auth_views.PasswordResetView.as_view(
    template_name ='authentication/password_reset.html',
    email_template_name = 'authentication/password_reset_email.html',
    subject_template_name = 'authentication/password_reset_subject.txt',
    success_url = '/'),
    name='password_reset'),
  re_path(r'^password-reset-confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z_\-]+)/$',
        auth_views.PasswordResetConfirmView.as_view( template_name = 'authentication/password_reset_confirm.html' ),
      name ='password_reset_confirmation'),
  re_path(r'^password-reset-complete/',views.password_reset_complete,name='password_reset_complete'),
  re_path(r'^sign-out/',views.sign_out,name='sign_out'),
  re_path(r'^sign-in/',views.sign_in,name='sign_in'),
  re_path(r'^register-user/',views.register_user,name='register_user')

]

#this is the url config for the authentication application. This is where all the views are connected to the url.py file
