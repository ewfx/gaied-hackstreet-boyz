import re
import unicodedata

def clean_text(text):
    """
    Cleans the extracted text by removing excessive spaces, unreadable characters, and normalizing.
    """
    text = text.strip()
    text = unicodedata.normalize("NFKD", text)  # Normalize Unicode characters
    text = re.sub(r"\s+", " ", text)  # Replace multiple spaces/newlines with a single space
    text = re.sub(r"[^a-zA-Z0-9\s.,]", "", text)  # Remove special characters except punctuation
    return text.lower()
