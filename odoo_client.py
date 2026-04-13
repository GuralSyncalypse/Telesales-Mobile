import requests

class OdooClient:
    def __init__(self, base_url="", db="", api_key=""):
        self.base_url = f"{base_url.rstrip('/')}/json/2"
        self.db = db
        self.api_key = api_key
        self.session = requests.Session()

        # Set up standard headers for all calls
        self.session.headers.update({
            "Authorization": f"bearer {self.api_key}",
            "X-Odoo-Database": self.db,
        })

    def check_connection(self):
        """
        Attempts to fetch the current user's info to verify the API key.
        """
        # In JSON-2, calling 'read' on res.users without IDs 
        # often isn't enough, so we perform a search for 'me'.
        # A simple call to 'res.users' 'search_read' with limit 1 is a safe bet.
        payload = {
            "domain": [("id", "=", 1)], # Or any simple domain
            "fields": ["id"],
            "limit": 1
        }
        response = self._call("res.users", "search_read", payload)
        
        # If we get a list (even if empty), the key and DB are valid.
        # If the key is wrong, self._call will return None or raise an error.
        return response is not None

    def _call(self, model, method, payload=None):
        """
        Simplified helper for the new REST-like structure:
        URL: {base_url}/json/2/{model}/{method}
        """
        addr = f"{self.base_url}/{model}/{method}"
        print("Call!")
        try:
            # In JSON-2, you send the arguments directly in the body
            res = self.session.post(addr, json=payload or {}, timeout=10)
            res.raise_for_status()
            # JSON-2 returns the data directly, not wrapped in a 'result' key
            return res.json()
        except Exception as e:
            print(f"API Error ({method} on {model}): {e}")

            if res.status_code == 403:
            # This will print the actual Odoo error (e.g., "Access Denied by record rule")
                print(f"Detailed 403 Error: {res.text}")

            return None

    def get_record_by_id(self, model: str, record_id: int, fields: list = None):
        """
        Fetches a single record by its ID.
        JSON-2 'read' takes 'ids' and 'fields' directly in the body.
        """
        payload = {
            "ids": [record_id],
            "fields": fields or []
        }
        response = self._call(model, "read", payload)
        
        # Returns a list of records; we return the first one
        return response[0] if response and isinstance(response, list) else None

    def get_table(self, table: str, fields: list = None, domain=None):
        """
        Fetches records using search_read.
        """
        payload = {
            "domain": domain or [],
            "fields": fields or []
        }
        # Returns the list of records directly
        return self._call(table, "search_read", payload) or []

    def update_field(self, model: str, record_id: int, field_name: str, new_value):
        """
        Updates a record.
        JSON-2 'write' takes 'ids' and 'vals' keys.
        """
        payload = {
            "ids": [record_id],
            "vals": {field_name: new_value}
        }
        # Odoo 19 write returns True on success
        return self._call(model, "write", payload) is True