import requests
import json

class OdooClient:
    def __init__(self, url, db, username, password):
        self.url = url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.cookies = None
        self.uid = None

    def login(self):
        addr = f"{self.url}/web/session/authenticate"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "db": self.db,
                "login": self.username,
                "password": self.password
            }
        }
        try:
            res = requests.post(addr, json=payload, timeout=10)
            res.raise_for_status()
            result = res.json().get('result')
            if result:
                self.uid = result.get('uid')
                self.cookies = res.cookies
                return True
        except Exception as e:
            print(f"Login Error: {e}")
        return False
    
    def getPhoneBook(self):
        if not self.cookies:
            return []
            
        addr = f"{self.url}/web/dataset/call_kw"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": "sale.customer",
                "method": "search_read",
                "args": [],
                "kwargs": {
                    "fields": ["name", "phone_number", "note"]
                }
            }
        }
        try:
            res = requests.post(addr, json=payload, cookies=self.cookies, timeout=10)
            return res.json().get('result', [])
        except Exception as e:
            print(f"Fetch Error: {e}")
            return []
