import logging
from typing import List
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from data_preprocessing.text_extraction import extract_text
from database_lookup.database_check import create_requests_table, fed_data_into_db, find_similar_request, provide_context
from models import openai_llm, deepseek_llm, huggingface_zephyr_llm, gemini_llm
from classifier.llm_classifier import call_llm
import os
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


REQUEST_SUBREQUEST_MAP = {
    "Adjustment": [],
    "AU Transfer": [],
    "Closing Notice": ["Reallocation Fees", "Amendment Fees", "Reallocation Principal"],
    "Commitment Change": ["Cashless Roll", "Decrease", "Increase"],
    "Fee Payment": ["Ongoing Fee", "Letter of Credit Fee"],
    "Money Movement-Inbound": ["Principal", "Interest", "Principal+Interest", "Principal+Interest+Fee"],
    "Money Movement-Outbound": ["Timebound", "Foreign Currency"]
}


@app.post("/classify")
async def classify_request(email: UploadFile = File(...), attachments: List[UploadFile] = File(None)):
    try:
        model = gemini_llm
        
        create_requests_table()
        logging.info("Requests table created or verified")

        """Extract text, classify request type, and check for duplicates."""
        context = provide_context(model=model, mapping=REQUEST_SUBREQUEST_MAP, look_for_sample_dataset=True)
        
        if isinstance(context, str):
            return {"Error": context}
        
        logging.info("Context provided for classification")

        file_extension = os.path.splitext(email.filename)[1] or ".txt"  # Default to .txt if no extension
        file_location = f"uploads/{os.path.splitext(email.filename)[0]}{file_extension}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(email.file, buffer)
        logging.info(f"Email file saved at {file_location}")

        extracted_text = extract_text(file_location)
        logging.info("Text extracted from email")

        attachment_info = []
        if attachments:
            for attachment in attachments:
                attachment_path = f"uploads/{email.filename}_{attachment.filename}"
                with open(attachment_path, "wb") as buffer:
                    shutil.copyfileobj(attachment.file, buffer)

                attachment_text = extract_text(attachment_path)
                attachment_info.append(attachment_text)
                logging.info(f"Attachment {attachment.filename} processed")

        # Check for past similar cases
        similar_case = find_similar_request(extracted_text)
        logging.info("Checked for similar cases in the database")

        if attachment_info:
            extracted_text += f"\nAttachments content to this email is: {''.join(attachment_info)}. Consider this to classify the request more accurately.\nAttachments content should be deprioritized in case the request is clear from the email body itself."

        # Call LLM
        if not similar_case:
            logging.info("No similar case found, calling LLM for classification")
            llm_result = call_llm(model=model, text=extracted_text, allowed_types=REQUEST_SUBREQUEST_MAP, similar_cases=context)

            if "error" in llm_result:
                return {"Error": llm_result["error"]}
            
            if fed_data_into_db(extracted_text, llm_result["request_type"], llm_result["sub_request_type"]):
                logging.info("Data successfully fed into the database")
            else:
                logging.error("Error in feeding data into the database")

            return {
                "extracted_text": extracted_text,
                "duplicate_found": bool(similar_case),
                "request_type": llm_result["request_type"],
                "sub_request_type": llm_result["sub_request_type"],
                "reasoning": llm_result["reasoning"]
            }
        else:
            logging.info("Similar case found, returning similar case details")
            return {
                "extracted_text": extracted_text,
                "duplicate_found": bool(similar_case),
                "similar_text": similar_case["text"],
                "request_type": similar_case["request_type"],
                "sub_request_type": similar_case["sub_request_type"],
                "similarity": similar_case["similarity"],
            }
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"Error": "Something went wrong. Please try again after sometime."}