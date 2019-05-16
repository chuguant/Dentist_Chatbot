from flask import Flask
from flask import render_template,jsonify,request
import requests
from rivescript import RiveScript

app = Flask(__name__)
app.secret_key = '12345'

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat',methods=['POST'])
def chat():
    try:
        user_message = request.form["text"]
        print(user_message)
        bot = RiveScript()
        bot.load_directory("./brain")
        bot.sort_replies()
        response_text = bot.reply("localuser", user_message)
        if "intent" in response_text:
            if "intent=dentistName" in response_text:
                res = requests.get('http://0.0.0.0:5003/information')
                data = res.json()
                response_text = ""
                for i in range(len(data)):
                    response_text = response_text + data[i]["name"] + " "
            if "intent=dentistInfo" in response_text:
                res = requests.get('http://0.0.0.0:5003/information')
                data = res.json()
                response_text = "Hi, here is the information about dentist you could book with. "
                for i in range(len(data)):
                    response_text = response_text + data[i]["name"] + ", live in " + data[i]["location"] + ", major in " + data[i][
                        "specialization"] + "|"
            if "intent=dentistSinInfo" in response_text:
                name = response_text[29:].capitalize()
                res = requests.get('http://0.0.0.0:5003/information/' + name)
                data = res.json()
                response_text = data["name"] + ", live in " + data["address"] + ", major in " + data["specialization"]
            if "intent=timetable" in response_text:
                name = response_text[24:].capitalize()
                res = requests.get('http://0.0.0.0:5002/timeslots/' + name)
                data = res.json()
                # print(data)
                # for i in data:
                #     print(i)
                response_text = ""
                for i in range(len(data)):
                    response_text = response_text + data[i]["period"] + " " + data[i]["state"] + "|"
            if "intent=book" in response_text:
                # print(response_text)
                period_tmp = response_text[20:32]
                period = period_tmp[0:2] + "-" + period_tmp[2:4] + "-" + period_tmp[4:6] + "-" + period_tmp[6:8] + "-" + period_tmp[8:12]
                name = response_text[41:].capitalize()
                print(name,period)
                res = requests.put('http://0.0.0.0:5002/book/' + name + "/" + period)
                # print(res.text)
                data = res.json()
                response_text = data
                # for i in range(len(data)):
                #     response_text = response_text + data[i]["period"] + " " + data[i]["state"] + "|"
            if "intent=cancel" in response_text:
                # print(response_text)
                period_tmp = response_text[22:34]
                period = period_tmp[0:2] + "-" + period_tmp[2:4] + "-" + period_tmp[4:6] + "-" + period_tmp[6:8] + "-" + period_tmp[8:12]
                name = response_text[43:].capitalize()
                # print(name,period)
                res = requests.put('http://0.0.0.0:5002/cancelation/' + name + "/" + period)
                # print(res.text)
                data = res.json()
                response_text = data
            if "intent=checktime" in response_text:
                period_tmp = response_text[25:37]
                period = period_tmp[0:2] + "-" + period_tmp[2:4] + "-" + period_tmp[4:6] + "-" + period_tmp[6:8] + "-" + period_tmp[8:12]
                name = response_text[46:].capitalize()
                # print(name,period)
                res = requests.get('http://0.0.0.0:5002/timeslots/' + name)
                # print(res.text)
                data = res.json()
                flg = 0
                for i in data:
                    if i["period"] == period:
                        state = i["state"]
                        flg = 1
                if flg == 0:
                    response_text = "Sorry, this time is not in the time table"
                elif state == "available":
                    response_text = "Congratulations, this time is available!"
                elif state == "reserved":
                    response_text = "Unfortunately, this time may have been booked, it is not available"
        else:
            pass
        if response_text == "[ERR: No Reply Matched]":
            response_text = "Sorry, I do not know what you mean. I am a dentist booking system. What can I do for you?"
        return jsonify({"status":"success","response":response_text})
    except Exception as e:
        print(e)
        return jsonify({"status":"success","response":"Sorry, I do not know what you mean. I am a dentist booking system to help you make appointment. What can I do for you?"})

# app.config["DEBUG"] = True
if __name__ == "__main__":
    app.run(port=8080,debug=True)