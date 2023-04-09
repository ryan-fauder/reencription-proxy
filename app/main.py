import requests
import json

PORT = 5050

def upload(data: dict) -> None:
  json_data = json.dumps(data)
  print(json_data)
  requests.post(f"http://127.0.0.1:{PORT}/text", data = json_data)

def download () -> dict:
  request = requests.get(f"http://127.0.0.1:{PORT}/text")

  data: str = request.text

  dict_data: dict = json.loads(data)

  return dict_data


if(__name__=="__main__"):
  data = {"capsule" : "capsule1", "ciphertext": "ciphertext1"}
  upload(data)
  response_data = download()
  print(response_data["capsule"])