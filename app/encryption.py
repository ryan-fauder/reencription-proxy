from umbral import *
from random import sample
import base64

def keygen(encoded = False):
    secret_key = SecretKey.random()
    public_key = secret_key.public_key()
    keys = {"public_key": public_key, "secret_key": secret_key}
    if(encoded):
        keys = encode_keys(keys)
    return keys

def encode_keys(keys = {}):
    try:
        if(keys == {}): raise Exception("Error")
        secret_key = base64.b64encode(keys["secret_key"].to_secret_bytes()).decode('utf-8')
        public_key = base64.b64encode(bytes(keys["public_key"])).decode('utf-8')
        return {"public_key": public_key, "secret_key": secret_key}
    except:
        print("encode_key error: Invalid keys")

def decode_keys(keys = {}):
    try:
        if(keys == {}): raise Exception("Error")
        secret_key = SecretKey.from_bytes(base64.b64decode(keys["secret_key"].encode()))
        public_key = secret_key.public_key()
        return {"public_key": public_key, "secret_key": secret_key}
    except:
        print("decode_key error: Invalid keys")

def encode_publicKey(publicKey):
    try:
        publicKey_encoded = base64.b64encode(bytes(publicKey)).decode('utf-8')
        return publicKey_encoded
    except:
        print("encode_publicKey error: Invalid publicKeys")

def decode_publicKey(publicKey_encoded):
    try:
        publicKey = PublicKey.from_bytes(base64.b64decode(publicKey_encoded.encode()))
        return publicKey
    except:
        print("encode_key error: Invalid keys")

def encode_kfrags(kfrags = []):
    try:
        kfrag_bytes_list = [bytes(kfrag) for kfrag in kfrags]
        kfrags_joined_bytes = b'-\\-#-\\-'.join(kfrag_bytes_list)
        kfrags_encoded = base64.b64encode(kfrags_joined_bytes).decode('utf-8')
        return kfrags_encoded
    except:
        print("encode_kfrag error: Invalid kfrags")

def decode_kfrags(kfrags_encoded = []):
    try:
        kfrags_joined_bytes = base64.b64decode(kfrags_encoded.encode())
        kfrag_bytes_list = kfrags_joined_bytes.split(b'-\\-#-\\-')
        kfrags = [VerifiedKeyFrag.from_verified_bytes(kfrag_bytes) for kfrag_bytes in kfrag_bytes_list]
        return kfrags
    except:
        print("decode_key error: Invalid keys")

def encrypt_bytes(bytes_obj, public_key, encoded = False):
    capsule, ciphertext = encrypt(public_key, bytes_obj)
    if(encoded):
        capsule = base64.b64encode(bytes(capsule)).decode('utf-8')
        ciphertext = base64.b64encode(ciphertext).decode('utf-8')
    return [capsule, ciphertext]

def decode_capsule(capsule):
    return Capsule.from_bytes(base64.b64decode(capsule.encode()))

def decode_cipher(ciphertext):
    return base64.b64decode(ciphertext.encode())

def decrypt_bytes(capsule, ciphertext, secret_key) -> bytes:
    bytes_obj = decrypt_original(secret_key, capsule, ciphertext)
    return bytes_obj

def grant_acess(owner_secret_key, owner_signer, receiving_public_key, required_frags, total_frags):
    return generate_kfrags( delegating_sk=owner_secret_key, 
                            receiving_pk=receiving_public_key, 
                            signer=owner_signer, 
                            threshold=required_frags, 
                            shares=total_frags
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

def decrypt_reencrypted_bytes(receiving_secret_key, owner_public_key, capsule, cfrags, ciphertext ):
    return decrypt_reencrypted(
                                receiving_sk = receiving_secret_key,
                                delegating_pk = owner_public_key,
                                capsule = capsule,
                                verified_cfrags = cfrags,
                                ciphertext = ciphertext
                                )


if(__name__=="__main__"):
    # Creating my keys
    # Paciente
    person = keygen()
    signer_keys = keygen()
    verifying_key, signer_key = signer_keys["public_key"], signer_keys["secret_key"] 
    my_signer = Signer(signer_key)
    
    print("Minha chave publica: ", person["public_key"])
    print("Minha chave privada: ", person["secret_key"])
    print("Meu assinador: ", my_signer)

    text = input("Text to encrypt: ")
    # Encriptação
    # Armazenados no IPFS com o formato:
    # record = {
    #     "key" = "....", // capsule
    #     "content" = "....", // cipher
    # }
    capsule, ciphertext = encrypt_bytes(text.encode(), person["public_key"])
    print(type(capsule))
    print("Capsula: ", capsule)
    print("Cifra: ", ciphertext)

    print("Descriptografado: ", decrypt_bytes(capsule, ciphertext, person["secret_key"]).decode())
    
    # Creating keys for another person
    # Medico
    other_person = keygen()
    other_signer = Signer(other_person["secret_key"])

    # Medico pede o documento e informa o identificador

    # Paciente dá o acesso e envia os kfrags para o SC
    all_kfrags = grant_acess(person["secret_key"], my_signer, other_person["public_key"], 1, 3)
    
    # Proxy obtem a capsule, cipher do sqlite
    # Proxy obtem kfrags do SC
    
    kfrags = sample(all_kfrags, 1)
    cfrags = get_cfrags(
        verifying_key,
        person["public_key"],
        other_person["public_key"], 
        capsule,
        kfrags,
        )
    # Proxy precisa retornar ao medico:
    # record = {
    #     "key" = "....", // capsule
    #     "content" = "....", // cipher
    #     "frags" = "...." // cfrags
    # }
    # Medico
    cleartext = decrypt_reencrypted(
                                receiving_sk = other_person["secret_key"],
                                delegating_pk = person["public_key"],
                                capsule = capsule,
                                verified_cfrags = cfrags,
                                ciphertext = ciphertext
                                )
    print(cleartext.decode())
