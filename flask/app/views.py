from flask import Flask, request, jsonify, render_template
import pickle
from app import app
import os
import time

#global model 
#model = pickle.load(open("model.pkl", 'rb'))

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


if __name__ == "__main__":
    app.run(debug=False)
