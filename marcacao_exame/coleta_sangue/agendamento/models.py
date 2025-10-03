from django.db import models
from django.core.exceptions import ValidationError
import datetime


def validate_horario(value):
    """Valida se o horário está entre 07:30 e 17:00."""
    inicio = datetime.time(7, 30)
    fim = datetime.time(17, 0)
    if not (inicio <= value <= fim):
        raise ValidationError("O horário deve estar entre 07:30 e 17:00.")


class Agendamento(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    data = models.DateField()
    hora = models.TimeField(validators=[validate_horario])  # ⬅️ restrição aplicada
    doador = models.BooleanField(default=False)  # novo campo para saber se é doador
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data', 'hora']

    def __str__(self):
        doador_status = "Doador" if self.doador else "Não Doador"
        return f"{self.nome} - {self.data} {self.hora} ({doador_status})"
