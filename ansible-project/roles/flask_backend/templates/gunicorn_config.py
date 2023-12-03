# ansible-project/roles/flask_backend/templates/gunicorn_config.py
bind = "0.0.0.0:80"
workers = 4
preload_app = True