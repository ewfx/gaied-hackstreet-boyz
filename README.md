# 🚀 GEN AI Email and Document Classification System

## 📌 Table of Contents
- [Introduction](https://github.com/ewfx/gaied-hackstreet-boyz/blob/main/README.md#-introduction)
- [Demo](https://github.com/ewfx/gaied-hackstreet-boyz/blob/main/README.md#-demo)
- [Inspiration](https://github.com/ewfx/gaied-hackstreet-boyz/blob/main/README.md#-inspiration)
- [What It Does](https://github.com/ewfx/gaied-hackstreet-boyz/blob/main/README.md#%EF%B8%8F-what-it-does)
- [How We Built It](https://github.com/ewfx/gaied-hackstreet-boyz/blob/main/README.md#%EF%B8%8F-how-we-built-it)
- [Challenges We Faced](https://github.com/ewfx/gaied-hackstreet-boyz/blob/main/README.md#-challenges-we-faced)
- [How to Run](https://github.com/ewfx/gaied-hackstreet-boyz/blob/main/README.md#-how-to-run)
- [Tech Stack](https://github.com/ewfx/gaied-hackstreet-boyz/blob/main/README.md#%EF%B8%8F-tech-stack)
- [Team](https://github.com/ewfx/gaied-hackstreet-boyz/blob/main/README.md#-team)

---

## 🎯 Introduction
A Gen AI Email and Document Classification System is an AI-powered solution that automatically analyzes, categorizes, and organizes documents based on their content, structure, and context. Utilizing natural language processing (NLP) and machine learning, the system can classify documents into predefined categories Adjustment, AU Transfer, Closing Notice, Commitment Change, Fee Payment, Money Movement-Inbound, Money Movement-Outbound. It can extract key information, detect document intent, and in future route files to the appropriate workflows. This enhances efficiency, improves document retrieval, and streamlines business processes by reducing manual sorting and classification efforts.


## 🎥 Demo
📹 [Video Demo](https://github.com/ewfx/gaied-hackstreet-boyz/blob/main/artifacts/demo/Gaied-hackstreet-boyz.mov)  
🖼️ [Architecture](https://github.com/ewfx/gaied-hackstreet-boyz/blob/main/artifacts/arch/Flowchart.pdf)


## 💡 Inspiration
1. Automation & Efficiency:
Businesses receive vast amounts of emails and documents daily. Manually sorting them is time-consuming and prone to errors. AI-powered classification automates this process, reducing workload and improving response times.

2. Advancements in NLP & AI:
With breakthroughs in Natural Language Processing (NLP) and transformer models (e.g., GPT, BERT), AI can now understand context, intent, and semantics, enabling accurate classification and routing.

3. Compliance & Risk Management:
Many industries (finance, healthcare, legal) require proper document handling for compliance. AI ensures documents are categorized correctly, reducing regulatory risks and audit errors.

4. Enhanced Customer Experience:
Faster email triage means quicker responses to customer inquiries, leading to better satisfaction and engagement.

5. Integration with Workflow Systems:
AI-classified documents can be seamlessly integrated with CRM, ERP, and ticketing systems to automate business workflows.

6. Scalability & Cost Reduction:
AI-driven classification scales effortlessly with business growth, reducing dependency on manual labor and cutting operational costs.


## ⚙️ What It Does
The Document Classifier processes emails and their attachments to classify them into relevant request types and sub-request types using a combination of text extraction, embedding similarity checks, and LLM-based classification (Gemini Pro 1.5). 

* Key Features
   - Accepts emails and attachments as input
   - Extracts text from .pdf, .doc, .docx, and .eml files
   - Uniforms extracted text for consistency
   - Uses *Gemini Pro 1.5* to classify text into request types and sub-request types
   - Maintains a database of prior classified requests
   - Uses *cosine similarity (all-MiniLM-L6-v2)* to detect duplicate requests
   - If similarity threshold < 0.7, calls *Gemini LLM* for classification
   - Provides classification results with extracted text, request type, sub-request type, reasoning, and duplicate status

* Architecture Flow
   1. *Input Handling*: Accepts email and attachments at endpoint /classify
   2. *Text Extraction*: Parses files from a sample dataset for initial classification
   3. *Uniform Text Processing*: Ensures consistency in extracted content
   4. *Database Lookup*: Appends request types/sub-types from stored dataset
   5. *New Input Processing*: Parses the incoming email and attachments
   6. *Duplicate Check*: Compares embeddings with cosine similarity
   7. *Classification*:
      - If duplicate found (>0.7 similarity), retrieve past classification
      - If no duplicate, call *Gemini LLM* to classify the request
   8. *Output Response*: json format
      {
        "extracted_text": "...",
        "duplicate_found": true/false,
        "request_type": "...",
        "sub_request_type": "...",
        "reasoning": "..."
      }

* API Endpoint: /classify
   * Request:
      - *Method:* POST
      - *Input:* Email and Attachments
      - *Processing:* Extract text → Check duplicates → Classify using LLM

   * Response:
      - Extracted text
      - Duplicate request status
      - Predicted request and sub-request types
      - Reasoning behind classification
   This pipeline ensures efficient classification and prevents redundant request handlin


## 🛠️ How We Built It
* Frontend: React for building an interactive UI, Lucide React for icons, and Tailwind CSS for responsive and modern styling.
* Backend: FastAPI for building high-performance APIs, running on Uvicorn as the ASGI server.
* Database: PostgreSQL for efficient storage, retrieval, and management of classified emails and documents.
* LLM APIs: Integration with OpenAI, GEMINI, DeepSeek, or Hugging Face models for advanced text analysis, classification, and intent detection.


## 🚧 Challenges We Faced
1. Doing NER on the input which requires context to reduce load on llm.
2. API limits exhausted, limiting the acceptance testing.
3. Writing robust test cases.
4. Balancing work and hackathon coding.


## 🏃 How to Run
1. Clone the repository  
   ```sh
   git clone https://github.com/ewfx/gaied-hackstreet-boyz.git
   ```
2. Install dependencies  
   ```sh
   Install docker. Make sure docker destop or daemon is running.
   Make sure latest Python version is installed and added to PATH [Optopnal] 
   Install VScode or any favorite IDE which supports both Python and Javascript libraries. 
   ```
3. Create .env file in ./code/src/backend/ with below content. Note API keys has to be fetched by logging into respective portals. Primarily we are using Gemini.
   DEEPSEEK_API_KEY=https://platform.deepseek.com/api_keys
   OPENAI_API_KEY=https://platform.openai.com/api-keys
   HUGGINGFACE_API_KEY=https://huggingface.co/settings/tokens
   GEMINI_API_KEY=https://ai.google.dev/gemini-api/docs/api-key
   DB_USER=GaiedHackstreetBoyz
   DB_PASSWORD=randomchars
   DB_NAME=emails_db
   DB_HOST=database
   DB_PORT=5432

4. Run the project
   ```sh
   # Navigate to code/src directory via
   <code>cd ./code/src</code>
   # First time running or new python module has been added to requirements
   docker-compose up --build
   # Minor changes to file:
   docker-compose up --force-recreate
   Once the all the services are up, you can access http://localhost:3000/ from your favorite browser to view the landing page
   ```


## 🏗️ Tech Stack
- 🔹 Frontend: React + lucide react + Tailwind css
- 🔹 Backend: FastAPI + uvicorn
- 🔹 Database: PostgreSQL
- 🔹 Testing: Pytest for python and Jest for React.
- 🔹 Deployment: Docker compose for multi service build and deployment
- 🔹 LLM APIs: OpenAI / GEMINI / DeepSeek / HuggingFace 


## 👥 Team
- **Himesh Maniyar** - [GitHub](https://github.com/Himesh-29) | [LinkedIn](https://www.linkedin.com/in/himesh-maniyar/)
- **Abijith M G** - [GitHub](https://github.com/abijithmg) | [LinkedIn](https://www.linkedin.com/in/abijithmg/)
- **Sunny Jain** - [GitHub](https://github.com/sunny34) | [LinkedIn](https://www.linkedin.com/in/sunny-jain-54630636/)
- **Shyju Adumkudi** - [GitHub](https://github.com/) | [LinkedIn](https://www.linkedin.com/in/shyju-adumkudi-a75413a/)
