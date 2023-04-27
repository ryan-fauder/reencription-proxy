from flask import request, jsonify
from flask_restful import Resource
from Model import db, Token, TokenSchema
from marshmallow import ValidationError

import json
import uuid
import jwt

tokens_schema = TokenSchema(many=True)
token_schema = TokenSchema()

class TokenResource(Resource):
    def get(self):
        tokens = Token.query.all()
        tokens = tokens_schema.dump(tokens)
        return tokens, 200

    def post(self):
        json_data = request.get_json(force=True)
        data = token_schema.load(json_data)

        token = Token(
            doctor_id=data['doctor_id'],
            public_key_patient=data['public_key_patient'],
            public_key_signer_patient=data['public_key_signer_patient'], 
            public_key_doctor=data['public_key_doctor'],
            key_frag=data['key_frag'],
            link=data['link']
        )

        db.session.add(token)
        db.session.commit()
        generated_token = token_schema.dump(token)['token']

        return json.dumps({ 'message': 'Tokens generated and sent successfully!', 'data': generated_token}), 201
