from main import db
from sqlalchemy.sql import func

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    
    def __repr__(self):
        return '<Role {}>'.format(self.name)
    
    @staticmethod
    def generate_default_roles():
        role1 = Role(name = 'Admin')
        role2 = Role(name = 'User')
        db.session.add(role1)
        db.session.add(role2)
        try:
            db.session.commit()
        except:
            db.session.rollback()