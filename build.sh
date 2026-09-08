#!/usr/bin/env bash
# Script de build usado pelo Render (buildCommand).
# Sai imediatamente se qualquer comando falhar.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Cria os usuários de acesso ao sistema a partir de variáveis de ambiente
# (USUARIO_1_NOME/USUARIO_1_SENHA, USUARIO_2_NOME/USUARIO_2_SENHA), se
# definidas. Não falha o build se as variáveis não existirem ou se os
# usuários já tiverem sido criados em um deploy anterior.
python manage.py criar_usuarios_producao
