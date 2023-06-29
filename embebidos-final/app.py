from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse
from datetime import datetime
from bbdd import init_db, db, Locker, LockerListResource

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lockers.db'
init_db(app)
api = Api(app)



parser = reqparse.RequestParser()
parser.add_argument('ocupado', type=bool)
parser.add_argument('cerrado', type=bool)
parser.add_argument('hora_ocupacion', type=str)
parser.add_argument('hora_desocupacion', type=str)
parser.add_argument('rut', type=str)
parser.add_argument('disponible', type=bool)
parser.add_argument('documento_notif', type=bool)
parser.add_argument('puerta_abierta_notif', type=bool)

class LockerResource(Resource):
    def get(self, locker_id):
        locker = db.session.query(Locker).get(locker_id)
        if locker is None:
            return {'error': 'Locker not found'}, 404
        return locker.to_dict()  # Usamos el nuevo método aquí

    def put(self, locker_id):
        args = parser.parse_args()
        locker = db.session.query(Locker).get(locker_id)
        if locker is None:
            return {'error': 'Locker not found'}, 404
        if args['ocupado'] is not None:
            locker.ocupado = args['ocupado']
        if args['cerrado'] is not None:
            locker.cerrado = args['cerrado']
        if args['hora_ocupacion'] is not None:
            locker.hora_ocupacion = datetime.strptime(args['hora_ocupacion'], "%Y-%m-%dT%H:%M:%S")
        if args['hora_desocupacion'] is not None:
            locker.hora_desocupacion = datetime.strptime(args['hora_desocupacion'], "%Y-%m-%dT%H:%M:%S")
        if args['rut'] is not None:
            locker.rut = args['rut']
        if args['disponible'] is not None:
            locker.disponible = args['disponible']
        if args['documento_notif'] is not None:
            locker.documento_notif = args['documento_notif']
        if args['puerta_abierta_notif'] is not None:
            locker.puerta_abierta_notif = args['puerta_abierta_notif']
        db.session.commit()
        return locker.to_dict(), 200


class InstructionsResource(Resource):
    instructions = []  # Almacena las instrucciones en una lista

    # Recibe nuevas instrucciones
    def post(self):
        args = parser.parse_args()  # Parser definido en tu código
        instruction = args  # Aquí debes definir cómo se ve una instrucción basada en args
        InstructionsResource.instructions.append(instruction)
        return jsonify(instruction)

    # Obtiene la última instrucción
    def get(self):
        if InstructionsResource.instructions:  # Si hay alguna instrucción
            return InstructionsResource.instructions.pop(0)  # Retorna y remueve la primera instrucción
        else:
            return 'No new instructions', 404


api.add_resource(LockerResource, '/locker/<int:locker_id>')
api.add_resource(LockerListResource, '/lockers')

if __name__ == '__main__':
		app.run(host='0.0.0.0', debug=True)
