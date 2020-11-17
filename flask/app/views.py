from flask import Flask, request, jsonify, render_template, make_response
import pickle
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
import jwt
import os
import time
import datetime
from functools import wraps

app.config['SECRET_KEY'] = 'thisisthesecretkey'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token') #http://127.0.0.1/route?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiTGl2aW5nZG9jcyIsImV4cCI6MTYwNTYyNTc3OH0.eiwl2xGq6qvM5j8D3GlVb_R7OS4zr3MYRmjlRwHYyAM

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 403

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message' : 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # os.chdir(os.path.dirname(__file__))
        # print("current workplace:", os.getcwd())
        f = request.files['file']
        global model
        model = pickle.load(f)
        #contents = f.read()
        pickle.dump(model, open('model.pkl', 'wb'))
        #model.save("model1.pkl")
        return 'file uploaded successfully'

@app.route('/predict', methods=['POST'])
def predict():

    # global model 
    model = pickle.load(open("model.pkl", 'rb'))
    # print(model)
    docid = next(request.form.values())
    prediction = model[int(docid)]

    return render_template('index.html', prediction_text1='{}'.format(prediction[0]), prediction_text2='{}'.format(prediction[1]), prediction_text3='{}'.format(prediction[2])
                           , prediction_text4='{}'.format(prediction[3]), prediction_text5='{}'.format(prediction[4]))


@app.route('/query/<int:docid>', methods=['GET'])
def get_prediction(docid):
    while True: 
        try:
            return jsonify({"prediction": model[docid]})
        except NameError:
            time.sleep(.5)


@app.route('/query_1', methods=['GET'])
def relative():
    while True:
        try: 
            return jsonify({"relative": str(sorted(list(model.keys())))})
        except NameError:
            time.sleep(.5)

@app.route('/protected')
@token_required
def protected():
    return jsonify({'message' : 'This is only available for people with valid tokens.'})

@app.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password == 'einberliner':
        #token = jwt.encode({'iat': datetime.datetime.utcnow(), 'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=15)}, app.config['SECRET_KEY'])
        token = jwt.encode({'iat': datetime.datetime.utcnow(), 'user' : auth.username, "scope": "public-api:read", "type": "client"}, app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})
    return make_response('Could not verify!',401) 
    #return 'test'

if __name__ == "__main__":
    app.run(debug=True)
