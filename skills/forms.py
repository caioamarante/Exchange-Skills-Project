from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'full_name', 'cpf', 'skill_offered', 'experience_time', 'skill_desired', 'profile_picture', 'certificate')
        widgets = {
            'experience_time': forms.TextInput(attrs={'placeholder': 'Ex: 2 anos, 6 meses, etc.'}),
            'cpf': forms.TextInput(attrs={'placeholder': '000.000.000-00'}),
            'skill_offered': forms.TextInput(attrs={'placeholder': 'Ex: Python, Design Gráfico'}),
            'skill_desired': forms.TextInput(attrs={'placeholder': 'Ex: React, Marketing'}),
        }

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'full_name', 'cpf', 'skill_offered', 'experience_time', 'skill_desired', 'profile_picture', 'certificate')
        widgets = {
            'experience_time': forms.TextInput(attrs={'placeholder': 'Ex: 2 anos, 6 meses, etc.'}),
            'cpf': forms.TextInput(attrs={'placeholder': '000.000.000-00'}),
            'skill_offered': forms.TextInput(attrs={'placeholder': 'Ex: Python, Design Gráfico'}),
            'skill_desired': forms.TextInput(attrs={'placeholder': 'Ex: React, Marketing'}),
        }
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('full_name', 'skill_offered', 'experience_time', 'skill_desired', 'profile_picture', 'certificate')
        widgets = {
            'experience_time': forms.TextInput(attrs={'placeholder': 'Ex: 2 anos, 6 meses, etc.'}),
            'skill_offered': forms.TextInput(attrs={'placeholder': 'Ex: Python, Design Gráfico, Inglês'}),
            'skill_desired': forms.TextInput(attrs={'placeholder': 'Ex: Edição de Vídeo, Marketing, React'}),
        }

class SupportForm(forms.Form):
    name = forms.CharField(max_length=100, label='Seu Nome')
    email = forms.EmailField(label='Seu E-mail')
    subject = forms.CharField(max_length=150, label='Assunto')
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), label='Mensagem')

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='E-mail', widget=forms.EmailInput(attrs={'autofocus': True}))
