from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm, SupportForm
from .models import User, Like, ChatRoom, Message

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

    # Buscar curtidas e matches para atualizar botões
    likes_sent_ids = Like.objects.filter(from_user=user).values_list('to_user_id', flat=True)
    
    # Pegar todos os ChatRooms onde o usuário está (user1 ou user2)
    chat_rooms = ChatRoom.objects.filter(Q(user1=user) | Q(user2=user))
    matched_user_ids = []
    for room in chat_rooms:
        matched_user_ids.append(room.get_other_user(user).id)

    return render(request, 'dashboard.html', {
        'perfect_matches': perfect_matches,
        'potential_teachers': potential_teachers,
        'likes_sent_ids': list(likes_sent_ids),
        'matched_user_ids': matched_user_ids
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

@login_required
def support_view(request):
    if request.method == 'POST':
        form = SupportForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            full_message = f"Nome: {name}\nE-mail: {email}\n\nMensagem:\n{message}"
            
            try:
                send_mail(
                    subject=f"Suporte Exchange Skills: {subject}",
                    message=full_message,
                    from_email=None,  # Usa o EMAIL_HOST_USER do settings
                    recipient_list=['suporte.caioamarante@gmail.com'],
                    fail_silently=False,
                )
                messages.success(request, 'Sua mensagem foi enviada com sucesso! Responderemos em breve.')
                return redirect('support')
            except Exception as e:
                messages.error(request, 'Erro ao enviar a mensagem. Verifique se o e-mail e a Senha de App estão corretos no arquivo .env.')
    else:
        initial_data = {'name': request.user.full_name, 'email': request.user.email}
        form = SupportForm(initial=initial_data)
        
    return render(request, 'support.html', {'form': form})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404

@login_required
def like_user(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        
        # Evitar curtir a si mesmo
        if target_user == request.user:
            return JsonResponse({'error': 'Ação inválida'}, status=400)
            
        # Criar a curtida se não existir
        Like.objects.get_or_create(from_user=request.user, to_user=target_user)
        
        # Verificar se é Match (o outro usuário também me curtiu?)
        is_match = Like.objects.filter(from_user=target_user, to_user=request.user).exists()
        
        if is_match:
            # Verifica se já não existe uma sala de chat
            room_exists = ChatRoom.objects.filter(
                Q(user1=request.user, user2=target_user) | Q(user1=target_user, user2=request.user)
            ).exists()
            
            if not room_exists:
                # Cria a sala de chat (Garante ordem dos IDs para facilitar buscas futuras, embora não seja estritamente necessário pelo Q)
                ChatRoom.objects.create(user1=request.user, user2=target_user)
                
            return JsonResponse({'status': 'match'})
            
        return JsonResponse({'status': 'liked'})
    return JsonResponse({'error': 'Método inválido'}, status=405)

@login_required
def chat_list(request):
    # Buscar salas de chat do usuário
    rooms = ChatRoom.objects.filter(Q(user1=request.user) | Q(user2=request.user)).order_by('-created_at')
    
    new_matches = []
    active_chats = []
    
    for room in rooms:
        other_user = room.get_other_user(request.user)
        last_message = room.messages.last()
        
        chat_info = {
            'room': room,
            'other_user': other_user,
            'last_message': last_message
        }
        
        if last_message is None:
            new_matches.append(chat_info)
        else:
            active_chats.append(chat_info)
            
    # Ordenar active_chats pela última mensagem (mais recente primeiro)
    active_chats.sort(key=lambda x: x['last_message'].timestamp, reverse=True)
    
    return render(request, 'chats.html', {
        'new_matches': new_matches,
        'active_chats': active_chats
    })

@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    
    # Segurança: Apenas participantes podem acessar a sala
    if request.user != room.user1 and request.user != room.user2:
        messages.error(request, 'Você não tem permissão para acessar este chat.')
        return redirect('dashboard')
        
    other_user = room.get_other_user(request.user)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(room=room, sender=request.user, content=content)
            # Para o MVP simples via HTTP POST, vamos apenas recarregar a página para ver a nova mensagem
            return redirect('chat_room', room_id=room.id)
            
    # Mensagens enviadas para esta sala
    room_messages = room.messages.all()
    
    return render(request, 'chat_room.html', {
        'room': room,
        'other_user': other_user,
        'messages': room_messages
    })
