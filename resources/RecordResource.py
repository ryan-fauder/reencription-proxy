from flask import request, jsonify
from flask_restful import Resource
from Model import Token, TokenSchema
import json
from encryption import *
from umbral import *
import ipfs
import os
import jwt

token_schema = TokenSchema()

class RecordResource(Resource):
    def post(self):
        data = request.get_json(force=True)
        doctor_id = data['doctor_id']

        token = request.headers.get('Authorization').replace('Bearer ', '')
        try:
            payload = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=['HS256'])
            print(payload)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token inválido'}), 401


        doctor_token = Token.query.filter_by(token=token).first()
        if doctor_token == None:
            return json.dumps({'message': 'Invalid token!'}), 404

        result = token_schema.dump(doctor_token)
        if result['doctor_id'] != int(doctor_id):
            return json.dumps({'message': 'Invalid token!'}), 401

        public_key_patient = PublicKey.from_bytes(deserializeFrom(result["public_key_patient"]))
        public_key_signer_patient = PublicKey.from_bytes(deserializeFrom(result["public_key_signer_patient"]))
        public_key_doctor = PublicKey.from_bytes(deserializeFrom(result["public_key_doctor"]))
        key_frag = deserializeListFrom(VerifiedKeyFrag.from_verified_bytes, result["key_frag"])
        print("Token decodificado")

        # Decodificar o Link
        ipfs_response = ipfs.get(result["link"])
        print(ipfs_response.keys())
        capsule = Capsule.from_bytes(deserializeFrom(ipfs_response["capsule"]))
        ciphertext = deserializeFrom(ipfs_response["content"])

        print("Cifra e capsula obtidas do IPFS")
        cfrags = get_cfrags(
            public_key_signer_patient, public_key_patient, public_key_doctor,
            capsule, kfrags=key_frag
        )
        record = {
            'public_key_patient': result["public_key_patient"],
            'capsule': ipfs_response['capsule'],
            'cfrags': serializeListFrom(cfrags),
            'ciphertext': ipfs_response['content']
        }
        return json.dumps({'message': 'Access granted!', 'data': record})