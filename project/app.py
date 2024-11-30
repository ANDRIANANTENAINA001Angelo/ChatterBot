from flask import Flask, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import json
import os

app = Flask(__name__)

# Initialisation du ChatBot
chatbot = ChatBot('MonProjetBot')
trainer = ListTrainer(chatbot)

# Chemin vers le fichier JSON contenant les données
JSON_FILE = 'chatbot.json'

# Charger ou créer le fichier JSON
if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

def load_data():
    """Charge les données du fichier JSON."""
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    """Sauvegarde les données dans le fichier JSON."""
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/train', methods=['POST'])
def train_chatbot():
    """
    Entraîner le chatbot à partir de paires question-réponse dans un fichier JSON.
    """
    try:
        data = load_data()
        if not data:
            return jsonify({"message": "Aucune donnée à entraîner."}), 400

        # Entraînement avec chaque paire du JSON
        for pair in data:
            trainer.train([pair['question'], pair['answer']])

        return jsonify({"message": "Chatbot entraîné avec succès."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    """
    Poser une question au chatbot et ajouter la paire question-réponse au fichier JSON.
    """
    try:
        # Récupérer la question depuis la requête
        input_data = request.json
        question = input_data.get('question', '').strip()

        if not question:
            return jsonify({"error": "Une question valide est requise."}), 400

        # Obtenir une réponse du chatbot
        response = chatbot.get_response(question).text

        # Charger les données existantes
        data = load_data()

        # Ajouter la nouvelle paire question-réponse
        new_pair = {"question": question, "answer": response}
        data.append(new_pair)

        # Sauvegarder les nouvelles données
        save_data(data)

        return jsonify({"question": question, "answer": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
