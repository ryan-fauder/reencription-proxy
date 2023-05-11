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
    data = [serializeFrom(bytes(item)) for item in iterable]
    return data

def deserializeListFrom(function, data: bytes) -> list:
    iterable = [deserializeFrom(item) for item in data]
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

def test():
    print("Testando a geração de chaves")
    person = keygen()
    print(f"OK - Chaves geradas")

    print("Testando a serializacao de chaves")
    serialized_person = serializeKeys(person)
    print(f"OK - {serialized_person}")

    content = "ESTE E UM CONTEUDO"
    print(f"Testando a encriptação e serializacao de informacoes: '{content}'")
    encrypted_content = encrypt(person["public_key"], content.encode())
    serialized_encrypted_content = serializeListFrom(encrypted_content)
    print(f"OK - {serialized_encrypted_content}")

    print(f"Testando a desserializacao das chaves")
    deserialized_person = deserializeKeys(serialized_person)
    print(f"OK - Pessoa desserializada {deserialized_person}")

    print(f"Testando a desserializacao de informacoes")
    iterable = pickle.loads(deserializeFrom(serialized_encrypted_content))
    deserialized_content = [Capsule.from_bytes(iterable[0]), iterable[1]]
    capsule, ciphertext = deserialized_content
    print(f"OK - Informacao desserializada")

    print(f"Testando a descriptografia")
    decrypted_content = decrypt_original(deserialized_person["secret_key"], capsule, ciphertext)
    print(f"OK - Descriptografado {decrypted_content}")

    print("-"*20)
    print(f"Testando a reencriptacao - Criando o assinador e pessoa para receber a permissao de reencriptar")
    signer_keys = keygen()
    signer = Signer(signer_keys["secret_key"])
    receiving_person = keygen()
    print(f"OK - Assinador e receiving_person gerados")
    
    print("-"*20)

    print(f"Testando a reencriptacao - Criando os fragmentos de chave privada (kfrag)")
    required_kfrag_amount = 1
    total_kfrag_amount = 3
    kfrags = grant_access(
        deserialized_person["secret_key"], signer, receiving_person["public_key"], 
        required_kfrag_amount, total_kfrag_amount
    )
    print(f"OK - Kfrags geradas")
    print(f"Testando a reencriptacao - Serializando kfrags")
    serialized_kfrags = serializeListFrom(kfrags)
    print(f"OK - Kfrags serializadas {serialized_kfrags}")
    print(f"Testando a reencriptacao - Desserializando kfrags")
    deserialized_kfrags = deserializeListFrom(VerifiedKeyFrag.from_verified_bytes, serialized_kfrags)
    print(f"OK - Kfrags deserializadas {deserialized_kfrags}")

    print("-"*20)

    print(f"Testando a reencriptacao - Obtendo fragmentos de capsula")
    cfrags = get_cfrags(
        signer_keys["public_key"], 
        deserialized_person["public_key"], receiving_person["public_key"],
        capsule, deserialized_kfrags,
    )
    print(f"OK - Cfrags obtidas")
    print(f"Testando a reencriptacao - Serializando cfrags")
    serialized_cfrags = serializeListFrom(cfrags)
    print(f"OK - Kfrags serializadas {serialized_cfrags}")
    print(f"Testando a reencriptacao - Desserializando cfrags")
    deserialized_cfrags = deserializeListFrom(VerifiedCapsuleFrag.from_verified_bytes, serialized_cfrags)
    print(f"OK - Cfrags deserializadas {deserialized_cfrags}")
    
    print("-"*20)

    print(f"Testando a reencriptacao - Testando a descriptacao")
    decrypted_reencrypted_content = decrypt_reencrypted(
        verified_cfrags = deserialized_cfrags,
        receiving_sk = receiving_person["secret_key"], delegating_pk = person["public_key"],
        capsule = capsule, ciphertext = ciphertext
    )
    print(f"OK - Descriptografia com reencriptacao {decrypted_reencrypted_content}")

if(__name__=="__main__"):
    test()