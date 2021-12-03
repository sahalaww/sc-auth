from main import db
from sqlalchemy.sql import func
from models.roles import Role
from werkzeug.security import generate_password_hash
import uuid

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password = db.Column(db.String(254))
    name = db.Column(db.String(125))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    roles = db.relationship("Role", backref=db.backref("roles", uselist=False))
   
    def __repr__(self):
        return '<User {}>'.format(self.username)

    @staticmethod
    def generate_default_users():
        admin_role = Role.query.filter_by(name='Admin').first().id
        user_role = Role.query.filter_by(name='User').first().id

        create_user1 = User(
            name='admin',
            uuid=uuid.uuid4().hex,
            username='admin',
            email='admin@email.com',
            password=generate_password_hash('pass1234'),
            role_id=admin_role
        )
        create_user2 = User(
            name='userman',
            uuid=uuid.uuid4().hex,
            username='userman',
            email='userman@email.com',
            password=generate_password_hash('pass1234'),
            role_id=user_role
        )
        db.session.add(create_user1)
        db.session.add(create_user2)

        try:
            db.session.commit()
        except:
            db.session.rollback()