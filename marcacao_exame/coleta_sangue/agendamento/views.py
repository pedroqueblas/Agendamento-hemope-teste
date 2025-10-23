import secrets
from datetime import datetime
from threading import Thread
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from django.core.paginator import Paginator
from django.conf import settings
from .models import Agendamento

HORARIOS_FIXOS = settings.APPOINTMENT_TIMES

# ----------------------------
# Função para envio assíncrono de e-mail
# ----------------------------
def send_email_async(subject, html_content, to_email):
    def _send():
        msg = EmailMultiAlternatives(subject, "", settings.DEFAULT_FROM_EMAIL, [to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    Thread(target=_send).start()

# ----------------------------
# Home
# ----------------------------
def home(request):
    return render(request, "home.html")

# ----------------------------
# Agendamento
# ----------------------------
def agendar(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        telefone = request.POST.get("telefone")
        data = request.POST.get("data")
        hora_str = request.POST.get("hora")
        doador = request.POST.get("doador") == "True"

        # Validar data
        try:
            data_obj = datetime.strptime(data, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"error": "Data inválida."})

        # Validar hora
        try:
            hora_obj = datetime.strptime(hora_str, "%H:%M").time()
        except ValueError:
            return JsonResponse({"error": "Hora inválida."})

        # Limite agendamento único por mês
        inicio_mes = data_obj.replace(day=1)
        fim_mes = (inicio_mes.replace(month=inicio_mes.month + 1)
                   if inicio_mes.month < 12
                   else inicio_mes.replace(year=inicio_mes.year + 1, month=1))
        if Agendamento.objects.filter(email=email, data__gte=inicio_mes, data__lt=fim_mes).exists():
            return JsonResponse({"error": "Você já possui um agendamento neste mês."})

        # Limite 10 pessoas por hora
        if Agendamento.objects.filter(data=data_obj, hora=hora_obj).count() >= 10:
            return JsonResponse({"error": "Esse horário já está cheio!"})

        # Criar token
        token = secrets.token_urlsafe(16)

        # Criar agendamento
        agendamento = Agendamento.objects.create(
            nome=nome,
            email=email,
            telefone=telefone,
            data=data_obj,
            hora=hora_obj,
            doador=doador,
            token_cancelamento=token
        )

        # Enviar e-mail
        subject = "Confirmação de Agendamento - Coleta de Sangue"
        html_content = render_to_string("emails/confirmacao.html", {
            "nome": nome,
            "data": data,
            "hora": hora_str,
            "doador": "Sim" if doador else "Não",
            "link_cancelamento": request.build_absolute_uri(f"/cancelar/{token}/")
        })
        send_email_async(subject, html_content, email)

        return JsonResponse({"success": "Agendamento realizado com sucesso! Um e-mail de confirmação foi enviado."})

    return render(request, "agendar.html")

# ----------------------------
# Horários disponíveis (AJAX)
# ----------------------------
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

# ----------------------------
# Login e Logout
# ----------------------------
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

# ----------------------------
# Dashboard (com paginação)
# ----------------------------
@login_required
def dashboard(request):
    data_filtro = request.GET.get("data")
    if data_filtro:
        queryset = Agendamento.objects.filter(data=data_filtro).order_by("hora")
    else:
        queryset = Agendamento.objects.all().order_by("data", "hora")

    paginator = Paginator(queryset, 20)
    page_number = request.GET.get("page")
    agendamentos = paginator.get_page(page_number)

    return render(request, "dashboard.html", {
        "agendamentos": agendamentos,
        "data_filtro": data_filtro
    })

# ----------------------------
# Cancelamento via link do e-mail
# ----------------------------
def cancelar_agendamento(request, token):
    agendamento = get_object_or_404(Agendamento, token_cancelamento=token)
    if request.method == "POST":
        if not agendamento.cancelado:
            agendamento.cancelado = True
            agendamento.save()
            messages.success(request, "Agendamento cancelado com sucesso.")
        else:
            messages.warning(request, "Este agendamento já foi cancelado.")
        return redirect("home")
    return render(request, "cancelar.html", {"agendamento": agendamento})

# ----------------------------
# Cancelamento via dashboard
# ----------------------------
@login_required
def cancelar_dashboard(request, agendamento_id):
    agendamento = get_object_or_404(Agendamento, id=agendamento_id)
    if not agendamento.cancelado:
        agendamento.cancelado = True
        agendamento.save()
        messages.success(request, "Agendamento cancelado com sucesso.")
    else:
        messages.warning(request, "Este agendamento já foi cancelado.")
    return redirect("dashboard")
