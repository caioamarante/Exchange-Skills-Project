from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'cpf', 'skill_offered', 'experience_time', 'skill_desired', 'is_staff')
    search_fields = ('full_name', 'email', 'cpf', 'skill_offered', 'skill_desired')
    list_filter = ('skill_offered', 'skill_desired', 'is_staff', 'is_superuser')
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Informações Pessoais', {'fields': ('email', 'password', 'full_name', 'cpf', 'profile_picture')}),
        ('Habilidades e Experiência', {'fields': ('skill_offered', 'experience_time', 'skill_desired', 'certificate')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
