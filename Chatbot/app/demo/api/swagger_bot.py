from __future__ import absolute_import, print_function
from flask import Flask
from flask_restplus import Resource, Api
from rivescript import RiveScript
import requests


app = Flask(__name__)
api = Api(app,
          default="Chat",  # Default namespace
          title="Rule-Based Chatbot",  # Documentation Title
          description="A bot you can chat with")

# question_model = api.model('Question', {
#     'message': fields.String
# })


@api.route('/ask/<string:qus>')
@api.param('qus', 'The question')
class Chat(Resource):
    # @api.expect(question_model)
    @api.response(400, 'Error')
    @api.response(200, 'OK')
    @api.doc(description="ask a question")
    def post(self,qus):
        # print(g.args)
        # Qus = request.json
        # qus = Qus['message']
        bot = RiveScript()
        bot.load_directory("./brain")
        bot.sort_replies()
        reply = bot.reply("localuser", qus)
        if "intent" in reply:
            if "intent=dentistName" in reply:
                res = requests.get('http://0.0.0.0:5003/information')
                data = res.json()
                reply = ""
                for i in range(len(data)):
                    reply = reply + data[i]["name"] + " "
            if "intent=dentistInfo" in reply:
                res = requests.get('http://0.0.0.0:5003/information')
                data = res.json()
                reply = ""
                for i in range(len(data)):
                    reply = reply + data[i]["name"] + ", live in "+data[i]["location"]+", major in "+data[i]["specialization"]+"|"
            if "intent=dentistSinInfo" in reply:
                name = reply[29:].capitalize()
                res = requests.get('http://0.0.0.0:5003/information/'+name)
                data = res.json()
                reply = data["name"] + ", live in " + data["address"] + ", major in " + data["specialization"]
            if "intent=timetable" in reply:
                name = reply[24:].capitalize()
                res = requests.get('http://0.0.0.0:5002/timeslots/' + name)
                data = res.json()
                # print(data)
                # for i in data:
                #     print(i)
                reply = ""
                for i in range(len(data)):
                    reply = reply + data[i]["period"] + " " + data[i]["state"] + "|"
            if "intent=book" in reply:
                # print(reply)
                period_tmp = reply[20:32]
                period = period_tmp[0:2]+"-"+period_tmp[2:4]+"-"+period_tmp[4:6]+"-"+period_tmp[6:8]+"-"+period_tmp[8:12]
                name = reply[41:].capitalize()
                # print(name,period)
                res = requests.put('http://0.0.0.0:5002/book/'+name+"/"+period)
                # print(res.text)
                data = res.json()
                reply = data
                # for i in range(len(data)):
                #     reply = reply + data[i]["period"] + " " + data[i]["state"] + "|"
            if "intent=cancel" in reply:
                # print(reply)
                period_tmp = reply[22:34]
                period = period_tmp[0:2] + "-" + period_tmp[2:4] + "-" + period_tmp[4:6] + "-" + period_tmp[6:8]+"-"+period_tmp[8:12]
                name = reply[43:].capitalize()
                # print(name,period)
                res = requests.put('http://0.0.0.0:5002/cancelation/' + name + "/" + period)
                # print(res.text)
                data = res.json()
                reply = data
            if "intent=checktime" in reply:
                period_tmp = reply[25:37]
                period = period_tmp[0:2] + "-" + period_tmp[2:4] + "-" + period_tmp[4:6] + "-" + period_tmp[6:8] + "-" + period_tmp[8:12]
                name = reply[46:].capitalize()
                print(name,period)
                res = requests.get('http://0.0.0.0:5002/timeslots/' + name)
                # print(res.text)
                data = res.json()
                flg = 0
                for i in data:
                    if i["period"] == period:
                        state = i["state"]
                        flg = 1
                if flg == 0:
                    reply = "Sorry, this time is not in the time table"
                elif state == "available":
                    reply = "Congratulations, this time is available!"
                elif state == "reserved":
                    reply = "Unfortunately, this time may be booked, it is not available"
        else:
            pass
        if reply == "[ERR: No Reply Matched]":
            return "Sorry, I do not know what you mean", 400
        else:
            return reply,200

if __name__ == '__main__':
    app.run("0.0.0.0",debug=True)