Project Description



What we are trying to achieve:

&#x09;- To be able to translate legal case files from English to Malayalam using LLM models.

&#x09;- To run this project locally by hosting such LLM models in house.

&#x09;- To use user-defined translations, stored in a JSON dictionary, for fine-tuned translation results.

&#x09;- To extract entities using NER techniques from case files from courts.



Model used:

&#x09;- InLegalTrans-En2Indic-1B by law-ai, fine-tuned legal model based on IndicTrans2-en-indic-1B developed by ai4bharat.



Data Flow:

&#x09;User Uploads Case file -> User chooses an option: Extract or Translate ->



# 

# **Draft-2**



**Overview**

The project aims to provide a secure and efficient solution for translating sensitive legal documents using locally hosted AI models, ensuring data privacy and better control over document processing.



In addition to the translation system, the application includes a standalone Named Entity Recognition (NER) module capable of extracting entities such as names, locations, dates, organizations, and legal references from uploaded documents. The extracted data can be exported in JSON format for external use and analysis.



The system is developed using Python, Flask, and various PDF processing and Natural Language Processing (NLP) libraries to support secure legal document translation and document intelligence functionalities.





**What we are trying solve**

* Legal documents contain sensitive information that should not be processed using external cloud-based translation services.
* Manual translation of case files is time-consuming and may lead to inconsistencies in legal terminology and formatting.
* General translation systems often fail to accurately preserve legal references and document structure.
* Extracting important entities from unstructured legal documents requires significant manual effort.





**System Overview**



*Translation Module*

&#x09;The Translation Module processes and translates legal PDF documents using locally hosted AI translation models. Uploaded files are parsed using PyMuPDF, where text is extracted paragraph-by-paragraph for translation.



&#x09;Before translation, legal terms and case references are protected using placeholder tokens to preserve sensitive and domain-specific content. The text is then translated using a Transformer-based model integrated through the Hugging Face 	Transformers library and IndicTrans toolkit.



&#x09;After translation, protected terms are restored and the translated content is rebuilt into a new PDF while maintaining the original document structure and formatting. The module operates entirely on local hardware using PyTorch, with optional 	GPU acceleration for improved performance.



*NER Module*

&#x09;The NER Module is designed to extract structured entities from legal and official documents. Uploaded text is first normalized and cleaned to improve extraction accuracy.



&#x09;The module uses a hybrid extraction approach combining regex-based pattern matching, spaCy EntityRuler patterns, and a Transformer-based legal NER model to identify entities such as case numbers, FIR numbers, legal sections, names, 	organizations, locations, phone numbers, and vehicle numbers.



&#x09;Extracted entities from all methods are merged, validated, and formatted into structured JSON output for external processing, analysis, or integration with other systems.





**Technologies Used**

* Python - Core programming language used for backend development and AI model integration.
* Flask - Lightweight web framework used to build the application interface and manage server-side operations.
* Transformers Library - Used for running locally hosted AI translation models for multilingual document translation.
* Named Entity Recognition (NER) Pipeline – Implemented for extracting structured entities from uploaded documents.
* PyMuPDF - Used for PDF reading, text extraction, and document processing.
* HTML, CSS, and JavaScript - Used for developing the frontend user interface and interactive features.
* JSON - Used for dictionary management, entity storage, and configuration handling.
* Git \& GitHub - Used for version control, project tracking, and collaborative development.
* Natural Language Processing (NLP) - Applied for text processing, entity extraction, and translation-related operations.



