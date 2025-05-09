import pandas as pd
import requests
from src.chatbot.api_connector import APIConnector
from tabulate import tabulate  # Import the tabulate library
import json  # Import the json library

class CMSService:
    def __init__(self, data_file):
        self.data_file = data_file
        self.data = pd.read_csv(data_file)
        self.api_connector = APIConnector()

    def fetch_healthcare_data(self, endpoint, params=None):
        """
        Fetch data from the healthcare API.
        :param endpoint: The API endpoint to fetch data from.
        :param params: Optional parameters for the API call.
        :return: JSON response from the API.
        """
        return self.api_connector.fetch_data(endpoint, params)

    def query_api_data(self, api_data, query_key):
        """
        Query the JSON output from the API data.
        :param api_data: The JSON data returned by the API.
        :param query_key: The key to search for in the JSON data.
        :return: Extracted information or a message if the key is not found.
        """
        if not isinstance(api_data, dict):
            return "Invalid API data format. Expected a JSON object."

        results = []
        def recursive_search(data, key):
            if isinstance(data, dict):
                for k, v in data.items():
                    if k == key:
                        results.append(v)
                    elif isinstance(v, (dict, list)):
                        recursive_search(v, key)
            elif isinstance(data, list):
                for item in data:
                    recursive_search(item, key)

        recursive_search(api_data, query_key)
        if results:
            return results
        else:
            return f"No results found for key: {query_key}"

    def train(self, data):
        # Extract metadata from the first row
        self.metadata = data.iloc[0]
        print("Metadata:", self.metadata)

        # Training logic: Read all rows except the first row
        self.training_data = data.iloc[1:]
        print("Training data loaded successfully.")

        # Create a simple keyword-based index for quick lookup
        self.index = {}
        for i, row in self.training_data.iterrows():
            for col in self.training_data.columns:
                if pd.notna(row[col]):
                    keywords = str(row[col]).lower().split()
                    for keyword in keywords:
                        if keyword not in self.index:
                            self.index[keyword] = []
                        self.index[keyword].append(row)

    def respond(self, user_input):
        # Response generation logic
        keywords = user_input.lower().split()
        matched_rows = []
        for keyword in keywords:
            if keyword in self.index:
                matched_rows.extend(self.index[keyword])

        if matched_rows:
            # For simplicity, return the first matched row
            response = matched_rows[0].to_dict()
            return f"Found matching data: {response}"
        else:
            return "Sorry, I don't have information on that."

# Example usage
if __name__ == "__main__":
    data_path = "src/data/Nutrition2.csv"
    chatbot = CMSService(data_file=data_path)

    # Fetch data from the healthcare API
    endpoint = input("Enter the API endpoint to fetch data from (e.g., 'plans'): ")
    params = input("Enter any parameters for the API call (e.g., 'state=CA'): ")

    print("Fetching data from healthcare API...")
    api_data = chatbot.fetch_healthcare_data(endpoint, params)
    if api_data:
        print("Healthcare API Data fetched successfully!")

        # Print the API data in JSON format
        print("API Data in JSON format:")
        print(json.dumps(api_data, indent=4))  # Pretty-print the JSON data

        # Query the API data in a loop
        while True:
            query_key = input("Enter the key to query in the API data (e.g., 'plan_name') or type 'exit' to quit: ")
            if query_key.lower() == "exit":
                print("Exiting the query loop. Goodbye!")
                break
            query_results = chatbot.query_api_data(api_data, query_key)
            
            # Format the results as a table
            if isinstance(query_results, list) and query_results:
                print(tabulate([[i + 1, result] for i, result in enumerate(query_results)], headers=["Index", "Result"], tablefmt="grid"))
            else:
                print("Query Results:", query_results)

        # Generate HTML table for api_data
        html_file_path = "index.html"

        if isinstance(api_data, dict):
            rows = "".join(
                f"<tr><td>{i + 1}</td><td>{key}</td><td>{value}</td></tr>"
                for i, (key, value) in enumerate(api_data.items())
            )
        elif isinstance(api_data, list):
            rows = "".join(
                f"<tr><td>{i + 1}</td><td>{item}</td><td>{json.dumps(item, indent=4)}</td></tr>"
                for i, item in enumerate(api_data)
            )
        else:
            rows = f"<tr><td>1</td><td>Data</td><td>{api_data}</td></tr>"

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>API Data Results</title>
            <link rel="stylesheet" href="results.css">
        </head>
        <body>
            <div class="container">
                <h1>API Data Results</h1>
                <table>
                    <thead>
                        <tr>
                            <th>Index</th>
                            <th>Key</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """

        # Write the HTML content to the file
        with open(html_file_path, "w", encoding="utf-8") as html_file:
            html_file.write(html_content)

        print(f"API data has been written to {html_file_path}. Open this file in a browser to view the results.")
