from umbral import SecretKey, Signer, CapsuleFrag, encrypt, decrypt_original, decrypt_reencrypted, generate_kfrags, reencrypt
from main import *
from random import sample
def gen_keys():
    secret_key = SecretKey.random()
    public_key = secret_key.public_key()
    return [public_key, secret_key]

def encrypt_text(text, public_key):
    binary_text = text.encode()
    capsule, ciphertext = encrypt(public_key, binary_text)
    return [capsule, ciphertext]

def decrypt_text(capsule, ciphertext, secret_key):
    binaryText = decrypt_original(secret_key, capsule, ciphertext)
    return binaryText.decode()

def grant_acess(owner_secret_key, owner_signer, receiving_public_key, required_frags, total_frags):
    return generate_kfrags( delegating_sk=owner_secret_key, 
                            receiving_pk=receiving_public_key, 
                            signer=owner_signer, 
                            threshold=required_frags, 
                            shares=total_frags
                        )
def check_cfrags(owner_verifying_key, owner_public_key, receiving_public_key, cfrags):
    suspicious_cfrags = [CapsuleFrag.from_bytes(bytes(cfrag)) for cfrag in cfrags]
    cfrags = [
        cfrag.verify(
            capsule, verifying_pk=owner_verifying_key,
            delegating_pk=owner_public_key, receiving_pk=receiving_public_key,
            )
        for cfrag in suspicious_cfrags
    ]
    return cfrags


if(__name__=="__main__"):
    # Creating my keys
    person = gen_keys()
    verifying_key, signer_key = gen_keys(); 
    my_signer = Signer(signer_key)
    print("Minha chave publica: ", person[0])
    print("Minha chave privada: ", person[1])
    print("Meu assinador: ", my_signer)
    text = input("Text to encrypt: ")

    # Encriptação
    capsule, ciphertext = encrypt_text(text, person[0])
    print(type(capsule))
    print("Capsula: ", capsule)
    print("Cifra: ", ciphertext)
    print("Descriptografado: ", decrypt_text(capsule, ciphertext, person[1]))

    # Creating keys for another person
    other_person = gen_keys()
    other_signer = Signer(other_person[1])
    # Granting acess
    all_kfrags = grant_acess(person[1], my_signer, other_person[0], 15, 45)
    
    # Trying to acess decrypt
    try:
        try_text = decrypt_text(capsule, ciphertext, other_person[1])
        print("Tentativa de Descriptografia: ", try_text)
    except: 
        print("Não foi possivel descriptografar")
    
    ## Reencription
    print("\nReencriptação: Início")
    other_capsule = capsule
    kfrags = sample(all_kfrags, 15) # Captura uma amostra dos kfrags, pois não pode possuir mais que 15
    cfrags = list() # Fragmentos de capsula de autoria do ohter_person
    for kfrag in kfrags:
        # Obtem o fragmento de capsula de other_person, via fragmento de kapsula de person
        cfrag = reencrypt(capsule = other_capsule, kfrag = kfrag) 
        cfrags.append(cfrag)
    cfrags = check_cfrags(verifying_key, person[0], other_person[0], cfrags)
    cleartext = decrypt_reencrypted(receiving_sk=other_person[1],
                                delegating_pk=person[0],
                                capsule=capsule,
                                verified_cfrags=cfrags,
                                ciphertext=ciphertext)
    print(cleartext.decode())
