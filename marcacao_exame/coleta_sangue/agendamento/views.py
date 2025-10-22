from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from django.core.paginator import Paginator
from django.conf import settings
from threading import Thread
from datetime import datetime
from .models import Agendamento

# Horários fixos disponíveis
HORARIOS_FIXOS = [
    "07:30", "08:00", "09:00", "10:00", "11:00",
    "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"
]

# =========================
# Função auxiliar: envio assíncrono de e-mail
# =========================
def send_email_async(subject, html_content, to_email):
    def _send():
        msg = EmailMultiAlternatives(subject, "", settings.DEFAULT_FROM_EMAIL, [to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    Thread(target=_send).start()

# =========================
# Home
# =========================
def home(request):
    return render(request, "home.html")

# =========================
# Agendamento
# =========================
def agendar(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        telefone = request.POST.get("telefone")
        data = request.POST.get("data")
        hora = request.POST.get("hora")
        doador = request.POST.get("doador") == "True"

        # Validação de agendamento único por mês
        try:
            data_obj = datetime.strptime(data, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "Data inválida."})

        inicio_mes = data_obj.replace(day=1)
        fim_mes = (inicio_mes.replace(month=inicio_mes.month + 1) 
                   if inicio_mes.month < 12 
                   else inicio_mes.replace(year=inicio_mes.year + 1, month=1))

        if Agendamento.objects.filter(email=email, data__gte=inicio_mes, data__lt=fim_mes).exists():
            return JsonResponse({"error": "Você já possui um agendamento neste mês."})

        # Verificar limite de 10 pessoas por hora
        if Agendamento.objects.filter(data=data, hora=hora).count() >= 10:
            return JsonResponse({"error": "Esse horário já está cheio!"})

        # Criar agendamento
        agendamento = Agendamento.objects.create(
            nome=nome,
            email=email,
            telefone=telefone,
            data=data,
            hora=hora,
            doador=doador
        )

        # Enviar e-mail assíncrono
        subject = "Confirmação de Agendamento - Coleta de Sangue"
        html_content = render_to_string("emails/confirmacao.html", {
            "nome": nome,
            "data": data,
            "hora": hora,
            "doador": "Sim" if doador else "Não",
        })
        send_email_async(subject, html_content, email)

        return JsonResponse({
            "success": "Agendamento realizado com sucesso! Um e-mail de confirmação foi enviado."
        })

    return render(request, "agendar.html")

# =========================
# Horários disponíveis (AJAX)
# =========================
def horarios_disponiveis_ajax(request, data):
    agendamentos = (
        Agendamento.objects.filter(data=data)
        .values("hora")
        .annotate(qtd=Count("id"))
    )
    ocupados = {item["hora"].strftime("%H:%M"): item["qtd"] for item in agendamentos}
    disponiveis = [
        {"hora": h, "vagas": max(0, 10 - ocupados.get(h, 0))}
        for h in HORARIOS_FIXOS
        if max(0, 10 - ocupados.get(h, 0)) > 0
    ]
    return JsonResponse(disponiveis, safe=False)

# =========================
# Login e Logout
# =========================
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

# =========================
# Dashboard (com paginação)
# =========================
@login_required
def dashboard(request):
    data_filtro = request.GET.get("data")
    if data_filtro:
        queryset = Agendamento.objects.filter(data=data_filtro).order_by("hora")
    else:
        queryset = Agendamento.objects.all().order_by("data", "hora")

    paginator = Paginator(queryset, 20)  # 20 agendamentos por página
    page_number = request.GET.get("page")
    agendamentos = paginator.get_page(page_number)

    return render(request, "dashboard.html", {
        "agendamentos": agendamentos,
        "data_filtro": data_filtro
    })
