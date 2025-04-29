import os
from datetime import datetime, timedelta
from math import trunc

import jwt
from flask import Flask, request, jsonify
from jwt.api_jws import decode
from pyexpat.errors import messages

from database import products

SECRET_KEY = os.getenv("SECRET_KEY", "quai")

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    dados = request.get_json()
    if not dados:
        return jsonify(message="Dados n fornecidos?"), 400
    if "username" not in dados or "password" not in dados:
        return jsonify(message="Campos 'username' e 'password' n foram prenchidos"), 400
    if dados['username'] == 'cleiton' and dados['password'] == 'rlteofin':
        token = jwt.encode(
            {"user": dados['username'], "exp": datetime.utcnow() + timedelta(minutes=30)},
            SECRET_KEY,
            algorithm="HS256"
        )

        return jsonify(token)

    return jsonify(message="Deu certo parabens!"), 401

@app.route('/products', methods=["GET"])
def protected():

    header = request.headers.get("Authorization")
    if not header:
        return jsonify(message="É necessario o token!"), 403

    par = header.split()
    if par[0].lower() != 'bearer' or len(par) !=2:
        return jsonify(message="Cabeçalho ruim!"), 401
    token = par[1]

    try:
        decod = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return produtos()
    except jwt.ExpiredSignatureError:
        return jsonify(message="Token expirado! Faça login novamente."), 401
    except jwt.InvalidTokenError:
        return jsonify(message="Token invalido!"), 403

def produtos():
    preco_asc = request.args.get('preco_asc')
    preco_desc = request.args.get('preco_desc')
    description_part = request.args.get('description_part')
    produto = products

    if preco_asc:
        list_asc =sorted(products,key=lambda x: x['product_price'])
        return jsonify(list_asc)

    if preco_desc:
        list_desc = sorted(products,key=lambda x: x['product_price'], reverse=True)
        return jsonify(list_desc)

    if description_part:
        description_part.lower()
        produto = [i for i in products if description_part in i['product_description'].lower()]
        return jsonify(produto)


    return jsonify(products)

@app.route('/products/<int:product_id>', methods=["GET"])
def produto_id(product_id):

    produto = [i for i in products if product_id == i['id']]
    return jsonify(produto)


if __name__ == '__main__':
    app.run(debug=True)