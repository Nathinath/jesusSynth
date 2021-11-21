
import json
from flask import Flask, request

import analyseSound

# -------------------------------------------------------------------------------------------------------------------------------
# 0 - Settings
# -------------------------------------------------------------------------------------------------------------------------------
api_gateway = 'http://localhost:3000/'
api_rec = 'http://localhost:3001/'

# -------------------------------------------------------------------------------------------------------------------------------
# 1 - Main methods
# -------------------------------------------------------------------------------------------------------------------------------
inData = {}
outData = {}

# -------------------------------------------------------------------------------------------------------------------------------
# 2 - Create micro service - Run main functions
# -------------------------------------------------------------------------------------------------------------------------------
app = Flask(__name__)

@app.route("/rec", methods=['POST'])
def apiRecord():
    inData = {}
    outData = {}
    statusOp = {}
    rawSignal = []

    inData = json.loads(request.data)
    print("Start recording with: " + str(inData['params']))

    fileName = inData['params']['recFileName']
    time = float(inData['params']['recDuration'])
    sampleRate = int(inData['params']['recSampleRate'])
    
    rawSignal, sampleRate, statusOp = analyseSound.record(fileName, time, sampleRate)
    print("Recording over: " + str(statusOp))

    # send request response
    if statusOp['success']:
        outData['name'] = "Raw signal"
        outData['sampleRate'] = sampleRate
        outData['data'] = rawSignal.to_dict('list')
        outData['statusOp'] = statusOp
        return json.dumps(outData), 201, {'content-type': 'application/json'}
    else:
        return json.dumps(outData), 409, {'content-type': 'application/json'}

@app.route("/preproc", methods=['POST'])
def apiPreproc():
    inData = {}
    outData = {}
    statusOp = {}
    rawSignal = []
    preprocSignal = []

    inData = json.loads(request.data)
    print("Start preprocessing with: " + str(inData['params']))

    threshold = float(inData['params']['preprocThres'])
    sampleRate = int(inData['rawSignal']['sampleRate'])
    rawSignal = inData['rawSignal']['data']
    
    preprocSignal, statusOp = analyseSound.preproc(rawSignal, sampleRate, threshold)
    print("Preprocessing over: " + str(statusOp))

    # send request response
    if statusOp['success']:
        outData['name'] = "Preprocessed signal"
        outData['sampleRate'] = sampleRate
        outData['data'] = preprocSignal.to_dict('list')
        outData['statusOp'] = statusOp
        return json.dumps(outData), 201, {'content-type': 'application/json'}
    else:
        return json.dumps(outData), 409, {'content-type': 'application/json'}

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=3001)