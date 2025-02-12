from flask import Flask, request, jsonify
import PyPDF2
import subprocess
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Guardar texto del PDF en memoria (simulación de base de datos)
document_text = ""

# Función para extraer texto del PDF
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    return text


# Función para comunicarse con Ollama
def query_ollama(prompt):
    result = subprocess.run(
        ["ollama", "run", "mistral", prompt],
        capture_output=True,
        text=True,
        encoding="utf-8"  # Asegurar que el texto se decodifique correctamente
    )
    return result.stdout.strip()


# 🟢 Endpoint para conversar con la IA sin PDF
@app.route("/chat", methods=["POST"])
def chat_with_ai():
    data = request.get_json()
    message = data.get("message")

    if not message:
        return jsonify({"error": "No message provided"}), 400

    # Enviar mensaje a Mistral
    response = query_ollama(message)

    return jsonify({"response": response})

# 🟢 Endpoint para subir un PDF y extraer su texto
@app.route("/upload", methods=["POST"])
def upload_pdf():
    global document_text

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    document_text = extract_text_from_pdf(file_path)
    
    return jsonify({"message": "PDF uploaded successfully", "content": document_text[:500]})  # Muestra solo los primeros 500 caracteres

# 🟢 Endpoint para hacer preguntas al documento
@app.route("/ask", methods=["POST"])
def ask_question():
    global document_text

    if not document_text:
        return jsonify({"error": "No document uploaded"}), 400

    data = request.get_json()
    question = data.get("question")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Consultamos la IA con el contenido del PDF
    response = query_ollama(f"Basado en este documento: {document_text[:2000]} \n\n Responde la pregunta: {question}")
    
    return jsonify({"answer": response})

# 🔥 Iniciar servidor Flask correctamente
if __name__ == "__main__":
    app.run(debug=True)
