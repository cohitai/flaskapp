# main.py
from flask_login import login_required, current_user
from flask import Flask, request, jsonify, render_template, make_response, Blueprint
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



main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('homepage.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('index.html', name=current_user.name)


app.config['SECRET_KEY'] = 'thisisthesecretkey'

path_to_model = 'prediction/model.pkl'
path_to_exclusion = 'exclusion/ext.pkl'

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

@app.route('/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        global model
        model = pickle.load(f)
        pickle.dump(model, open(path_to_model, 'wb'))
        return '<h1> file uploaded successfully. <h1>'

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        model = pickle.load(open(path_to_model, 'rb'))
    except FileNotFoundError:
        return "ModelNotFoundError: please upload a model first and try again."

    docid = next(request.form.values())
    
    try:
        prediction = model[int(docid)]
    except KeyError:
        return "DocidError: {0} does not exist in the system.".format(docid)
    website = 'https://berliner-zeitung.de/'     
    return render_template('index.html', prediction_text1='{}'.format(website+prediction[0]), prediction_text2='{}'.format(website+prediction[1]), prediction_text3='{}'.format(website+prediction[2])
                           , prediction_text4='{}'.format(website+prediction[3]), prediction_text5='{}'.format(website+prediction[4]))

@app.route('/query/<int:docid>', methods=['GET'])
@login_required
def get_prediction(docid):
    model = pickle.load(open(path_to_model, 'rb'))
    while True: 
        try:
            return jsonify({"prediction": model[docid]})
        except NameError:
            time.sleep(.5)


@app.route('/exclusion_form', methods=['GET', 'POST'])
@login_required
def exclusion_form():
    docid = next(request.form.values())
    return get_exclusion(docid)


@app.route('/inclusion_form', methods=['GET', 'POST'])
@login_required
def inclusion_form():
    docid = next(request.form.values())
    return reinclude(docid)


@app.route('/exclude/<int:docid>', methods=['GET'])
@login_required
def get_exclusion(docid):

    # initiating an empty list if it does not exist yet. 
    if not os.path.exists(path_to_exclusion):
        with open(path_to_exclusion, 'wb') as f:
            pickle.dump([],f)

    with open(path_to_exclusion, 'rb') as f:
        list_ex = pickle.load(f)
        list_ex.append(docid)
    with open(path_to_exclusion,'wb') as f:
        pickle.dump(list(set(list_ex)),f)
    try:
        return '<h1>DocId {0} is now excluded<h1>'.format(docid)
    except NameError:
        time.sleep(.5)

@app.route('/include/<int:docid>', methods=['GET'])
@login_required
def reinclude(docid):
    
    # initiating an empty list if it does not exist yet. 
    if not os.path.exists(path_to_exclusion):
        with open(path_to_exclusion, 'wb') as f:
            pickle.dump([],f)

    with open(path_to_exclusion, 'rb') as f:
        exclusion_data = pickle.load(f)
        try:
            exclusion_data.remove(docid)
        except ValueError:
            pass
    with open(path_to_exclusion, 'wb') as f:
        pickle.dump(exclusion_data, f)
    
    return "<h1>new excluded articles list:{0}<h1>".format(str(exclusion_data))

@app.route('/exclusions_list', methods=['GET'])
@login_required
def list_ext():

    # initiating an empty list if it does not exist yet.    
    if not os.path.exists(path_to_exclusion):
        with open(path_to_exclusion, 'wb') as f:
            pickle.dump([],f)

    exclusion_data = []
    with open(path_to_exclusion, 'rb') as f:
        return jsonify({"excluded articles": str( pickle.load(f))})

@app.route('/query_1', methods=['GET'])
@login_required
def relative():
    model = pickle.load(open(path_to_model, 'rb'))
    while True:
        try: 
            return jsonify({"relative": str(sorted(list(model.keys())))})
        except NameError:
            time.sleep(.5)

@app.route('/protected')
@token_required
def protected():
    return jsonify({'message' : 'This is only available for people with valid tokens.'})

@app.route('/create_token',methods=['POST'])
@login_required
def create_token():
    auth = request.authorization
    user = request.POST.get('username', '')
    password1 = request.POST.get('password', '')

    if user == 'Livingdocs' and password1 == 'einberliner':
        #token = jwt.encode({'iat': datetime.datetime.utcnow(), 'user' : auth.username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=15)}, app.config['SECRET_KEY'])
        token = jwt.encode({'iat': datetime.datetime.utcnow(), 'user' : auth.username, "scope": "public-api:read", "type": "client"}, app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})
    return make_response('Could not verify!',401)
