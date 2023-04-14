from config import BASE_URL, SC_FILE_STORAGE
from pprint import pprint
import requests
import json
import encryption


def sc_get_storage():
    with open(SC_FILE_STORAGE, 'r') as file:
      data = json.load(file)
    return data

def sc_sends_request(data: dict):
  json_data = json.dumps(data)
  request = requests.post(f"{BASE_URL}/resource", data = json_data)
  token_json = request.json()
  token: dict = json.loads(token_json)["data"]
  return token

def doctor_connects_proxy(data):
  json_data = json.dumps(data)
  request = requests.post(f"{BASE_URL}/record", data = json_data)
  result = request.json()
  dict_result: dict = json.loads(result)
  return dict_result

def main():
  # Ate esse momento, a requisicao do doutor foi processada pela SC
  # o SC ira pedir um token de acesso do medico para a proxy
  print("SC buscando todas as informações")
  sc_request_data = sc_get_storage()

  print("SC requisita token de acesso")
  doctor_id = sc_request_data['doctor_id']
  key_frags = encryption.decode_kfrags(sc_request_data['key_frag'])
  access_token = sc_sends_request(sc_request_data)

  # Medico pede documento para a proxy
  doctor_data = {
    'doctor_id': doctor_id,
    'token': access_token
  }

  print("Doutor inicia conexão com a proxy")
  document = doctor_connects_proxy(doctor_data)
  patient_kfrags = encryption.decode_kfrags(document['data']['key_frag'])
  print("Documento obtido")

  pprint(document['data'])
  print(patient_kfrags == key_frags)

if(__name__=="__main__"):
  main()

   