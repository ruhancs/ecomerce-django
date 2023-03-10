from django.contrib import admin
from django.contrib.auth.admin import UserAdmin #para bloquear a editar senha encriptografada na area do admin
from .models import Account, UserProfile
from django.utils.html import format_html

# Register your models here.
class AccountAdmin(UserAdmin):
    # itens que serao mostrados na area do usuario
    list_display =('email', 'first_name','last_name','username','last_login','date_joined','is_active')
    list_display_links = ('email', 'first_name', 'last_name', 'username')
    readonly_fields = ('last_login', 'date_joined')
    ordering = ('-date_joined',)
    
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class ProfileAdmin(admin.ModelAdmin):
    def thumbnail(self,object):
        return format_html('<img src="{}" width="30" style="border-radius:50%;>'.format(object.profile_picture.url))
    
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail','user','city','state','country')

admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile,ProfileAdmin)
