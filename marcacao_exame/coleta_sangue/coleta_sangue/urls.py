from django.urls import path
from agendamento import views

urlpatterns = [
    path('', views.home, name="home"),
    path('agendar/', views.agendar, name="agendar"),
    path('horarios/<str:data>/', views.horarios_disponiveis_ajax, name="horariosFixo"),
    path('login/', views.login_view, name="login"),
    path('logout/', views.logout_view, name="logout"),
    path('dashboard/', views.dashboard, name="dashboard"),
]
