from requests import get, post

base_url = 'https://tuttiinsieme.ew.r.appspot.com/'

#questo da un secondo computer dovrebbe funzionare per chiedere i dati dal server

#questa è una richiesta con url legata alla funzione main del server,
#che chiede la lsita dei sensori/chiavi del dizionario data
r = get(f'{base_url}/sensors')
sensors = r.json()
print(sensors)

#per ogni sensore/chiave del dizionario database
#chiama l'ulr associato alla funzione che manda i dati dei sensoti
#e la richiesta viene fatta per ogni sensore, quindi è una funzione che chiede tutti i dati
for s in sensors:
    r = get(f'{base_url}/sensors/{s}')
    print(s,r.json())