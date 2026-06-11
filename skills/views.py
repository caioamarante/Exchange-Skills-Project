from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm
from .models import User

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

from django.db.models import Q

@login_required
def dashboard(request):
    user = request.user
    
    # Separar as habilidades em listas, removendo espaços em branco
    user_skills_offered = [s.strip() for s in user.skill_offered.split(',') if s.strip()]
    user_skills_desired = [s.strip() for s in user.skill_desired.split(',') if s.strip()]
    
    # Construir query dinâmica: A outra pessoa OFERECE algo que EU DESEJO
    q_other_offers = Q()
    for skill in user_skills_desired:
        q_other_offers |= Q(skill_offered__icontains=skill)
        
    # Construir query dinâmica: A outra pessoa DESEJA algo que EU OFEREÇO
    q_other_desires = Q()
    for skill in user_skills_offered:
        q_other_desires |= Q(skill_desired__icontains=skill)

    # Se o usuário não preencheu nenhuma habilidade, retornamos vazio
    if not q_other_offers and not q_other_desires:
        perfect_matches = User.objects.none()
        potential_teachers = User.objects.none()
    else:
        # Match Perfeito: Tem que atender às DUAS condições (Ele oferece o que quero E quer o que ofereço)
        perfect_matches = User.objects.filter(q_other_offers, q_other_desires).exclude(id=user.id).distinct()
        
        # Professores em Potencial: Atende apenas à primeira condição (Ele oferece o que eu quero)
        if q_other_offers:
            potential_teachers = User.objects.filter(q_other_offers).exclude(id=user.id).exclude(id__in=perfect_matches.values_list('id', flat=True)).distinct()
        else:
            potential_teachers = User.objects.none()

    return render(request, 'dashboard.html', {
        'perfect_matches': perfect_matches,
        'potential_teachers': potential_teachers
    })

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'profile.html', {'form': form})
