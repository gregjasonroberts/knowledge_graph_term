# fred_loader.py
import os
import requests

class FREDLoader:
    """
    Fetches time series observations from FRED via the /fred/series/observations endpoint.
    Expects your FRED_API_KEY in the environment.
    """
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ["FRED_API_KEY"]
        self.base_url = "https://api.stlouisfed.org/fred/series/observations"

    def fetch_observations(self, series_id, start=None, end=None):
        params = {
            "series_id": series_id,
            "api_key": self.api_key,
            "file_type": "json"
        }
        if start:
            params["observation_start"] = start
        if end:
            params["observation_end"] = end

        resp = requests.get(self.base_url, params=params, timeout=10)
        resp.raise_for_status()
        payload = resp.json()

        # The JSON comes back under the "observations" key
        return payload.get("observations", [])

    def store_series(self, handler, series_id, start=None, end=None):
        """
        Pulls all observations for the given series and writes to Neo4j
        using handler.store_indicator(series_id, date, value).
        """
        observations = self.fetch_observations(series_id, start, end)
        for obs in observations:
            date = obs["date"]            # e.g. "2025-04-30"
            value = obs["value"]          # e.g. "99.4" or "." if missing
            if value == ".":
                continue                  # skip missing data points
            handler.store_indicator(
                indicator_id=series_id,
                date=date,
                value=float(value)
            )
