from config import BASE_URL, SC_FILE_STORAGE, DOCTOR_FILE_STORAGE
from pprint import pprint
import requests
import json
from encryption import *
from umbral import *

def get_storage(path):
    with open(path, 'r') as file:
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
  sc_request_data = get_storage(SC_FILE_STORAGE)

  print("SC requisita token de acesso")
  doctor_id = sc_request_data['doctor_id']
  key_frags = deserializeListFrom(VerifiedKeyFrag.from_verified_bytes, sc_request_data['key_frag'])
  access_token = sc_sends_request(sc_request_data)

  # Medico pede documento para a proxy
  doctor_data = {
    'doctor_id': doctor_id,
    'token': access_token
  }

  print("Doutor obtém suas informações")
  doctor_key_encoded = get_storage(DOCTOR_FILE_STORAGE)
  doctor_keys = deserializeKeys(doctor_key_encoded)

  print("Doutor inicia conexão com a proxy")
  response = doctor_connects_proxy(doctor_data)['data']

  print(response.keys())
  public_key_patient = PublicKey.from_bytes(deserializeFrom(response["public_key_patient"]))
  cfrags = deserializeListFrom(VerifiedCapsuleFrag.from_verified_bytes, response["cfrags"])
  capsule = Capsule.from_bytes(deserializeFrom(response["capsule"]))
  ciphertext = deserializeFrom(response["ciphertext"])

  print("Doutor decodifica o conteúdo")
  content: bytes = decrypt_reencrypted(
        verified_cfrags = cfrags,
        receiving_sk = doctor_keys["secret_key"], delegating_pk = public_key_patient,
        capsule = capsule, ciphertext = ciphertext
    )
  print("Conteudo decodificado por reencriptacao")
  with open("./examples/pdf-example.pdf", "wb") as file:
    file.write(content)
  print("Conteudo escrito em um arquivo")
if(__name__=="__main__"):
  main()

   