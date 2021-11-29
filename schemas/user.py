from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    username = fields.Str(validate=validate.Length(min=3), required=True)

class UserRegisterSchema(UserSchema):
    name = fields.Str(validate=validate.Length(min=3), required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserLoginSchema(UserSchema):
    password = fields.Str(required=True)
