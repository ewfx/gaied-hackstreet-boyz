import pymupdf  # PDF extraction
import docx
from mailparser import MailParser
from msg_parser import MsOxMessage
from data_preprocessing.data_cleaning import clean_text
import os

def extract_text_from_pdf(pdf_path):
    """Extract raw text from a PDF file."""
    try:
        doc = pymupdf.open(pdf_path)  # Explicit usage of PyMuPDF
        text = "\n".join([page.get_text() for page in doc])
        return clean_text(text)
    except Exception as e:
        return "Error in extracting text from PDF"

def extract_text_from_docx(docx_path):
    """Extract raw text from a DOCX file."""
    try:
        doc = docx.Document(docx_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return clean_text(text)
    except Exception as e:
        return "Error in extracting text from DOCX"

def extract_text_from_txt(txt_path):
    """Extract raw text from a TXT file."""
    try:
        with open(txt_path, "r", encoding="utf-8") as file:
            text = file.read()
        return clean_text(text)
    except Exception as e:
        return "Error in extracting text from TXT"

def extract_text_from_email(email_path):
    """Extract text and metadata from a .email or .eml file using mail-parser."""
    try:
        parser = MailParser()
        parser.parse_from_file(email_path)

        # Extract metadata
        subject = parser.subject or "No subject"
        sender = parser.from_[0][1] if parser.from_ else "Unknown sender"
        recipients = ", ".join([recipient[1] for recipient in parser.to]) if parser.to else "Unknown recipients"
        body = parser.text_plain[0] if parser.text_plain else "No content in email."

        # Combine metadata and body into a single text output
        text = f"Subject: {subject}\nSender: {sender}\nRecipients: {recipients}\n\n{body}"
        return text
    except Exception as e:
        return f"Error in extracting text from email: {str(e)}"
    
def extract_text_from_msg(msg_path):
    """Extract text and metadata from a .msg file using msg-parser."""
    try:
        msg = MsOxMessage(msg_path)
        subject = msg.subject or "No subject"
        sender = msg.sender or "Unknown sender"
        recipients = ", ".join(msg.recipients) if msg.recipients else "Unknown recipients"
        body = msg.body or "No content in email."

        # Combine metadata and body into a single text output
        text = f"Subject: {subject}\nSender: {sender}\nRecipients: {recipients}\n\n{body}"
        return text
    except Exception as e:
        return f"Error in extracting text from MSG: {str(e)}"

def convert_email_to_txt(email_path):
    """Convert .eml, .msg, or .email files to plain text."""
    try:
        # Read the content of the email file
        with open(email_path, "r", encoding="utf-8", errors="ignore") as file:
            content = file.read()

        # Create a temporary .txt file
        txt_path = email_path + ".txt"
        with open(txt_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(content)

        return txt_path
    except Exception as e:
        raise ValueError(f"Error converting email to text: {str(e)}")

def extract_text(file_path):
    """Extract and classify text from a file."""
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    elif file_path.endswith(".txt"):
        text = extract_text_from_txt(file_path)
    elif file_path.endswith(".msg") or file_path.endswith(".eml") or file_path.endswith(".email"):
        # Convert email to .txt and process it
        txt_path = convert_email_to_txt(file_path)
        text = extract_text_from_txt(txt_path)
        # Optionally, clean up the temporary .txt file
        os.remove(txt_path)
    else:
        raise ValueError("Unsupported file format")

    return text