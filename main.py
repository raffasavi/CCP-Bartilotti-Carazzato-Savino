from flask import Flask, request, redirect, url_for, send_file
from google.cloud import firestore, storage
from werkzeug.utils import secure_filename
import os
from secret import secret

app = Flask(__name__)


@app.route('/', methods=['GET'])
def main():
    return 'ok funziona'


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return redirect(url_for('static', filename='form.html'))
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return redirect(request.url)
        fname = secure_filename(file.filename)
        print(fname)
        file.save(os.path.join('/tmp/', fname))

        client = storage.Client()
        bucket = client.bucket('upload-mamei-1')
        source_file_name = fname
        destination_blob_name = source_file_name
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(os.path.join('/tmp/', fname))

        # blob.upload_from_string(file.read(),content_type=file.content_type)

        return 'File {} uploaded to {}.'.format(source_file_name, destination_blob_name)


@app.route('/sensors/<l>', methods=['GET', 'POST'])  ## guardare per gli indirizzi personalizzati con
def save_data():
    if request.method == 'GET':
        return redirect(url_for('static', filename='form.html'))
    if request.method == 'POST':
        s = request.values['secret']
        if s == secret:
            # dati su firestore
            date = request.values['date']
            hms = request.values['hms']
            hour = request.values['hour']
            value = request.values['value']
            db = firestore.Client()
            db.collection(l).document(hms).set(
                {'date': date, 'hour': hour, 'value': value})  # l dovrebbe essere il parametro passato dal link
            # immagine
            file = request.files['file']
            fname = file.filename  # il prof usava una libreria per il nome nel caso rimetti
            print(fname)

            client = storage.Client()
            bucket = client.bucket('[metti il nome del bucket creato su GCP]')
            source_file_name = fname
            destination_blob_name = source_file_name
            blob = bucket.blob(destination_blob_name)

            blob.upload_from_filename(os.path.join('/tmp/', fname))
        return 'ok', 200
    else:
        return 'non autorizzato', 401


# funzione per mandare i dati a chi li chiede, infatti il metodo è GET
@app.route('/sensors/<l>', methods=['GET'])
def get_data():
    db = firestore.Client()
    result = ''
    for doc in db.collection(l).stream():
        result += (f'{doc.id} --> {doc.to_dict()}<br>')
    return result


# esecuzione flask sulla porta 8080 bla bla bla kjn
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)



