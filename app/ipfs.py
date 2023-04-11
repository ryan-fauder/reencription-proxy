import requests
import json

# Define a URL da API Gateway do IPFS
ipfs_api_url = "http://127.0.0.1:8080/api/v0/add"

# Define o caminho do arquivo a ser enviado para o IPFS
file_path = "/path/to/file"

# Faz a requisição POST para enviar o arquivo para o IPFS
with open(file_path, "rb") as f:
    response = requests.post(ipfs_api_url, files={"file": f})
    
# Extrai o hash do arquivo do corpo da resposta
if response.status_code == 200:
    data = json.loads(response.content)
    hash = data["Hash"]
    print(f"Arquivo enviado com sucesso! Hash: {hash}")
else:
    print(f"Erro ao enviar arquivo para o IPFS: {response.content}")