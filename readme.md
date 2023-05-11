# Proxy
- Identificar partes necessárias do SC.
- Buscar biblioteca python para ipfs
- Alterar para jwt

- Questões
-- [] Onde deve ser armazenado o id?

import requests

url = 'http://localhost:5000/protected'
headers = {'Authorization': 'Bearer <token>'}
response = requests.get(url, headers=headers)


import jwt
from datetime import datetime, timedelta
from flask import Flask, jsonify, request

app = Flask(__name__)

# Definindo a chave secreta para assinar o token JWT
app.config['SECRET_KEY'] = 'mysecretkey'

# Criando uma rota para gerar o token JWT
@app.route('/generate_token')
def generate_token():
    # Definindo o payload do token JWT
    payload = {
        'sub': '1234567890',
        'name': 'John Doe',
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=30)
    }

    # Gerando o token JWT
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

    # Retornando o token no header da resposta
    return jsonify({'token': token.decode('UTF-8')}), 200, {'Authorization': 'Bearer ' + token.decode('UTF-8')}

# Criando uma rota protegida que precisa do token JWT no header da requisição
@app.route('/protected')
def protected():
    # Pegando o token JWT do header da requisição
    token = request.headers.get('Authorization').replace('Bearer ', '')

    # Decodificando o token JWT
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Token inválido'}), 401

    # Retornando o payload do token JWT
    return jsonify({'payload': payload}), 200

if __name__ == '__main__':
    app.run(debug=True)
