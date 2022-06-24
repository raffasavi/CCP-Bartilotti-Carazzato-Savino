################################################################################################
######################################### LIBRERIE #############################################
################################################################################################

from flask import Flask, request, render_template, send_file
from google.cloud import firestore, storage
from werkzeug.utils import secure_filename
from secret import secret
import smtplib
import traceback
import os

################################################################################################
########################################## START ###############################################
################################################################################################

app = Flask(__name__)

@app.route('/home', methods=['GET'])
@app.route('/', methods=['GET'])
def main():
    return render_template("front_end.html")

################################################################################################
################################ SALVATAGGIO DATI DI INPUT #####################################
################################################################################################

@app.route('/sensors/<names>', methods=['POST'])
def save_data(names):
    s = request.values['secret']
    if s == secret:
        # dati su firestore
        all = request.values['all']
        hms = request.values['hms']
        day = request.values['day']
        month = request.values['month']
        hour = request.values['hour']
        min = request.values['min']
        sec = request.values['sec']
        value = request.values['value']
        db = firestore.Client()
        db.collection(names).document(all).set({'hms': hms, 'day': int(day), 'month': int(month),
                                                'hour': int(hour), 'min': int(min), 'sec': int(sec),
                                                'value': int(value), 'all': all})

        # immagine su cloudstorage
        file = request.files['file']
        fname = secure_filename(file.filename)
        file.save(os.path.join('/tmp/', fname))

        client = storage.Client()
        bucket = client.bucket('raccolta-frame')
        source_file_name = fname
        destination_blob_name = source_file_name
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(os.path.join('/tmp/', fname))

################################################################################################
###################################### EMAIL INTRUDER ##########################################
################################################################################################

        if int(hour) >= 12 and int(value) >= 1 and int(sec) >= 54: #and sec >= 54:

            # and int(value) >= 1: // intanto prova orario + verifica se serve o no int
            #                      // invia una mail ogni volta che client invia un dato
            # if int(hour) >= 22 and int(hour) <6 and int(value) >= 1:

            ####funzione invio mail
            server = smtplib.SMTP(host='smtp.gmail.com', port=587)
            server.ehlo()
            server.starttls()
            # log
            server.login('ccp.project.22@gmail.com', 'claudiocomputing1!')

            # create msg AGGIUNGERE FORMAT CHE DICE QUALE SENSOR HA VISTO L'INTRUSO
            subject = 'SICUREZZA NEGOZIO'
            if int(value) == 1:
                b1 = "INTRUDER ALERT: La telecamera ha rilevato un'intrusione fuori orario consentito\n"
                b2 = "Rilevato {} intruso".format(value)
                body = b1+b2
            else:
                b1 = "INTRUDER ALERT: La telecamera ha rilevato un'intrusione fuori orario consentito\n"
                b2 = "Rilevati {} intrusi".format(value)
                body = b1+b2

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
@app.route('/informazioni', methods=['POST'])
def index2():
    idsens = request.form['id']  # prendo l'id dalla form
    db = firestore.Client()
    dati = []
    dati.append(['hour', 'value'])
    lasth = lh(idsens)
    for doc in db.collection(idsens).stream():
        x = doc.to_dict()
        if x['hour'] == lasth:
            dati.append([x['hms'], int(x['value'])])
    return render_template("profilo_sensore.html", dati=dati)

# ------------------------------ ACCESSO A MAGGIORI INFO DI UN SENSORE
@app.route('/database', methods=['POST'])
def index3():
    idsens = request.form['id']  # prendo l'id dalla form
    db = firestore.Client()
    dati = []
    for doc in db.collection(idsens).stream():
        x = doc.to_dict()
        key = idsens + "_" + x['all']
        dati.append([x['day'], x['month'], x['hms'], x['value'], key])
    return render_template("dati_sensore.html", dati=dati)

# ------------------------------ funzione automatica: segna l'ultima ora di funzione del sensore
def lh(id):
    db = firestore.Client()
    maxh = 0
    maxd = 0
    for doc in db.collection(id).stream():
        x = doc.to_dict()
        if x['day'] > maxd:
            maxd = x['day']
    for doc in db.collection(id).stream():
        x = doc.to_dict()
        if x['hour'] > maxh and x['day'] == maxd:
            maxh = x['hour']
    return maxh

# ------------------------------ VISUALIZZAZIONE IMMAGINE
@app.route('/imm', methods=['POST'])
def index4():
    idsenseimm = request.form['id']                  # prendo l'id dell immagine
    bucket_name = 'raccolta-frame'                   # nome bucket
    fname = "frame_{}.jpg".format(idsenseimm)        # nome frame

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(fname)
    blob.download_to_filename(os.path.join('/tmp/', fname))
    return send_file(os.path.join('/tmp/', fname), mimetype='image/jpeg')

#---------------------------------- REGISTRAZIONE NUOVO SENSORE E INVIO FILE
@app.route('/download')
def index5():
    return render_template("download.html")

@app.route('/salva',methods=('GET', 'POST'))
def index6():
    indirizzo = request.form['email']
    nreg = registra(indirizzo)

    # download file
#    buck_name = 'file_progetto'
#    destination_name = "dwn_read_to_start.txt"
#    souce_name = "read_to_start.txt"
#    download_blob(buck_name, destination_name, souce_name)

    dati = "il tuo sensore è il numero: {}".format(+nreg)
    return render_template("download2.html", dati=dati)

def registra(indirizzo):
    # ricerca numero iscrizione
    db = firestore.Client()
    nreg = 0
    for doc in db.collection("registrati").stream():
        nreg = nreg + 1
    # registrazione
    nreg = nreg + 1
    db.collection("registrati").document(indirizzo).set({'email': indirizzo, "sensor": nreg})
    return nreg

#def download_blob(bucket_name, source_blob_name, destination_file_name):
#    storage_client = storage.Client()
#    bucket = storage_client.bucket(bucket_name)
#    blob = bucket.blob(source_blob_name)
#    blob.download_to_filename(destination_file_name)
#    return 'ok'

# esecuzione flask sulla porta 8080
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
