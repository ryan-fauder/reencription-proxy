from umbral import Signer
from config import BASE_URL, SC_FILE_STORAGE, DOCTOR_FILE_STORAGE
from pprint import pprint
from umbral import * 
from encryption import *  
import json
import ipfs
def patient_create_record(content: bytes, patient_public_keys):
  capsule, ciphertext = [serializeFrom(bytes(i)) for i in encrypt(patient_public_keys, content)]
  obj = json.dumps({'capsule': capsule, 'content': ciphertext})
  return ipfs.add(obj)

def patient_grants_access(patient_secret_key, patient_signer, doctor_public_key, required_frags, total_frags):
  return grant_access(patient_secret_key, patient_signer, doctor_public_key, required_frags, total_frags)

def create_instance(content: bytes) -> None:
  patient_keys = keygen()
  doctor_keys = keygen()
  patient_signer_keys = keygen()
  patient_signer = Signer(patient_signer_keys['secret_key'])
  doctor_id = "1"
  record = "RECORD 1"
  key_frags = patient_grants_access(patient_keys['secret_key'], patient_signer, doctor_keys['public_key'], 1, 1)

  cid_record = patient_create_record(content, patient_keys['public_key'])
  print(f"O Record do paciente foi armazenado na IPFS em {cid_record}")

  data = {
    'doctor_id': doctor_id,
    'public_key_patient': serializeFrom(bytes(patient_keys['public_key'])),
    'public_key_signer_patient': serializeFrom(bytes(patient_signer_keys['public_key'])),
    'public_key_doctor': serializeFrom(bytes(doctor_keys['public_key'])), 
    'key_frag':  serializeListFrom(key_frags), 
    'link': cid_record
  }
  # Armazenando o pedido do SC em um arquivo
  with open(SC_FILE_STORAGE, 'w') as file:
      json.dump(data, file, indent=4)
  print("Arquivo do Contrato Inteligente foi criado")

  # Criando o armazenamento do Doutor:
  with open(DOCTOR_FILE_STORAGE, 'w') as file:
    keys = serializeKeys(doctor_keys)
    json.dump(keys, file, indent=4)
  
  print("Arquivo com as chaves do Doutor foi criado")

def test_instance():
  # Armazenando o pedido do SC em um arquivo
  with open(SC_FILE_STORAGE, 'r') as file:
      token_obj = json.load(file)
  print("Token obtido do armazenamento do SC")
  
  # Criando o armazenamento do Doutor:
  with open(DOCTOR_FILE_STORAGE, 'r') as file:
    doctor_key_encoded = json.load(file)
    doctor_keys = deserializeKeys(doctor_key_encoded)
  print("Chaves obtidas do armazenamento do doutor")

  public_key_patient = PublicKey.from_bytes(deserializeFrom(token_obj["public_key_patient"]))
  public_key_signer_patient = PublicKey.from_bytes(deserializeFrom(token_obj["public_key_signer_patient"]))
  public_key_doctor = PublicKey.from_bytes(deserializeFrom(token_obj["public_key_doctor"]))
  key_frag = deserializeListFrom(VerifiedKeyFrag.from_verified_bytes, token_obj["key_frag"])
  print("Token decodificado")
  

  ipfs_obj = ipfs.get(token_obj["link"])
  capsule = Capsule.from_bytes(deserializeFrom(ipfs_obj['capsule']))
  ciphertext = deserializeFrom(ipfs_obj['content'])
  print("Cifra e capsula obtidas do IPFS")

  cfrags = get_cfrags(public_key_signer_patient, public_key_patient, public_key_doctor, capsule, kfrags=key_frag)
  content: bytes = decrypt_reencrypted(
        verified_cfrags = cfrags,
        receiving_sk = doctor_keys["secret_key"], delegating_pk = public_key_patient,
        capsule = capsule, ciphertext = ciphertext
    )
  print("Conteudo decodificado por reencriptacao")
  return content

def main():
  with open("./examples/umbral-doc.pdf", "rb") as file:
    content = file.read()
    create_instance(content)

  content = test_instance()
  with open("./examples/pdf-example.pdf", "wb") as file:
    file.write(content)
  print("Conteudo escrito em um arquivo")

if(__name__=="__main__"):
  main()