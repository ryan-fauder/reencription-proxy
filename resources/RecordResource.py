from flask import request, jsonify
from flask_restful import Resource
from Model import Token, TokenSchema
import json
import encryption
import ipfs
token_schema = TokenSchema()

class RecordResource(Resource):
    def post(self):
        data = request.get_json(force=True)
        doctor_id = data['doctor_id']
        token = data['token']
        doctor_token = Token.query.filter_by(token=token).first()

        if doctor_token == None:
            return json.dumps({'message': 'Invalid token!'}), 404

        result = token_schema.dump(doctor_token)

        if result['doctor_id'] != int(doctor_id):
            return json.dumps({'message': 'Invalid token!'}), 401

        public_key_patient = encryption.decode_publicKey(result["public_key_patient"])
        public_key_signer_patient = encryption.decode_publicKey(result["public_key_signer_patient"])
        public_key_doctor = encryption.decode_publicKey(result["public_key_doctor"])
        key_frag = encryption.decode_kfrags(result["key_frag"])
        print("Token decodificado")
        

        # Decodificar o LInk
        ipfs_obj = ipfs.get(result["link"])
        capsule = encryption.decode_capsule(ipfs_obj['capsule'])
        ciphertext = encryption.decode_cipher(ipfs_obj['content'])
        print("Cifra e capsula obtidas do IPFS")

        cfrags = encryption.get_cfrags(public_key_signer_patient, public_key_patient, public_key_doctor, capsule, kfrags=key_frag)
        print(cfrags)
        record = {
            'public_key_patient': result["public_key_patient"],
            'capsule': ipfs_obj['capsule'],
            'cfrags': encryption.encode_bytes(bytes(cfrags[0])),
            'ciphertext': ipfs_obj['content']
        }
        print(record.keys())
        return json.dumps({'message': 'Access granted!', 'data': record})