from flask import Flask, request, render_template,redirect,url_for
from flask_cors import cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
import sqlite3
import tensorflow as tf
import numpy as np
import smtplib
import vonage

gfr = 0.0

app = Flask(__name__)
#app.secret_key= "Secret Key"
model = tf.keras.models.load_model('Kidney.h5')
client = vonage.Client(key="6204fec1", secret="0uU9UC2GlKLbjL7E")
sms = vonage.Sms(client)


#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Lokesh@1628@localhost/final'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#db = SQLAlchemy(app)


#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = ''
#app.config['MYSQL_DB'] = 'flask'

#db = MySQL(app)


#class Data(db.Model):
   # id = db.Column(db.Integer, primary_key = True)
   # name = db.Column(db.String(100))
   # phn = db.Column(db.Integer)
   # eid = db.Column(db.String(100))
   # age = db.Column(db.Integer)
   # sg = db.Column(db.Float(100))
   # al = db.Column(db.Float(100))
   # sc = db.Column(db.Float(100))
   # pcv = db.Column(db.Float(100))
   # htn = db.Column(db.Float(100))


    #def __init__(self,id,name,phn,eid,age,sg,al,sc,pcv,htn):
     #   self.name = name
     #   self.phn = phn
     #   self.eid = eid
     #   self. age = age
     #   self.sg = sg
     #   self.al = al
     #   self .sc = sc
     #   self.pcv = pcv
     #   self.htn = htn



@app.route("/")
@cross_origin()
def home():
    return render_template("main.html")

@app.route("/predict", methods=["GET", "POST"])
@cross_origin()
def predict():
    if request.method == "POST":

        # getting data
        name = request.form['name']
        phn = request.form['phn']
        eid = request.form['eid']
        age = request.form['age']
        sg = request.form["sg"]
        al = request.form["al"]
        sc = request.form["sc"]
        pcv = request.form["pcv"]
        htn = request.form["htn"]


        #my_data = Data(name, phn, eid, age, sg, al, sc, pcv, htn)
        #db.session.add(my_data)
        #db.session.commit()


        #print(sg,al,sc,pcv,htn)
        l = [sg, al, sc, pcv, htn]
        l = np.array(l)
        l = l.reshape(1, -1)
        l = [[float(sg), float(al), float(sc), float(pcv), float(htn)]]
        inp = model.predict(l)
        gfr = ((1.086)*(175)*(float(sc)**(-1.154))*(int(age)**(-0.203))*(0.742))
        print(sg,al,sc,pcv,htn,gfr)
        #return render_template('home.html', prediction_text = "FINAL REPORT {}".format(inp))
        if(eid!=""):
            with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
                smtp.login("akprogramer@gmail.com", "Chintu@3009")
                if (inp < 0.5):
                    print("CKD")
                    subject = f'Chronic Kidney Disease Predictor'
                    content = f'name={name}\n\n emailid={eid}\n\n age={age}\n\n GFR = {gfr}\n\n Your Having Chronic Kidney disease'

                    msg = f'Subject: {subject}\n\n{content}'
                    smtp.sendmail("akprogramer@gmail.com", eid, msg)

                else:
                    print("Non-CKD")
                    subject = f'Chronic Kidney Disease Predictor'
                    content = f'name={name}\n\n emailid={eid}\n\n age={age}\n\n Your Not Having Chronic Kidney disease'

                    msg = f'Subject: {subject}\n\n{content}'
                    smtp.sendmail("akprogramer@gmail.com", eid, msg)
            smtp.close()
        if (phn != ""):
            if (inp < 0.5):
                responseData = sms.send_message(
                    {
                        "from": "Chronic Kidney Disease Predictor",
                        "to": "919550607442",
                        "text": "FINAL REPORT HAVING CKD",
                    }
                )

                if responseData["messages"][0]["status"] == "0":
                    print("Message sent successfully.")
                else:
                    print(f"Message failed with error: {responseData['messages'][0]['error-text']}")
            else:
                responseData = sms.send_message(
                    {
                        "from": "Chronic Kidney Disease Predictor",
                        "to": "919550607442",
                        "text": "FINAL REPORT HAVING NON-CKD",
                    }
                )

                if responseData["messages"][0]["status"] == "0":
                    print("Message sent successfully.")
                else:
                    print(f"Message failed with error: {responseData['messages'][0]['error-text']}")





        if (inp < 0.5):
            print("CKD,a")
            prediction_text = "FINAL REPORT HAVING CKD"
            if(gfr >= 90):
                a = "Normal"
                return render_template('main.html',res=prediction_text,res1=a)
            elif(gfr >= 60 and gfr <= 89):
                a = "Stage 2"
                return render_template('main.html', res=prediction_text, res1=a)
            elif(gfr >= 30 and gfr <= 59):
                a = "Stage 3"
                return render_template('main.html', res=prediction_text, res1=a)
            elif(gfr >= 15 and gfr <= 29):
                a = "Stage 4"
                return render_template('main.html', res=prediction_text, res1=a)
            elif(gfr < 15):
                a = "Stage 5"
                return render_template('main.html', res=prediction_text, res1=a)
        else:
            print("Non-CKD")
            prediction_text = "FINAL REPORT HAVING NON-CKD"
            return render_template('main.html', res=prediction_text,res1=gfr)

    return render_template("main.html")


if __name__ == "__main__":
    app.run(debug=True)
