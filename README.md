# VerDex

> **AI-powered Legal Document Translation & Named Entity Recognition (NER)**
>
> Developed as a group project during an internship at the **IT Cell, High Court of Kerala**.

---

## 📖 Overview

**VerDex** is an AI-powered legal document processing system designed to improve the accessibility of English case files for Malayalam-speaking users.

The application translates English legal documents into Malayalam PDF files using modern Machine Learning techniques while also providing **Named Entity Recognition (NER)** extraction for downstream legal workflows.

To address data privacy and confidentiality requirements, the system is designed to **run entirely on a local machine** and is **not publicly hosted**.

Initially intended for use within the **High Court of Kerala**, the project is designed with future expansion for public access in mind.

---

## ✨ Features

* Translate English case files into Malayalam
* Generate translated documents in PDF format
* Extract Named Entities (NER) in JSON format
* Interactive and user-friendly web interface
* Runs completely offline for enhanced security
* Local AI inference without cloud processing
* REST API powered by Flask
* Optimized workflow for legal document processing

---

## 🤖 AI Model

VerDex currently uses:

**IndicTrans2.0 (1B Parameters)**

Developed by **AI4Bharat**, the model provides high-quality translation between Indian languages and English, making it well suited for legal document translation into Malayalam.

---

## 🛠 Tech Stack

| Technology                   | Purpose                   |
| ---------------------------- | ------------------------- |
| Python                       | Core Programming Language |
| Flask                        | Backend Web API           |
| HTML                         | User Interface            |
| CSS                          | Styling                   |
| JavaScript                   | Frontend Interaction      |
| AI4Bharat IndicTrans2.0 (1B) | Machine Translation       |
| Machine Learning             | Translation & NER         |
| JSON                         | Entity Extraction Output  |
| PDF Processing               | Document Generation       |

---

## ⚙️ How It Works

1. Upload an English legal case file.
2. Choose one of the available operations:

   * **Translate**
   * **Extract Named Entities**
3. The backend processes the document locally using AI models.
4. Receive either:

   * A translated Malayalam PDF
   * Named entities in JSON format

---

## 📸 Screenshots

### Home Interface

> *(Insert screenshot here)*

<br><br>

### Translation Workflow

> *(Insert screenshot here)*

<br><br>

### Malayalam PDF Output

> *(Insert screenshot here)*

<br><br>

### Named Entity Extraction

> *(Insert screenshot here)*

<br><br>

### JSON Output

> *(Insert screenshot here)*

---

## 📂 Proposed Project Structure

```text
VerDex/
│
├── app.py
├── requirements.txt
├── README.md
│
├── models/
│   ├── translation.py
│   ├── ner.py
│   └── model_loader.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── uploads/
│
├── outputs/
│   ├── translated_pdfs/
│   └── extracted_entities/
│
├── utils/
│   ├── pdf_handler.py
│   ├── file_utils.py
│   └── helpers.py
│
└── logs/
```

---

## 🚀 Running the Project

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Run the Flask application:

```bash
python app.py
```

The application runs locally through the Flask development server.

---

## 🔒 Privacy & Security

Legal case files often contain confidential information.

To preserve privacy and comply with security requirements:

* All processing occurs locally.
* No files are uploaded to external servers.
* No cloud-based inference is performed.
* AI models execute directly on the host machine.

This design makes VerDex suitable for environments where sensitive legal information must remain within institutional infrastructure.

---

## 🎯 Intended Users

Current target users include:

* High Court officials
* Judicial staff
* Legal researchers
* IT Cell personnel

The project has been designed with the possibility of future public deployment after further refinement.

---

## 📈 Future Improvements

* Higher-accuracy translation models
* Faster inference
* OCR support for scanned documents
* Batch document processing
* Additional Indian language support
* Searchable translated PDFs
* Improved legal terminology consistency
* Public deployment with secure authentication

---

## 📄 License

This repository is intended for educational and demonstration purposes unless otherwise specified.

---

## 👥 Credits

Developed as a collaborative internship project with Alan Sunny, at the **IT Cell, High Court of Kerala**.

Special thanks to our mentor Mr. Harikrishnan P V and other mentors for their guidance throughout the development process.
