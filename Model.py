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
    public_key_patient = Column(Integer, nullable=False)
    public_key_doctor = Column(Integer, nullable=False)
    key_frag = Column(LargeBinary(length=256))
    link = Column(String(128), nullable=False)

class TokenSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    doctor_id = Column(Integer, nullable=False)
    token = fields.String()
    public_key_patient = fields.Integer(required=True)
    public_key_doctor = fields.Integer(required=True)
    key_frag = fields.String(required=True, validate=validate.Length(1))
    link = fields.String(required=True, validate=validate.Length(1))
