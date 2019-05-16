# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

# from flask import request
import bson
from flask import Flask,request,jsonify
from flask_restplus import Resource, Api
from flask_restplus import fields
# from flask_restplus import inputs
# from flask_restplus import reqparse
from flask_pymongo import PyMongo

app = Flask(__name__)
api = Api(app,
          default="Information",  # Default namespace
          title="Dentist Information",  # Documentation Title
          description="The dentist information")

dentist_name = api.model('DentistName', {
    'name': fields.String
})

dentist_information = api.model('DentistInformation', {
    'name': fields.String,
    'address': fields.String,
    'specialization': fields.String
})

app.config["MONGO_DBNAME"] = "my-database"
app.config["MONGO_URI"] = "mongodb://Conlin:Tcgabcd123@ds111492.mlab.com:11492/my-database"
mongo = PyMongo(app)

@api.route('/information')
class Timeslots(Resource):
    @api.response(200, 'OK')
    @api.doc(description="Get all the dentist information")
    def get(self):
        api_data = mongo.db.dentist_info
        output = []
        for q in api_data.find():
            output.append({'name': q['name'],
                           'location': q['address'],
                           'specialization': q['specialization']})
        return output, 200
    @api.expect(dentist_information)
    @api.response(200, 'OK')
    @api.response(201, 'Created')
    @api.response(400, 'Error')
    @api.doc(description="Add the information of dentist")
    def post(self):
        # print(g.args)
        api_data = mongo.db.dentist_info
        info = request.json
        n_list = []
        for q in api_data.find():
            n_list.append(q['name'])
        name = info['name']
        addr = info['address']
        specialization = info['specialization']
        # print(name,n_list)
        output = {'name':name,'address':addr,'specialization':specialization}
        if name not in n_list:
            api_data.insert_one(output)
            return  output, 200
        else:
            return "Name esisted",400
    @api.expect(dentist_name)
    @api.response(400, 'Error')
    @api.response(200, 'OK')
    @api.doc(description="Deletes an existing dentist file by name")
    def delete(self):
        info = request.json
        name = info['name']
        flg = 0
        api_data = mongo.db.dentist_info
        for q in api_data.find():
            if name == str(q['name']):
                flg = 1
        # q = api_data.find_one({'indicator': id})
        if flg:
            try:
                mongo.db.dentist_info.remove({'name': name})
            except bson.errors.InvalidId:
                return "", 400
            output = {"message": "Dentist %s is removed from the database!" % (name)}
            return output, 200
        else:
            return "", 400

@api.route('/information/<string:name>')
@api.param('name', 'The name of dentist')
class Country_Year_Class(Resource):
    @api.response(400, 'Error')
    @api.response(200, 'OK')
    @api.doc(description="Input a dentist name")
    def get(self, name):
        api_data = mongo.db.dentist_info
        flg = 0
        for q in api_data.find():
            if name == str(q['name']):
                flg = 1
        if flg:
            q = api_data.find_one({'name': name})
            output = ({'name': q['name'],
                       'address': q['address'],
                       'specialization': q['specialization']})
            return output, 200
        else:
            return "", 400

# @api.route('/bottest')
# class Timeslots(Resource):
#     @api.response(200, 'OK')
#     @api.doc(description="Get all the dentist name")
#     def get(self):
#         # api_data = mongo.db.dentist_info
#         # output = []
#         # for q in api_data.find():
#         #     output.append({'name': q['name'],
#         #                    'location': q['address'],
#         #                    'specialization': q['specialization']})
#         output = {"messages": [{"text": "Welcome to the Chatfuel Rockets!"},{"text": "What are you up to?"}]}
#         return output, 200


if __name__ == '__main__':
    #######################################  mongodb   ######################################################
    # mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % ('Conlin', 'Tcgabcd123', 'ds111492.mlab.com', '11492', 'my-database')
    # client = MongoClient(mongo_uri)
    # db = client['my-database']
    app.run("0.0.0.0",debug=True)