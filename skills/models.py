from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O usuário deve ter um endereço de email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None  # Removendo o username padrão, usaremos o email
    email = models.EmailField(unique=True, verbose_name="E-mail")
    full_name = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf = models.CharField(max_length=14, unique=True, verbose_name="CPF")
    skill_offered = models.CharField(max_length=100, verbose_name="Habilidade que possui")
    experience_time = models.CharField(max_length=50, verbose_name="Tempo de experiência")
    skill_desired = models.CharField(max_length=100, verbose_name="Habilidade que deseja aprender")
    certificate = models.FileField(upload_to='certificates/', blank=True, null=True, verbose_name="Certificado")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'cpf', 'skill_offered', 'experience_time', 'skill_desired']

    objects = UserManager()

    def __str__(self):
        return f"{self.full_name} - Oferece: {self.skill_offered} | Quer: {self.skill_desired}"
