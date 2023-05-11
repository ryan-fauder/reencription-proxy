from flask import Flask
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, LargeBinary
from datetime import datetime, timedelta

import jwt
import os

ma = Marshmallow()
db = SQLAlchemy()

class Auth(db.Model):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    doctor_id = Column(Integer, nullable=False)
    jwt = Column(String(1024), unique=True, nullable=False)
    public_key_patient = Column(String(256), nullable=False)
    public_key_signer_patient = Column(String(256), nullable=False)
    public_key_doctor = Column(String(256), nullable=False)
    key_frag = Column(String(1024), nullable=False)
    bundle_hash = Column(String(128), nullable=False)

    def __init__(self, doctor_id, public_key_patient, public_key_signer_patient, public_key_doctor, key_frag, bundle_hash, access_token):
        self.doctor_id = doctor_id
        self.public_key_patient = public_key_patient
        self.public_key_signer_patient = public_key_signer_patient
        self.public_key_doctor = public_key_doctor
        self.key_frag = key_frag
        self.bundle_hash = bundle_hash
        self.access_token = access_token 

    def __repr__(self):
           return f"<Auth(doctor_id='{self.doctor_id}', token='{self.token}')>"
    
    @property
    def to_deserialize(self):
        return {
            "doctor_id": self.doctor_id,
            "public_key_patient": PublicKey.from_bytes(deserializeFrom(self.public_key_patient)),
            "public_key_signer_patient": PublicKey.from_bytes(deserializeFrom(self.public_key_signer_patient)),
            "public_key_doctor": PublicKey.from_bytes(deserializeFrom(self.public_key_doctor)),
            "key_frag": deserializeListFrom(VerifiedKeyFrag.from_verified_bytes, self.key_frag),
            "bundle_hash": self.bundle_hash
        }

class AuthSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    doctor_id = fields.Integer(required=True)
    token = fields.String(dump_only=True)
    public_key_patient = fields.String(required=True)
    public_key_signer_patient = fields.String(required=True)
    public_key_doctor = fields.String(required=True)
    key_frag = fields.String(required=True)
    bundle_hash = fields.String(required=True)
