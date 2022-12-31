from django.contrib import admin
from .models import Category #declaraçao do database

# Register your models here.
# para o slug ser criado automaticamente
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')


admin.site.register(Category, CategoryAdmin)