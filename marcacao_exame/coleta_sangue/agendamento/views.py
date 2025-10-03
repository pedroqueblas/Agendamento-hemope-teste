from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Agendamento
from django.conf import settings

# Horários fixos
HORARIOS_FIXOS = ["07:30", "08:00", "09:00", "10:00", "11:00",
                  "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]

def home(request):
    return render(request, "home.html")

def agendar(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        telefone = request.POST.get("telefone")
        data = request.POST.get("data")
        hora = request.POST.get("hora")
        doador = request.POST.get("doador") == "True"

        # Verificar limite de 10 pessoas por hora
        count = Agendamento.objects.filter(data=data, hora=hora).count()
        if count >= 10:
            return JsonResponse({"error": "Esse horário já está cheio!"})

        agendamento = Agendamento.objects.create(
            nome=nome, email=email, telefone=telefone, data=data, hora=hora, doador=doador
        )

        # Enviar e-mail de confirmação
        subject = "Confirmação de Agendamento - Coleta de Sangue"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [email]
        html_content = render_to_string("emails/confirmacao.html", {
            "nome": nome,
            "data": data,
            "hora": hora,
            "doador": "Sim" if doador else "Não",
        })
        msg = EmailMultiAlternatives(subject, "", from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        return JsonResponse({"success": "Agendamento realizado com sucesso! Um e-mail de confirmação foi enviado."})

    return render(request, "agendar.html")

def horarios_disponiveis_ajax(request, data):
    disponiveis = []
    for h in HORARIOS_FIXOS:
        count = Agendamento.objects.filter(data=data, hora=h).count()
        vagas = max(0, 10 - count)
        if vagas > 0:
            disponiveis.append({"hora": h, "vagas": vagas})
    return JsonResponse(disponiveis, safe=False)

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "login.html", {"error": "Usuário ou senha inválidos"})
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def dashboard(request):
    data_filtro = request.GET.get("data")
    if data_filtro:
        agendamentos = Agendamento.objects.filter(data=data_filtro).order_by("hora")
    else:
        agendamentos = Agendamento.objects.all().order_by("data", "hora")
    return render(request, "dashboard.html", {
        "agendamentos": agendamentos,
        "data_filtro": data_filtro
    })
