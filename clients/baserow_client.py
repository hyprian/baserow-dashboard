# clients/baserow_client.py

import requests
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class BaserowClient:
    def __init__(self, api_token, base_url):
        self.base_url = base_url.rstrip('/')
        self.headers = {"Authorization": f"Token {api_token}"}
        if not api_token:
            raise ValueError("Baserow API token is required.")

    def _get_all_rows(self, table_id):
        """Fetches all rows from a table with pagination."""
        all_rows = []
        page = 1
        while True:
            # Using size=200, the max allowed, for efficiency
            url = f"{self.base_url}/api/database/rows/table/{table_id}/?user_field_names=true&page={page}&size=200"
            try:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])
                all_rows.extend(results)
                # If there is no 'next' link, we've reached the last page
                if not data.get("next"):
                    break
                page += 1
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching data from Baserow table {table_id}: {e}")
                return None
        return all_rows

    def get_table_as_dataframe(self, table_id):
        """Gets a full table and returns it as a pandas DataFrame."""
        rows = self._get_all_rows(table_id)
        if rows is None:
            return pd.DataFrame()
        return pd.DataFrame(rows)

# Note: The other methods like batch_create_rows are not needed for this project
# but it's fine to leave them in the client file.