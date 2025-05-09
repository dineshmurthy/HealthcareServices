import requests

class APIConnector:
    
    def __init__(self, base_url="https://marketplace.api.healthcare.gov/api/v1/"):
        self.base_url = base_url

    def fetch_data(self, endpoint, params=None):
        """
        Fetch data from the specified endpoint of the API.
        :param endpoint: The API endpoint to fetch data from.
        :param params: Optional parameters for the API call.
        :return: JSON response from the API.
        """
        apikey = "apikey=d687412e7b53146b2631dc01974ad0a4"
        url = f"{self.base_url}{endpoint}"
#        if params:
 #           url += f"{params}"
        url += apikey
        print(f"Fetching data from: {url}")  # Debug statement to check the URL

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from {url}: {e}")
            return None