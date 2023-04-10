import requests
import json
import encryption
from config import BASE_URL
from umbral import Signer
from pprint import pprint

SC_FILE_STORAGE = "sc_storage.txt"
IPFS_URL = ""

def sc_generate_storage():
  patient_keys = encryption.keygen()
  doctor_keys = encryption.keygen()
  patient_signer_keys = encryption.keygen()
  patient_signer = Signer(patient_signer_keys['secret_key'])
  doctor_id="1"
  key_frags = patient_grants_acess(patient_keys['secret_key'], patient_signer, doctor_keys['public_key'], 1, 1)
  
  data = {
    'doctor_id': doctor_id,
    'public_key_patient': encryption.encode_publicKey(patient_keys['public_key']), 
    'public_key_doctor': encryption.encode_publicKey(doctor_keys['public_key']), 
    'key_frag':  encryption.encode_kfrags(key_frags), 
    'link': "ipfs"
  }

  # Armazenando no arquivo
  with open(SC_FILE_STORAGE, 'w') as file:
      json.dump(data, file, indent=4)

def sc_get_storage():
    with open(SC_FILE_STORAGE, 'r') as file:
      data = json.load(file)
    return data

def patient_grants_acess(patient_secret_key, patient_signer, doctor_public_key, required_frags, total_frags):
  return encryption.grant_acess(patient_secret_key, patient_signer, doctor_public_key, required_frags, total_frags)

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
  sc_generate_storage()
  # Ate esse momento, a requisicao do doutor foi processada pela SC
  # o SC ira pedir um token de acesso do medico para a proxy
  sc_request_data = sc_get_storage()

  print(sc_request_data['key_frag'])
  doctor_id = sc_request_data['doctor_id']
  key_frags = encryption.decode_kfrags(sc_request_data['key_frag'])
  access_token = sc_sends_request(sc_request_data)

  # Medico pede documento para a proxy
  doctor_data = {
    'doctor_id': doctor_id,
    'token': access_token
  }
  document = doctor_connects_proxy(doctor_data)
  patient_kfrags = encryption.decode_kfrags(document['data']['key_frag'])

  pprint(document['data'])
  print(patient_kfrags == key_frags)
if(__name__=="__main__"):
  main()