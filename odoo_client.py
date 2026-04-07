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

    def _call_kw(self, model, method, args=None, kwargs=None):
        if not self.cookies:
            return None

        addr = f"{self.url}/web/dataset/call_kw"

        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": model,
                "method": method,
                "args": args or [],
                "kwargs": kwargs or {}
            }
        }

        try:
            res = requests.post(addr, json=payload, cookies=self.cookies, timeout=10)
            return res.json().get("result")
        except Exception as e:
            print(f"Odoo Call Error: {e}")
            return None

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
    
    def get_record_by_id(self, model, record_id, fields=None):
        result = self._call_kw(
            model=model,
            method="read",
            args=[[record_id]],
            kwargs={
                "fields": fields or []
            }
        )

        return result[0] if result else None

    def getPhoneBook(self):
        result = self._call_kw(
            model="sale.customer",
            method="search_read",
            args=[],
            kwargs={
                "fields": ["name", "phone_number", "note"]
            }
        )

        return result or []

    def update_field(self, model : str, record_id, field_name, new_value):
        result = self._call_kw(
            model=model,
            method="write",
            args=[[record_id], {field_name: new_value}]
        )
        return result is True

