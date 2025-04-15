from unittest.mock import patch
import requests

BASE_URL = "http://127.0.0.1:5000"

# Simulações das respostas que o servidor retornaria
mock_get_responses = {
    f"{BASE_URL}/": {"status_code": 200, "json": lambda: {"message": "Bem-vindo à API!"}},
    f"{BASE_URL}/api/produtos": {"status_code": 200, "json": lambda: ["banana", "maçã", "laranja"]},
    f"{BASE_URL}/api/supermercados": {"status_code": 200, "json": lambda: ["Lidl", "Continente", "Pingo Doce"]},
    f"{BASE_URL}/api/impacto": {"status_code": 200, "json": lambda: {"impacto_total": 3.5}},
}

mock_post_response = {
    "status_code": 201,
    "json": lambda: {"mensagem": "Encomenda criada com sucesso!"}
}

def mock_requests_get(url, *args, **kwargs):
    resp = mock_get_responses.get(url, {"status_code": 404, "json": lambda: {"erro": "Não encontrado"}})
    mock = type("MockResponse", (), {})()
    mock.status_code = resp["status_code"]
    mock.json = resp["json"]
    return mock

def mock_requests_post(url, *args, **kwargs):
    mock = type("MockResponse", (), {})()
    mock.status_code = mock_post_response["status_code"]
    mock.json = mock_post_response["json"]
    return mock

@patch("requests.get", side_effect=mock_requests_get)
@patch("requests.post", side_effect=mock_requests_post)
def run_tests(mock_get, mock_post):
    print("GET /")
    r = requests.get(f"{BASE_URL}/")
    print(f"Status: {r.status_code}")
    print("Resposta:", r.json(), "\n")

    print("GET /api/produtos")
    r = requests.get(f"{BASE_URL}/api/produtos")
    print(f"Status: {r.status_code}")
    print("Resposta:", r.json(), "\n")

    print("GET /api/supermercados")
    r = requests.get(f"{BASE_URL}/api/supermercados")
    print(f"Status: {r.status_code}")
    print("Resposta:", r.json(), "\n")

    print("POST /api/encomendas")
    payload = {
        "supermercado": "Continente",
        "produtos": [
            {"nome": "banana", "quantidade": 2},
            {"nome": "maçã", "quantidade": 1}
        ]
    }
    r = requests.post(f"{BASE_URL}/api/encomendas", json=payload)
    print(f"Status: {r.status_code}")
    print("Resposta:", r.json(), "\n")

    print("GET /api/impacto")
    r = requests.get(f"{BASE_URL}/api/impacto")
    print(f"Status: {r.status_code}")
    print("Resposta:", r.json(), "\n")

if __name__ == "__main__":
    run_tests()
