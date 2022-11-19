import re
import numpy as np
import os
from flask import Flask, app, request, render_template, redirect
from tensorflow.keras import models 
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.python.ops.gen_array_ops import concat
from tensorflow.keras.applications.inception_v3 import preprocess_input
import requests
from flask import Flask, app, redirect, render_template, request, url_for

from cloudant.client import Cloudant

client = Cloudant.iam('0941a94e-25e5-4f75-9079-5dd257ff7931-bluemix','D45bUG7nGt6FPKxu4fp5KSz8jLcBAoA3ZRxemtL__4Ru', connect=True)
my_database = client.create_database('my_database')

# client =Cloudant.iam("DATABASE=bludb;HOSTNAME=764264db-9824-4b7c-82df-40d1b13897c2.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=32536;PROTOCOL=TCPIP;UID=zvg68201;PWD=YAxMH9HtQ1UoLD4E;SECURITY=SSL;")
# connection = ibm_db.connect(connectionstring, '', '')

model1 = load_model('level.h5')
model2 = load_model('body.h5')


app = Flask(__name__)


@app.route("/")
def signup():
    return render_template("Index.html")


@app.route("/login")
def signin():
    return render_template("login.html")


@app.route("/register")
def aboutus():

    return render_template("register.html")


@app.route("/Index")
def index():
    return render_template("Index.html")


@app.route("/home")
def home():
    return render_template("home_page.html")


@app.route("/prediction")
def prediction():
    return render_template("prediction.html")


@app.route("/log_out")
def logout():
    return render_template("log_out.html")


@app.route("/afterreg", methods=['POST'])
def afterreg():
    x = [x for x in request.form.values()]
    print(x)
    data = {
        'name': x[0],
        'email': x[1],
        'pass': x[2]
    }
    print(data)
    query = {'data': {'$eq': data}}
    docs = my_database.get_query_result(query)
    print(docs)
    print(len(docs.all()))
    if (len(docs.all()) == 0):
        url = my_database.create_document(data)
        # response = requests.get(url)
        return render_template('home_page.html', pred="Registration Successful")
    else:
        return render_template('login.html', pred="You are already a member,Please login using your detials")


@app.route("/userlogin", methods=['GET', 'POST'])
def login():
    user = request.form['email']
    passw = request.form['password']
    print(user, passw)
    query = {'email': {'$eq': user}}
    docs = my_database.get_query_result(query)
    print(docs)
    print(len(docs.all()))
    if(len(docs.all())==0):
        return render_template('login.html', pred="Email not found")
    else:
        if((user==docs[0][0]['email'] and passw==docs[0][0]['pass'])):
            return render_template('home_page.html', pred="Login Successful")
        else:
            return render_template('login.html', pred="Enter Password")


@app.route('/result', methods=["GET", "POST"])
def res():
    if request.method == "POST":
        f = request.files['image']
        # getting the current path i.e where app.py is present #print("current path", basepath)
        basepath = os.path.dirname(__file__)
        # from anywhere in the system we can give image t
        filepath = os.path.join(basepath, 'uploads', f.filename)
        #print("upload folder is", filepath)
        f.save(filepath)

        img = image.load_img(filepath, target_size=(244, 244))
        x = image.img_to_array(img)  # img to array
        x = np.expand_dims(x, axis=0)  # used for adding one more dimension
        # print(x)
        img_data = preprocess_input(x)
        prediction1 = np.argmax(model2.predict(img_data))
        prediction2 = np.argmax(model1.predict(img_data))
        # prediction=model.predict(x)#instead of predict_classes(x) we can use predict(X) ---->predict_classes #print("prediction is ",prediction)
        index1 = ['front', 'rear', 'side']
        index2 = ['minor', 'moderate', 'severe']
        #result = str(index[output[0]])
        result1 = index1[prediction1]
        result2 = index2[prediction2]

        if (result1 == "front" and result2 == "minor"):
            value = "3000 - 5000 INR"
        elif (result1 == "front" and result2 == "moderate"):
            value = "6000 - 8000 INR"
        elif (result1 == "front" and result2 == "severe"):
            value = "9000 - 11000 INR"
        elif (result1 == "rear" and result2 == "minor"):
            value = "4800 - 6000 INR"
        elif (result1 == "rear" and result2 == "moderate"):
            value = "7080 - 9000 INR"
        elif (result1 == "rear" and result2 == "severe"):
            value = "11000 - 13000 INR"
        elif (result1 == "side" and result2 == "minor"):
            value = "6000 - 8000 INR"
        elif (result1 == "side" and result2 == "moderate"):
            value = "9000 - 11000 INR"
        elif (result1 == "side" and result2 == "severe"):
            value = "12000 - 15000 INR"
        else:
            value = "16000 - 50000 INR"
    
        return render_template('prediction.html', prediction=value)
"""" Running our application """
if __name__ == "__main__":
    app.run(debug=False, port=8080)
