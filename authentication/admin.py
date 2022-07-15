from django.contrib import admin
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth.admin import UserAdmin


# Register your models here.
class UserProfileInline(admin.StackedInline):
  list_display = ['phone_number','address']
  model = UserProfile

def phone_number(self):
  if self.userprofile.phone_number:
    value = self.userprofile.phone_number
  else:
    value = ''
  return value

class UserModelAdmin(UserAdmin):
  inlines = [UserProfileInline]
  list_display = ['id','first_name','last_name','email',phone_number,'is_superuser',]
  list_per_page = 10
  list_display_links = ['id']
  ordering = ['-date_joined']
  search_fields = ['username','first_name','last_name','email']



admin.site.unregister(User)
admin.site.register(User,UserModelAdmin)

