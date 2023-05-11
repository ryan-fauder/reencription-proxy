from flask import request, jsonify
from flask_restful import Resource
from models.auth import db, Auth, AuthSchema
from marshmallow import ValidationError

import json
import uuid
import jwt

auths_schema = AuthSchema(many=True)
auth_schema = AuthSchema()

class AuthResource(Resource):
    def get(self):
        auths = Auth.query.all()
        auths = auths_schema.dump(auths)
        return auths, 200

    def post(self):
        json_data = request.get_json(force=True)
        data = auth_schema.load(json_data)
        access_token = uuid.uuid4()

        auth = Auth(
            doctor_id=data['doctor_id'],
            public_key_patient=data['public_key_patient'],
            public_key_signer_patient=data['public_key_signer_patient'], 
            public_key_doctor=data['public_key_doctor'],
            key_frag=data['key_frag'],
            bundle_hash=data['link'],
            access_token=access_token
        )

        db.session.add(auth)
        db.session.commit()
        jwt_token = jwt.encode({'access_token': access_token, 'exp': datetime.utcnow() + timedelta(minutes=60)}, os.environ['SECRET_KEY'])

        return json.dumps({ 'message': 'Tokens generated and sent successfully!', 'token': jwt_token}), 201
