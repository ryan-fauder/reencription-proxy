from umbral import *
from random import sample
import base64
import pickle

def keygen(serialized = False):
    secret_key = SecretKey.random()
    public_key = secret_key.public_key()
    keys = {"public_key": public_key, "secret_key": secret_key}

    return serializeKeys(keys) if serialized else keys

def serializeKeys(keys = {}):
    try:
        secret_key = serializeFrom(keys["secret_key"].to_secret_bytes())
        public_key = serializeFrom(bytes(keys["public_key"]))
        return {"public_key": public_key, "secret_key": secret_key}
    except:
        print("serializeKeys error: Invalid keys")

def deserializeKeys(keys = {}):
    try:
        secret_key = SecretKey.from_bytes(deserializeFrom(keys["secret_key"]))
        public_key = PublicKey.from_bytes(deserializeFrom(keys["public_key"]))
        return {"public_key": public_key, "secret_key": secret_key}
    except:
        print("deserializeKeys error: Invalid keys")

def serializeFrom(data: bytes) -> str: 
    # Converte para um formato que pode ser transportado
    return base64.b64encode(data).decode('utf-8')

def deserializeFrom(data: str) -> bytes:
    # Converte para bytes, para que possa ser estruturado em um objeto
    return base64.b64decode(data.encode())

def serializeListFrom(iterable) -> str:
    # Converte uma lista para um formato que pode ser transportado
    data = [bytes(item) for item in iterable]
    return serializeFrom(pickle.dumps(data))

def deserializeListFrom(function, data: bytes) -> list:
    iterable = pickle.loads(deserializeFrom(data))
    return list(map(function, iterable))

def grant_access(owner_secret_key, owner_signer, receiving_public_key, 
    required_frags, total_frags):
    return generate_kfrags( 
        delegating_sk=owner_secret_key, receiving_pk=receiving_public_key,         
        signer=owner_signer, threshold=required_frags, shares=total_frags
    )

def get_cfrags(owner_verifying_key, owner_public_key, receiving_public_key, capsule, kfrags):
     # Captura uma amostra dos kfrags, pois não pode possuir menos que 15
    suspicious_cfrags = list() # Fragmentos de capsula de autoria do ohter_person
    for kfrag in kfrags:
        # Obtem o fragmento de capsula de other_person, via fragmento de kapsula de person
        cfrag = reencrypt(capsule, kfrag) 
        suspicious_cfrags.append(CapsuleFrag.from_bytes(bytes(cfrag)))

    cfrags = [
        cfrag.verify(
            capsule, verifying_pk=owner_verifying_key,
            delegating_pk=owner_public_key, receiving_pk=receiving_public_key,
            )
        for cfrag in suspicious_cfrags
    ]
    return cfrags