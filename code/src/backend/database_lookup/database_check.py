import logging
import psycopg2
from sentence_transformers import SentenceTransformer, util
import numpy as np
from data_preprocessing.data_construction import data_construction_func
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from utils import list_files_in_dir


# Load embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def create_requests_table():
    logging.info("Creating requests table...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id SERIAL PRIMARY KEY,
        text TEXT NOT NULL,
        request_type VARCHAR(255),
        sub_request_type VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    logging.info("Requests table created successfully.")

def provide_context(model, mapping, look_for_sample_dataset=True):
    context = []
    
    if look_for_sample_dataset:
        for x in list_files_in_dir("sample_dataset"):
            result = data_construction_func(model, mapping, x)
            if "error" in result:
                return f"Rate limit exceeded. Details: {result['details']}."
            else:
                context.append(data_construction_func(model, mapping, x))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT text, request_type, sub_request_type FROM requests")
    past_requests = cursor.fetchall()
    past_requests = [{"text": x[0], "request_type": x[1], "sub_request_type": x[2]} for x in past_requests]
    cursor.close()
    conn.close()
    
    context += past_requests
    logging.info("Context provided successfully.")
    return context

def find_similar_request(text, threshold=0.7):
    """Check PostgreSQL for similar past requests based on cosine similarity."""
    logging.info("Finding similar request...")
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch past requests
    cursor.execute("SELECT text, request_type, sub_request_type FROM requests")
    past_requests = cursor.fetchall()

    text_embedding = embed_model.encode(text, convert_to_tensor=True)

    best_match = None
    for past_text, req_type, sub_req_type in past_requests:
        past_embedding = embed_model.encode(past_text, convert_to_tensor=True)
        score = util.pytorch_cos_sim(text_embedding, past_embedding).item()

        if score >= threshold:
            best_match = {"text": past_text, "request_type": req_type, "sub_request_type": sub_req_type, "similarity": score}
            break

    cursor.close()
    conn.close()
    if best_match:
        logging.info(f"Similar request found: {best_match}")
    else:
        logging.info("No similar request found.")
    return best_match

def fed_data_into_db(text, request_type, sub_request_type):
    try:
        logging.info("Feeding data into the database...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO requests (text, request_type, sub_request_type) VALUES (%s, %s, %s)", (text, request_type, sub_request_type))
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Data fed into the database successfully.")
        return True
    except Exception as e:
        logging.error(f"Error: {e}")
        return False