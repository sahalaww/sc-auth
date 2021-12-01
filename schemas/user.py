import uuid
from marshmallow import Schema, fields, validate
from main import app

class UserSchema(Schema):
    username = fields.Str(validate=validate.Length(min=3), required=True)

class UserRegisterSchema(UserSchema):
    name = fields.Str(validate=validate.Length(min=3), required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserLoginSchema(UserSchema):
    password = fields.Str(required=True)

class UserRegisterAdminSchema(UserRegisterSchema):
   role_name = fields.Str(required=True)

class UsersResponse(Schema):
    uuid = fields.Str()
    name = fields.Str()
    username = fields.Str()
    email = fields.Email()
    role_id = fields.Int()

class UserUpdateSchema(Schema):
    uuid = fields.Str(required=True)
    name = fields.Str()
    password = fields.Str()