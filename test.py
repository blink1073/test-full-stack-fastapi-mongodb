import requests


res = requests.get('http://127.0.0.1:8000/api/v1/users/all')
print(res.json())

json = dict(email='test@example.com', is_superuser=True, original="test@example.com")
#res = requests.post('http://127.0.0.1:8000/api/v1/users/', json=json)
requests.put('http://127.0.0.1:8000/api/v1/users/', json=json)
print(res.text)