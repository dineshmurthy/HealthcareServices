from chatbot.bot import ChatBot
import pandas as pd

def main():
    # Load the training data from the CSV file
    data_path = "src/data/Nutrition2.csv"
    nutrition_data = pd.read_csv(data_path)

    # Initialize the chatbot with the data file
    chatbot = ChatBot(data_file=data_path)
    chatbot.train(nutrition_data)

    print("Chatbot is ready to answer your questions about nutrition!")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        response = chatbot.respond(user_input)
        print(f"Chatbot: {response}")

def rows_per_state(data_path):
    nutrition_data = pd.read_csv(data_path)
    state_counts = nutrition_data['State'].value_counts()
    return state_counts

if __name__ == "__main__":
    main()
    data_path = "src/data/Nutrition2.csv"
    print(rows_per_state(data_path))