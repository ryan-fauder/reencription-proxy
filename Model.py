import uuid
from flask import Flask
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, LargeBinary
import jwt
from datetime import datetime, timedelta
import os

ma = Marshmallow()
db = SQLAlchemy()

class Token(db.Model):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    doctor_id = Column(Integer, nullable=False)
    token = Column(String(1024), unique=True, nullable=False)
    public_key_patient = Column(String(256), nullable=False)
    public_key_signer_patient = Column(String(256), nullable=False)
    public_key_doctor = Column(String(256), nullable=False)
    key_frag = Column(String(1024), nullable=False)
    link = Column(String(128), nullable=False)

    def __init__(self, doctor_id, public_key_patient, public_key_signer_patient, public_key_doctor, key_frag, link):
        self.doctor_id = doctor_id 
        self.public_key_patient = public_key_patient
        self.public_key_signer_patient = public_key_signer_patient
        self.public_key_doctor = public_key_doctor 
        self.key_frag = key_frag 
        self.link = link 
        self.token = jwt.encode({'doctor_id': doctor_id, 'exp': datetime.utcnow() + timedelta(minutes=60)}, os.environ['SECRET_KEY'])

    def __repr__(self):
           return f"<Token(doctor_id='{self.doctor_id}', token='{self.token}')>"

class TokenSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    doctor_id = fields.Integer(required=True)
    token = fields.String(dump_only=True)
    public_key_patient = fields.String(required=True)
    public_key_signer_patient = fields.String(required=True)
    public_key_doctor = fields.String(required=True)
    key_frag = fields.String(required=True)
    link = fields.String(required=True)
