from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

# Create your models here.

# modulo para o superuser
class MyaccountManager(BaseUserManager):
    # criar usuario normal
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email')

        if not username:
            raise ValueError('User must have an username')

        user = self.model(
            email = self.normalize_email(email),#ajusta o email inserido
            username = username,
            first_name = first_name,
            last_name = last_name
        )

        user.set_password(password)#para inserir a senha no usuario
        user.save(using=self._db)
        return user

    # criar superuser
    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name= first_name,
            last_name= last_name
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user




class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100,unique=True)
    phone_number = models.CharField(max_length=50,)

    date_joined = models.DateTimeField(auto_now_add=True)#preenche sozinho
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD ='email'#para logar com email ao invez do username
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    objects = MyaccountManager()#informar que esta usando esta classe dentro de Account 

    def __str__(self) -> str:
        return self.email

    # se tem permissao de admin
    def has_perm(self,perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True


class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=100,blank=True) 
    address_line_2 = models.CharField(max_length=100,blank=True)
    profile_picture = models.ImageField(blank=True,upload_to='userprofile')
    city = models.CharField(max_length=50,blank=True)
    state = models.CharField(max_length=50,blank=True)
    country = models.CharField(max_length=50,blank=True)

    def __str__(self):
        return self.user.first_name

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'