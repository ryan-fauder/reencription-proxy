from flask import request
from flask_restful import Resource
from Model import db, Token, TokenSchema

import json
import uuid

tokens_schema = TokenSchema(many=True)
token_schema = TokenSchema()

class TokenResource(Resource):
    def get(self):
        tokens = Token.query.all()
        tokens = tokens_schema.dump(tokens).data
        return tokens, 200
    def get(self, token):
        data = request.get_json()
        doctor_id = data['doctor_id']
        doctor_token = Token.query.filter_by(token=token).first()
        if doctor_token.doctor_id == doctor_id:
            return jsonify({'message': 'Access granted!'}), 200
        else:
            return jsonify({'message': 'Invalid token!'}), 401
    def post(self):
        json_data = request.get_json(force=True)
        data, errors = token_schema.load(json_data)
        if errors:
            return errors, 422

        token = Token(
            doctor_id=json_data['doctor_id'],
            public_key_patient=json_data['public_key_patient'], 
            public_key_doctor=json_data['public_key_doctor'], 
            key_frag=json_data['key_frag'], 
            link=json_data['link']
        )
        db.session.add(token)
        db.session.commit()

        result = token_schema.dump(token).data

        return jsonify({ 'message': 'Tokens generated and sent successfully!', 'token': result }), 201