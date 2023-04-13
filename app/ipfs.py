import requests
import json
from config import IPFS_BASE_URL

def add(file) -> str:
    response = requests.post(f"{IPFS_BASE_URL}/add", files={"file": file}, params={'cid-version': 1})

    if response.status_code != 200:
        print(f"Erro ao obter arquivo do IPFS: {response.content}")
        return

    data = json.loads(response.content)
    return data["Hash"]

def get(cid: str) -> dict:
    params = {'arg': cid, 'archive': True, 'compress': True}

    response = requests.post(f"{IPFS_BASE_URL}/get", params=params)
    if response.status_code != 200:
        print(f"Erro ao obter arquivo do IPFS: {response.content}")
        return
    try:
        import tarfile, io
        with tarfile.open(fileobj=io.BytesIO(response.content),mode='r:gz') as tar: #Compression Error
            filename = tar.getnames()[0]
            file = tar.extractfile(filename) # KeyError
            content: bytes = file.read()
        return json.loads(content)
    except tarfile.BadGzipFile:
        print("Erro ao obter arquivo do IPFS: Não foi possível realizar leitura do arquivo - Arquivo não é Gzip")
    except KeyError:
        print(f"Erro ao obter arquivo do IPFS: Não foi possível extrair arquivo {filename} - Arquivo não existe")

        
def main():
    file_path = "./examples/record.txt"
    with open(file_path, "rb") as file:
        cid = add(file)
        content = get(cid)
        print(content)

main()