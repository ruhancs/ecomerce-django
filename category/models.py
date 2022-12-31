from django.db import models
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100,unique=True)
    description = models.TextField(max_length=255, blank=True)
    cat_image = models.ImageField(upload_to='photos/categories',blank=True)#pasta que sera inserida as imagens para utilizar

    class Meta:#nome do db no pagina de admin
        verbose_name = 'category'
        verbose_name_plural= 'categories'

    def get_url(self):
    #pega o nome da url dentro de store para formar a url de busca por categoria 
        return reverse('products_by_category', args=[self.slug])
    
    def __str__(self) -> str: 
        return self.category_name