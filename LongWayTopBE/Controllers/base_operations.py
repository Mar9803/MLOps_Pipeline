from flask import Flask, request, jsonify, current_app
from Service.DataService import csv_to_dataframe, save_dataset
from flask_cors import CORS


app = Flask(__name__, instance_relative_config=True)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:3000"]}})

@app.route('/')
def home():
    return "Welcome to Flask with Docker!"

# API che salva il file csv caricato dal client
@app.route('/api/upload', methods=['POST'])
def upload_file():

    if 'file_csv' not in request.files:
        return jsonify({"error": "Nessun file inviato"}), 400

    file = request.files['file_csv']

    current_app.logger.info(f"Ricevuto file: {file}")

    if file.filename == '':
        return jsonify({"error": "Nessun file selezionato"}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Il file deve essere un .csv"}), 400

    response_data, df_cleaned = csv_to_dataframe(file)
    
    if response_data is None:
        return jsonify({"error": "Errore nell'elaborazione del file"}), 500
    
    file_path = save_dataset(df_cleaned, file.filename)
    
    response_data.update({"file_path": file_path})

    return jsonify(response_data), 200

@app.route('/api/models', methods=['GET'])
def list_models():
    file_path = request.args.get("file_path")
    if not file_path:
        return jsonify({"error": "File path mancante"}), 400

    try:
        df = pd.read_csv(file_path)  # rileggi il dataset
        models = suggest_models(df)  # business logic nel service
        return jsonify({"models": models}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500    

# API che rilegge il file appena caricato e suggerisce il modello adatto
@app.route('/api/models/suggest', methods=['GET'])
def list_models():
    file_path = request.args.get("file_path")
    if not file_path:
        return jsonify({"error": "File path mancante"}), 400

    try:
        df = pd.read_csv(file_path)  # rileggi il dataset
        models = suggest_models(df)  # business logic nel service
        return jsonify({"models": models}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

def get_app():
    return app

