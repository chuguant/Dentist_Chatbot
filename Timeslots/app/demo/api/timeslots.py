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
          default="Appointments",  # Default namespace
          title="Dentist Reservation",  # Documentation Title
          description="Book an appointment with a dentist")

dentist_name = api.model('DentistName', {
    'name': fields.String
})

# booktime_model = api.model('Booktime', {
#     'period': fields.String,
#     'state': fields.String
# })

period_model = api.model('Period',{
    'period':fields.String
})

event_model = api.model('book_id',{
    'book_id':fields.String
})

app.config["MONGO_DBNAME"] = "my-database"
app.config["MONGO_URI"] = "mongodb://Conlin:Tcgabcd123@ds111492.mlab.com:11492/my-database"
mongo = PyMongo(app)

@api.route('/timeslots/<string:name>')
@api.param('name', 'The dentist name')
class Timeslots(Resource):
    @api.response(400, 'Error')
    @api.response(200, 'OK')
    @api.doc(description="Available time of this dentist")
    def get(self,name):
        api_data = mongo.db[name]
        name_l = []
        name_s = ''
        for j in mongo.db.dentist_info.find():
            name_l.append(j['name'])
            name_s=name_s+j['name']+','
        if name not in name_l:
            return "Sorry, no "+name+" dentist here. Mayebe you mean "+name_s,400
        output_list = []
        for q in api_data.find():
            output_list.append({'period':q['period'],'state':q['state']})
        # print(output_list)
        return output_list, 200

    @api.expect(period_model)
    @api.response(400, 'Error')
    @api.response(200, 'OK')
    @api.doc(description="Add an available time,format xx-xx-dd-mm-yyyy(24h, e.g.12-13-26-04-2019)")
    def post(self,name):
        info = request.json
        period = info['period']
        # state = info['state']
        t_list = []
        name_l = []
        name_s = ''
        for j in mongo.db.dentist_info.find():
            name_l.append(j['name'])
            name_s=name_s+j['name']+','
        if name not in name_l:
            return "Sorry, no "+name+" dentist here. Mayebe you mean "+name_s,400
        for q in mongo.db[name].find():
            t_list.append(q['period'])
        if period not in t_list:
            mongo.db[name].insert_one({'period':period,'state':'available'})
            return  "Timeslots added", 200
        else:
            return "Time esisted",400

    @api.expect(period_model)
    @api.response(400, 'Error')
    @api.response(200, 'OK')
    @api.doc(description="Deletes an existing timeslot")
    def delete(self,name):
        name_l = []
        name_s = ''
        for j in mongo.db.dentist_info.find():
            name_l.append(j['name'])
            name_s=name_s+j['name']+','
        if name not in name_l:
            return "Sorry, no "+name+" dentist here. Mayebe you mean "+name_s,400
        info = request.json
        period = info['period']
        flg = 0
        api_data = mongo.db[name]
        for q in api_data.find():
            if period == str(q['period']):
                flg = 1
        # q = api_data.find_one({'indicator': id})
        if flg:
            try:
                mongo.db[name].remove({'period': period})
            except bson.errors.InvalidId:
                return "", 400
            output = {"message": "Timeslots %s is removed from the database!" % (period)}
            return output, 200
        else:
            return "", 400

@api.route('/book/<string:name>/<string:period>')
@api.param('name', 'The dentist name')
class BookAppointment(Resource):
    # @api.expect(period_model)
    @api.response(400, 'Error')
    @api.response(200, 'OK')
    @api.doc(description="Book a time,format xx-xx-dd-mm-yyyy(24h, e.g.12-13-26-04-2019")
    def put(self, name,period):
        name_l = []
        name_s = ''
        for j in mongo.db.dentist_info.find():
            name_l.append(j['name'])
            name_s=name_s+j['name']+','
        if name not in name_l:
            return "Sorry, no "+name+" dentist here. Mayebe you mean "+name_s,400
        api_data = mongo.db[name]
        # info = request.json
        # period = info['period']
        time_list = []
        for j in mongo.db[name].find():
            time_list.append(j['period'])
        if period not in time_list:
            return 'This period is not the available time, please check the time list of '+name, 400
        q = api_data.find_one({'period': period})
        if q['state'] == 'reserved':
            return 'This time period has already been reserved', 400
        else:
            api_data.update_one({'period': period},{'$set': {'state':'reserved'}})
            book_id = period.replace('-','')
            mongo.db.book_id.insert_one({'book_id': book_id+name})
            return 'You have successfully booked this time,and the book id is '+book_id+name+'.',200

@api.route('/cancelation/<string:name>/<string:period>')
@api.param('name', 'The dentist name')
class Cancelation(Resource):
    # @api.expect(period_model)
    @api.response(400, 'Error')
    @api.response(200, 'OK')
    @api.doc(description="Cancel an appointment according to your book_id, xx-xx-dd-mm-yyyy and dentist name, e.g.12-13-26-04-2019")
    def put(self, name,period):
        name_l = []
        name_s = ''
        for j in mongo.db.dentist_info.find():
            name_l.append(j['name'])
            name_s=name_s+j['name']+','
        if name not in name_l:
            return "Sorry, no "+name+" dentist here. Mayebe you mean "+name_s,400
        api_data = mongo.db[name]
        # info = request.json
        # period = info['period']
        q = api_data.find_one({'period': period})
        if q['state'] == 'available':
            return 'This time has not been booked', 400
        else:
            api_data.update_one({'period': period},{'$set': {'state':'available'}})
            book_id = period.replace('-','')
            mongo.db.book_id.remove({'book_id': book_id+name})
            return 'You have successfully canceled this time,and the book id is '+book_id+name+'.',200



@api.route('/event_id')
class BookEvent(Resource):
    @api.response(400, 'Error')
    @api.response(200, 'OK')
    @api.doc(description="The booked event id")
    def get(self):
        api_data = mongo.db.book_id
        output_list = []
        for q in api_data.find():
            output_list.append({'id': q['book_id']})
        # print(output_list)
        return output_list, 200

    # @api.expect(event_model)
    # @api.response(400, 'Error')
    # @api.response(200, 'OK')
    # @api.doc(description="Deletes booked event id")
    # def delete(self):
    #     info = request.json
    #     event = info['book_id']
    #     flg = 0
    #     api_data = mongo.db.book_id
    #     for q in api_data.find():
    #         if event == str(q['period']):
    #             flg = 1
    #     # q = api_data.find_one({'indicator': id})
    #     if flg:
    #         try:
    #             mongo.db.book_id.remove({'id': event})
    #         except bson.errors.InvalidId:
    #             return "", 400
    #         output = {"message": "Event ID %s is removed from the database!" % (event)}
    #         return output, 200
    #     else:
    #         return "", 400

if __name__ == '__main__':
    #######################################  mongodb   ######################################################
    # mongo_uri = 'mongodb://%s:%s@%s:%s/%s' % ('Conlin', 'Tcgabcd123', 'ds111492.mlab.com', '11492', 'my-database')
    # client = MongoClient(mongo_uri)
    # db = client['my-database']
    app.run("0.0.0.0",debug=True)