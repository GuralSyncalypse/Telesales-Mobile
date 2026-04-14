import requests
import json

class OdooClient:
    def __init__(self, base_url = "", db = "", username = "", password = ""):
        self.base_url = base_url.rstrip('/')
        self.db = db
        self.username = username
        self.password = password
        self.session = requests.Session() # Persists cookies automatically

    def _call_kw(self, model, method, args, kwargs=None):
        """
        Internal helper to handle the Odoo JSON-RPC payload structure.
        """
        if not self.cookies:
            return {"error": "Authentication required"}

        addr = f"{self.base_url}/web/dataset/call_kw"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": model,
                "method": method,
                "args": args,
                "kwargs": kwargs or {}
            }
        }

        try:
            res = self.session.post(addr, json=payload, timeout=10)
            res.raise_for_status() # Check for HTTP errors
            return res.json()
        except Exception as e:
            print(f"RPC Error ({method} on {model}): {e}")
            return None

    def login(self):
        addr = f"{self.base_url}/web/session/authenticate"
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
            res = self.session.post(addr, json=payload, timeout=10)
            res.raise_for_status()
            result = res.json().get('result')
            if result:
                self.cookies = res.cookies
                return True
        except Exception as e:
            print(f"Login Error: {e}")
        return False
    
    def get_record_by_id(self, model: str, record_id: int, fields: list = None):
        """
        Fetches a single record by its ID.
        :param fields: Optional list of field names to retrieve. 
                    If None, Odoo returns all accessible fields.
        """
        # Odoo 'read' expects: [ [ids], [fields] ]
        args = [[record_id]]
        kwargs = {"fields": fields} if fields else {}

        response = self._call_kw(model, "read", args, kwargs)

        if response and response.get('result'):
            # 'read' returns a list of dictionaries; 
            # since we passed one ID, we return the first element.
            return response['result'][0]
        
        return None

    def get_table(self, table: str, domain=[] , fields: list = None):
        """
        Fetches customer records using the centralized RPC helper.
        """
        
        if not table:
            return

        model = table
        method = "search_read"
        
        # search_read standard args are usually a domain filter [].
        args = [domain]

        # kwargs contains the list of fields to fetch.
        kwargs = {
            "fields": fields or []
        }

        response = self._call_kw(model, method, args=args, kwargs=kwargs)

        # Return the result list if it exists, otherwise an empty list
        return response.get('result', []) if response else []


    def update_field(self, model: str, record_id: int, field_name: str, new_value):
        # Odoo 'write' expects: [ [ids], {values_dict} ]
        args = [[record_id], {field_name: new_value}]
        
        response = self._call_kw(model, "write", args)
        
        # Odoo returns True on successful write
        return response.get('result') is True if response else False