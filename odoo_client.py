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

<<<<<<< Updated upstream
    def _call_kw(self, model, method, args=None, kwargs=None):
        if not self.cookies:
            return None

        addr = f"{self.url}/web/dataset/call_kw"

=======
    def _call_kw(self, model, method, args, kwargs=None):
        """
        Internal helper to handle the Odoo JSON-RPC payload structure.
        """
        if not self.cookies:
            return {"error": "Authentication required"}

        addr = f"{self.url}/web/dataset/call_kw"
>>>>>>> Stashed changes
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "model": model,
                "method": method,
<<<<<<< Updated upstream
                "args": args or [],
=======
                "args": args,
>>>>>>> Stashed changes
                "kwargs": kwargs or {}
            }
        }

        try:
            res = requests.post(addr, json=payload, cookies=self.cookies, timeout=10)
<<<<<<< Updated upstream
            return res.json().get("result")
        except Exception as e:
            print(f"Odoo Call Error: {e}")
=======
            res.raise_for_status() # Check for HTTP errors
            return res.json()
        except Exception as e:
            print(f"RPC Error ({method} on {model}): {e}")
>>>>>>> Stashed changes
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
    
<<<<<<< Updated upstream
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

=======
    def get_record_by_id(self, model: str, record_id: int, fields: list = None):
        """
        Fetches a single record by its ID.
        :param fields: Optional list of field names to retrieve. 
                    If None, Odoo returns all accessible fields.
        """
        # Odoo 'read' expects: [ [ids], [fields] ]
        args = [[record_id]]
        kwargs = {"fields": fields} if fields else {}

        response = self._execute_kw(model, "read", args, kwargs)

        if response and response.get('result'):
            # 'read' returns a list of dictionaries; 
            # since we passed one ID, we return the first element.
            return response['result'][0]
        
        return None

    def get_table(self, model: str, fields: list = None):
        """
        Fetches customer records using the centralized RPC helper.
        """
        model = "sale.customer"
        method = "search_read"
        
        # search_read standard args are usually a domain filter [].
        # kwargs contains the list of fields to fetch.
        kwargs = {
            "fields": ["name", "phone_number", "note"]
        }

        response = self._call_kw(model, method, args=[], kwargs=kwargs)

        # Return the result list if it exists, otherwise an empty list
        return response.get('result', []) if response else []

    def getPhoneBook(self):
        """
        Fetches customer records using the centralized RPC helper.
        """
        model = "sale.customer"
        method = "search_read"
        
        # search_read standard args are usually a domain filter [].
        # kwargs contains the list of fields to fetch.
        kwargs = {
            "fields": ["name", "phone_number", "note"]
        }

        response = self._call_kw(model, method, args=[], kwargs=kwargs)

        # Return the result list if it exists, otherwise an empty list
        return response.get('result', []) if response else []

    def update_field(self, model: str, record_id: int, field_name: str, new_value):
        # Odoo 'write' expects: [ [ids], {values_dict} ]
        args = [[record_id], {field_name: new_value}]
        
        response = self._call_kw(model, "write", args)
        
        # Odoo returns True on successful write
        return response.get('result') is True if response else False
>>>>>>> Stashed changes
