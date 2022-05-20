from flask import Flask, request, render_template
from google.cloud import firestore, storage
from werkzeug.utils import secure_filename
from secret import secret
import traceback
import json
import os

app = Flask(__name__)


@app.route('/home', methods=['GET'])
@app.route('/', methods=['GET'])
def main():
    return render_template("front_end.html")


################################################################################################
########################################## INPUT ###############################################
################################################################################################

@app.route('/sensors/<names>', methods=['POST'])
def save_data(names):
    s = request.values['secret']
    if s == secret:

        # dati su firestore
        date = request.values['date']
        all = request.values['all']
        hour = request.values['hour']
        value = request.values['value']
        db = firestore.Client()
        db.collection(names).document(all).set({'date': date, 'hour': int(hour), 'value': int(value)})

        # immagine su cloudstorage
        file = request.files['file']
        fname = secure_filename(file.filename)
        file.save(os.path.join('/tmp/', fname))

        client = storage.Client()
        bucket = client.bucket('frame-bucket')
        source_file_name = fname
        destination_blob_name = source_file_name
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(os.path.join('/tmp/', fname))
        ###INVIO MAIL INTRUDER###
        if int(hour) >= 12 and int(
                value) >= 1:  # and int(value) >= 1: // intanto prova orario + verifica se serve o no int // invia una mail ogni volta che client invia un dato
            # if int(hour) >= 22 and int(hour) <6 and int(value) >= 1:
            ####funzione invio mail
            server = smtplib.SMTP(host='smtp.gmail.com', port=587)
            server.ehlo()
            server.starttls()
            # log
            server.login('ccp.project.22@gmail.com', 'claudiocomputing1!')
            # create msg
            subject = 'SICUREZZA NEGOZIO'
            body = 'INTRUDER ALERT: La telecamera ha rilevato una presenza fuori orario consentito'
            # struttura
            message = f'Subject: {subject}\n\n{body}'
            # invio e chiudo comunicazione
            server.sendmail('ccp.project.22@gmail.com', 'ccp.project.22@gmail.com', message)
            server.quit()
            ####
        ######
        return 'ok', 200
    else:
        return 'non autorizzato', 401


################################################################################################
########################################## OUTPUT ##############################################
################################################################################################

# ------------------------------ ACCESSO ALLA LISTA
@app.route("/lista", methods=['GET'])
def index():
    try:
        sensori = mostra_lista()
        return render_template("lista_sensori.html", sensori=sensori,
                               mess="Sono presenti " + str(len(sensori)) + " sensori nel database")
    except:
        traceback.print_exc()
        return render_template("lista_sensori.html", sensori=[],
                               mess="Non è stato possibile recuperare le informazioni")


# ------------------------------ funzione automatica: interrogo il db per la lista sensori
def mostra_lista():
    db = firestore.Client()
    result = []
    sensori = db.collections()
    for racc in sensori:
        sensore = {'id': racc.id}
        result.append(sensore)
    return result


# ------------------------------ ACCESSO A MAGGIORI INFO DI UN SENSORE
# @app.route('/informazioni', methods=['POST'])
# def get_data():
#    idsens = request.form['id']#prendo l'id dalla form
#    db = firestore.Client()
#    result = ''
#    for doc in db.collection(idsens).stream():
#        result += (f'{doc.id} --> {doc.to_dict()}<br>')
#    return result

# ------------------------------ ACCESSO A MAGGIORI INFO DI UN SENSORE
@app.route('/informazioni', methods=['POST'])
def index2():
    idsens = request.form['id']  # prendo l'id dalla form
    db = firestore.Client()
    dati = []
    dati.append(['hour', 'value'])
    for doc in db.collection(idsens).stream():
        x = doc.to_dict()
        dati.append([x['hour'], int(x['value'])])
    return render_template("profilo_sensore.html", dati=dati)


# esecuzione flask sulla porta 8080
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)



