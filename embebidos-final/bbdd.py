from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource

db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lockers.db'
    db.init_app(app)
    with app.app_context():
        db.create_all()


class LockerListResource(Resource):
    def post(self):
        new_locker1 = Locker()
        new_locker2 = Locker()
        new_locker3 = Locker()
        db.session.add(new_locker1)
        db.session.add(new_locker2)
        db.session.add(new_locker3)
        db.session.commit()
        return {"message": "3 lockers created"}, 201

class Locker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ocupado = db.Column(db.Boolean, default=False)
    cerrado = db.Column(db.Boolean, default=True)
    hora_ocupacion = db.Column(db.DateTime, nullable=True)
    hora_desocupacion = db.Column(db.DateTime, nullable=True)
    rut = db.Column(db.String(10), nullable=True)
    disponible = db.Column(db.Boolean, default=True)
    documento_notif = db.Column(db.Boolean, default=False)
    puerta_abierta_notif = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "ocupado": self.ocupado,
            "cerrado": self.cerrado,
            "hora_ocupacion": self.hora_ocupacion.isoformat() if self.hora_ocupacion else None,
            "hora_desocupacion": self.hora_desocupacion.isoformat() if self.hora_desocupacion else None,
            "rut": self.rut,
            "disponible": self.disponible,
            "documento_notif": self.documento_notif,
            "puerta_abierta_notif": self.puerta_abierta_notif
        }
