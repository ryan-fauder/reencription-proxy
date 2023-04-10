from flask import request, jsonify
from flask_restful import Resource
from Model import Token, TokenSchema
import json

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

        if result['doctor_id'] == int(doctor_id):
            return json.dumps({'message': 'Access granted!', 'data': result}), 200
        else:
            return json.dumps({'message': 'Invalid token!'}), 401