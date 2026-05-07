from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os

# Importing Functions
from nerParser import extract_text
from nerEngine import get_entities
from fileRebuilder import rebuild_translated_pdf

app = Flask(__name__)

last_pdf_path = ""

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {"pdf", "docx"}
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Connection to UI
@app.route('/')
def home():
    return render_template('index.html')

@app.route("/upload", methods=["POST"])
def upload():
    global last_docx_path, last_pdf_path

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    mode = request.form.get("mode")

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
    
        try:
            if mode == "translate":

                translated_pdf = rebuild_translated_pdf(filepath)

                last_pdf_path = translated_pdf

                return jsonify({
                    "success": True,
                    "download": os.path.basename(translated_pdf)
                })
                    
            elif mode == "extract":
                parsed = extract_text(filepath)
                entities = get_entities(parsed)
                return jsonify(entities)


        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "Invalid file type"}), 400
    
@app.route("/download-pdf")
def download_pdf():
    global last_pdf_path

    if not last_pdf_path:
        return "No file available", 400

    return send_file(last_pdf_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)