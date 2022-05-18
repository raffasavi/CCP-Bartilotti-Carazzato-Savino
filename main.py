from flask import Flask, request
from google.cloud import firestore
from secret import secret
app = Flask(__name__)

@app.route('/', methods=['GET'])
def main():
    return 'ok FUNZIONA ok'

@app.route('/sensors/sensor', methods=['POST']) ## guardare per gli indirizzi personalizzati con
def save_data():
    s = request.values['secret']
    if s == secret:
        idsens = request.values['idsens']
        date = request.values['date']
        hms = request.values['hms']
        hour = request.values['hour']
        value = request.values['value']
        db = firestore.Client()
        db.collection(idsens).document(hms).set({'date': date, 'hour':hour, 'value': value})
        return 'ok', 200
    else:
        return 'non autorizzato',401
# funzione per mandare i dati a chi li chiede, infatti il metodo è GET
@app.route('/sensors/sensor1', methods=['GET'])
def get_data():
    db = firestore.Client()
    result = ''
    for doc in db.collection('sensor1').stream():
        result += (f'{doc.id} --> {doc.to_dict()}<br>')
    return result

# esecuzione flask sulla porta 8080
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

