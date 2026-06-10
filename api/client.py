import requests


class APIClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or "http://localhost:5000"
        self.session = requests.Session()

    def login(self, username, password):
        r = self.session.post(f"{self.base_url}/api/login", json={"username": username, "password": password})
        return r.json() if r.ok else None

    def get(self, path):
        r = self.session.get(f"{self.base_url}{path}")
        return r.json() if r.ok else None

    def post(self, path, data=None):
        r = self.session.post(f"{self.base_url}{path}", json=data or {})
        return r.json() if r.ok else None

    def put(self, path, data=None):
        r = self.session.put(f"{self.base_url}{path}", json=data or {})
        return r.json() if r.ok else None

    def delete(self, path):
        r = self.session.delete(f"{self.base_url}{path}")
        return r.ok
