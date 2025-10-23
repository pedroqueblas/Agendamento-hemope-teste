# Agendamento HEMOPE - Documentação do Projeto
# Sistema web desenvolvido para facilitar o agendamento de coletas de sangue e exames no HEMOPE. O projeto permite que usuários realizem agendamentos de forma prática e segura, controlando datas, horários e evitando duplicidade de registros.
# Funcionalidades
•	Agendamento de exames e coletas de sangue
•	Validação de horários disponíveis (entre 07:30 e 17:00)
•	Envio de confirmação por e-mail (quando configurado)
•	Painel administrativo para controle de agendamentos
•	Bloqueio de múltiplos agendamentos com o mesmo e-mail
•	Interface simples e intuitiva, com layout responsivo
•	Controle de datas, evitando agendamentos duplicados ou em dias inválidos
Tecnologias Utilizadas
Backend: Python, Django
Frontend: HTML, CSS, JavaScript
Banco de Dados: SQLite (padrão Django, podendo ser trocado por PostgreSQL)
Outras: Django Email System, Bootstrap / CSS customizado
Estrutura do Projeto

Agendamento-hemope-teste/
│
├── marcacao_exame/
│   ├── coleta_sangue/
│   │   ├── templates/
│   │   ├── static/
│   │   ├── views.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── forms.py
│   │
│   ├── marcacao_exame/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│
├── db.sqlite3
├── manage.py
└── README.md

# Como Executar o Projeto
# 1️⃣ Clonar o Repositório:
git clone https://github.com/pedroqueblas/Agendamento-hemope-teste.git
cd Agendamento-hemope-teste/marcacao_exame
# 2️⃣ Criar Ambiente Virtual:
python -m venv venv
venv\Scripts\activate (Windows)
source venv/bin/activate (Linux/Mac)
# 3️⃣ Instalar Dependências:
 pip install -r requirements.txt
4️⃣ Aplicar Migrações:
 python manage.py makemigrations
 python manage.py migrate
# 5️⃣ Executar o Servidor:
 python manage.py runserver
Acesse http://127.0.0.1:8000/
Configurações de E-mail (Opcional)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'seuemail@gmail.com'
EMAIL_HOST_PASSWORD = 'suasenha'

# Use variáveis de ambiente (.env) para proteger suas credenciais.
Melhorias Futuras
•	Sistema de autenticação para administradores e usuários
•	Painel para reagendar ou cancelar consultas
•	Envio de lembrete automático (e-mail ou WhatsApp)
•	Migração para PostgreSQL
•	Interface aprimorada com TailwindCSS
•	Implementar testes automatizados (Pytest)
•	Dashboard de estatísticas
Autor
Pedro Queblas - Estudante de Sistemas de Informação | Desenvolvedor Front-End & Back-End
GitHub: https://github.com/pedroqueblas
Projeto criado com propósito educativo e social para facilitar o processo de agendamento de doação de sangue e exames no HEMOPE.
