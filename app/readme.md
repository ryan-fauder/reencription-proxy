# App

## Public Gateway para IPFS

https://cloudflare-ipfs.com/ipfs/


## DAG function

````py
def dag():

    # Criando um nó DAG vazio
    empty_node = {
        "Links": []
    }

    # Convertendo o nó para o formato JSON
    empty_node_json = json.dumps(empty_node)

    # Adicionando o nó ao IPFS
    response = requests.post('http://localhost:5001/api/v0/dag/put?input-enc=json', data=empty_node_json)

    # Obtendo o CID do DAG vazio
    cid = response.json()['Cid']['/']

    # Adicionando um arquivo ao DAG
    response = requests.post(f'http://localhost:5001/api/v0/add?pin=false&quieter=true&cid-version=1&hash=sha2-256', files={'file': open(file_path, 'rb')})

    # Obtendo o CID do arquivo adicionado
    file_cid = response.json()['Hash']

    # Criando um nó para o arquivo
    file_node = {
        "Links": [
            {
                "Name": "exemplo.txt",
                "Hash": file_cid,
                "Size": response.json()['Size']
            }
        ]
    }

    # Convertendo o nó para o formato JSON
    file_node_json = json.dumps(file_node)

    # Adicionando o nó do arquivo ao DAG vazio
    response = requests.post(f'http://localhost:5001/api/v0/dag/put?input-enc=json&cid-version=1&hash=sha2-256', data=file_node_json)

    # Obtendo o CID do DAG raiz
    dag_cid = response.json()['Cid']['/']

    print(dag_cid)


```