from flask import request, jsonify
from flask_restful import Resource
from models.auth import Auth, AuthSchema
from models.record import *
import json

from encryption import *
from umbral import *

import ipfs
import os
import jwt
import uuid

auth_schema = AuthSchema()

class RecordResource(Resource):
    def post(self):
        data = request.get_json(force=True)

        token = request.headers.get('Authorization').replace('Bearer ', '')
        try:
            payload = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401

        auth_instance = Auth.query.filter_by(access_token=payload["access_token"]).first()
        if auth_instance == None:
            return json.dumps({'message': 'Invalid token!'}), 404

        auth = auth_instance.to_deserialize()
        print("Auth decodificado")

        # Decodificar o Link
        serialized_record = ipfs.get(auth["bundle_hash"])
        record = deserializeRecord(serialized_record)

        print("Cifra e capsula obtidas do IPFS")
        cfrags = get_cfrags(
            auth["public_key_signer_patient"], auth["public_key_patient"], auth["public_key_doctor"],
            record["capsule"], kfrags=auth["key_frag"]
        )

        response = {
            'public_key_patient': auth["public_key_patient"],
            'cfrags': serializeListFrom(cfrags),
            **serialized_record
        }
        return json.dumps(response)