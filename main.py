from flask import Flask, request, redirect, url_for, send_file
from google.cloud import firestore, storage
from werkzeug.utils import secure_filename
from secret import secret
import os

app = Flask(__name__)


@app.route('/', methods=['GET'])
def main():
    return 'ok funziona'


@app.route('/sensors/sensor', methods=['GET', 'POST'])  ## guardare per gli indirizzi personalizzati con
def save_data():
    if request.method == 'GET':
        return redirect(url_for('static', filename='form.html'))
    if request.method == 'POST':
        s = request.values['secret']
        if s == secret:
            # dati su firestore
            idsens = request.values['idsens']
            date = request.values['date']
            all = request.values['all']
            hour = request.values['hour']
            value = request.values['value']
            db = firestore.Client()
            db.collection(idsens).document(all).set(
                {'date': date, 'hour': hour, 'value': value})  # l dovrebbe essere il parametro passato dal link
            # immagine
            file = request.files['file']
            fname = secure_filename(file.filename)
            file.save(os.path.join('/tmp/', fname))

            client = storage.Client()
            bucket = client.bucket('cc-cartella')
            source_file_name = fname
            destination_blob_name = source_file_name
            blob = bucket.blob(destination_blob_name)

            blob.upload_from_filename(os.path.join('/tmp/', fname))
            return 'ok', 200
        else:
            return 'non autorizzato', 401


# funzione per mandare i dati a chi li chiede, infatti il metodo è GET
@app.route('/sensors/sensor', methods=['GET'])
def get_data():
    db = firestore.Client()
    result = ''
    for doc in db.collection('sensor').stream():
        result += (f'{doc.id} --> {doc.to_dict()}<br>')
    return result


# esecuzione flask sulla porta 8080
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)



