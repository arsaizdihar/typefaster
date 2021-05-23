from flask import Blueprint, request, jsonify
from http import HTTPStatus
from models import db, User
from flask_jwt_extended import create_access_token, jwt_required, current_user, create_refresh_token
from flask_cors import cross_origin
import re
import requests
import random

api = Blueprint('api', __name__)
with open("api/words.txt", "r") as file:
    words = file.read().split()


@api.route('auth/sign-up', methods=['POST'])
@cross_origin()
def sign_up():
    data = request.json
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return {'error': 'Invalid data input'}, HTTPStatus.BAD_REQUEST
    username = data.get('username')
    if User.query.filter_by(name=username).first():
        return {'error': 'Username already used. Please try another.'}, HTTPStatus.BAD_REQUEST
    email = data.get('email')
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        return {'error': 'Invalid Email'}, HTTPStatus.BAD_REQUEST
    if User.query.filter_by(email=email).first():
        return {'error': 'Email already used.'}, HTTPStatus.BAD_REQUEST
    password = data.get('password')
    if len(password) < 3:
        return {'error': 'Password is too short.'}, HTTPStatus.BAD_REQUEST
    new_user = User(username, email, password)
    access_token = create_access_token(identity=new_user)
    refresh_token = create_refresh_token(identity=new_user)
    response = jsonify(
        {'success': 'User created', 'access_token': access_token, 'refresh_token': refresh_token})
    db.session.add(new_user)
    db.session.commit()
    return response, HTTPStatus.OK


@api.route('auth/login', methods=['POST'])
@cross_origin()
def login():
    data = request.json
    if 'email' not in data or 'password' not in data:
        return {'error': 'Invalid Log in'}, HTTPStatus.BAD_REQUEST
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not user.check_password(data.get('password')):
        return {'error': 'Email or password is wrong.'}, HTTPStatus.UNAUTHORIZED
    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)
    response = jsonify(success='login success',
                       access_token=access_token, refresh_token=refresh_token)
    return response, HTTPStatus.OK


@api.route('auth/get-user')
@cross_origin()
@jwt_required()
def get_user_data():
    return jsonify(username=current_user.name, email=current_user.email), HTTPStatus.OK


@api.route("auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
@cross_origin()
def refresh():
    access_token = create_access_token(identity=current_user)
    return jsonify(access_token=access_token)


@api.route("/random-words/<int:num>")
@jwt_required()
@cross_origin()
def random_words(num):
    return jsonify(random.choices(words, k=num))
