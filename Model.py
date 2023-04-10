import uuid
from flask import Flask
from marshmallow import Schema, fields, pre_load, validate
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, LargeBinary
ma = Marshmallow()
db = SQLAlchemy()

class Token(db.Model):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    doctor_id = Column(Integer, nullable=False)
    token = Column(String(50), unique=True, default=str(uuid.uuid4()), nullable=False)
    public_key_patient = Column(String(256), nullable=False)
    public_key_doctor = Column(String(256), nullable=False)
    key_frag = Column(String(512), nullable=False)
    link = Column(String(128), nullable=False)

class TokenSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    doctor_id = fields.Integer(required=True)
    token = fields.String(dump_only=True)
    public_key_patient = fields.String(required=True)
    public_key_doctor = fields.String(required=True)
    key_frag = fields.String(required=True)
    link = fields.String(required=True)
