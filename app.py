from flask import Flask
from flask_restful import  Api
from views.siLing import siLing



app = Flask(__name__)
api = Api(app)

api.add_resource(siLing, '/siLing') #


if __name__ == '__main__':
    app.run()
