from flask import Flask, render_template, request, jsonify
from src.chatbot.bot import CMSService
import pandas as pd
import openai
import logging

app = Flask(__name__)

# Initialize the chatbot
data_path = "src/data/Nutrition2.csv"
cmssvc = CMSService(data_file=data_path)  # Ensure this is correctly initialized
print(f"Type of chatbot: {type(cmssvc)}")  # Debugging: Check the type of chatbot

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/plans", methods=["GET", "POST"])
def plans():
    results = None
    if request.method == "POST":
        selected_option = request.form.get("option")
        if selected_option == "option2":
            # Call fetch_healthcare_data with "option2" as the endpoint
            endpoint = "option2"
            results = services.fetch_healthcare_data(endpoint)
    return render_template("plans.html", results=results)

@app.route("/query", methods=["POST"])
def query():
    api_data = request.json.get("api_data")
    query_key = request.json.get("query_key")
    if not api_data or not query_key:
        return jsonify({"error": "Invalid input"}), 400

    query_results = chatbot.query_api_data(api_data, query_key)
    return jsonify({"results": query_results})

@app.route("/fetch_data", methods=["POST"])
def fetch_data():
    selected_option = request.form.get("option")
    results = None

    try:
        if selected_option == "option1":
            params = request.form.get("zipcode")
            endpoint = "/counties/by/zip/" + params + "?"
        elif selected_option == "option2":
            params = request.form.get("planyear")
            endpoint = "plans/" + request.form.get("planid") + "?year=" + params + "&"
        elif selected_option == "option3":
            params = request.form.get("state")
            endpoint = "states/" + params + "?"
        elif selected_option == "option4":
            params = request.form.get("medicationname")
            endpoint = "drugs/autocomplete?q=" + params + "&"
        elif selected_option == "option5":
            params = request.form.get("state")
            endpoint = "states/" + params + "?"
        else:
            return "Invalid option selected", 400

        print(f"Endpoint : {endpoint}")
        print(f"Params : {params}")
        results = cmssvc.fetch_healthcare_data(endpoint, params)
    except AttributeError as e:
        print(f"Error: {e}")
        return f"An error occurred: {e}", 500

    return render_template("plans.html", results=results)

@app.route("/codes", methods=["GET", "POST"])
def codes():
    results = None
    categories = None
    if request.method == "POST":
        selected_option = request.form.get("option")
        if selected_option == "list_all":
            # Read all data from DHSCodes.xlsx
            df = pd.read_excel("src/DHSCodes.xlsx")
            results = df.to_dict(orient="records")  # Convert to a list of dictionaries
        elif selected_option == "list_by_category":
            # Retrieve unique values from the Category column
            df = pd.read_excel("src/DHSCodes.xlsx")
            categories = df["Category"].dropna().unique().tolist()  # Get unique non-null values
    return render_template("codes.html", results=results, categories=categories)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        openai.api_key = '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'
        response = openai.ChatCompletion.create(
            #model="gpt-3.5-turbo",
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        ai_message = response.choices[0].message['content'].strip()
        return jsonify({'message': ai_message})
    except openai.error.InvalidRequestError as e:
        logging.error(f"OpenAI API error: {e}")
        return jsonify({'error': f"OpenAI API error: {e}"}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': f"Unexpected error: {e}"}), 500

@app.route("/services")
def services():
    return render_template("ChatServices.html")

if __name__ == "__main__":
    app.run(debug=True)