import pytest
from unittest.mock import patch, MagicMock
import psycopg2
from data_preprocessing.data_cleaning import clean_text
from data_preprocessing.text_extraction import extract_text
from data_preprocessing.data_construction import data_construction_func
from database_lookup.database_check import (
    get_db_connection,
    create_requests_table,
    provide_context,
    find_similar_request,
    fed_data_into_db,
)
from classifier.llm_classifier import call_llm


@patch("database_lookup.database_check.psycopg2.connect")
def test_get_db_connection(mock_connect):
    mock_connect.return_value = MagicMock()
    conn = get_db_connection()
    mock_connect.assert_called_once()
    assert conn is not None


@patch("database_lookup.database_check.get_db_connection")
def test_create_requests_table(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    create_requests_table()

    mock_get_db_connection.assert_called_once()
    mock_conn.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once_with(
        """
    CREATE TABLE IF NOT EXISTS requests (
        id SERIAL PRIMARY KEY,
        text TEXT NOT NULL,
        request_type VARCHAR(255),
        sub_request_type VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("database_lookup.database_check.get_db_connection")
@patch("database_lookup.database_check.list_files_in_dir")
@patch("database_lookup.database_check.data_construction_func")
def test_provide_context(mock_data_construction_func, mock_list_files_in_dir, mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [("text1", "type1", "subtype1")]
    mock_list_files_in_dir.return_value = ["file1", "file2"]
    mock_data_construction_func.side_effect = lambda model, mapping, x: {"file": x}

    context = provide_context("model", "mapping", look_for_sample_dataset=True)

    mock_list_files_in_dir.assert_called_once_with("sample_dataset")
    mock_data_construction_func.assert_any_call("model", "mapping", "file1")
    mock_data_construction_func.assert_any_call("model", "mapping", "file2")
    mock_get_db_connection.assert_called_once()
    mock_conn.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once_with("SELECT text, request_type, sub_request_type FROM requests")
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
    assert len(context) == 3  # 2 from sample dataset + 1 from DB

@patch("database_lookup.database_check.get_db_connection")
def test_fed_data_into_db(mock_get_db_connection):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    result = fed_data_into_db("test_text", "type1", "subtype1")

    mock_get_db_connection.assert_called_once()
    mock_conn.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO requests (text, request_type, sub_request_type) VALUES (%s, %s, %s)",
        ("test_text", "type1", "subtype1"),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
    assert result is True

def test_clean_text():
    # Test for normalizing Unicode characters
    assert clean_text("Café") == "cafe"
    
    # Test for removing excessive spaces
    assert clean_text("This   is   a   test.") == "this is a test."
    
    # Test for removing special characters except punctuation
    assert clean_text("Hello! How's it going?@#$%^&*") == "hello hows it going"
    
    # Test for handling newlines and tabs
    assert clean_text("Line1\nLine2\tLine3") == "line1 line2 line3"
    
    # Test for empty string
    assert clean_text("") == ""
    
    # Test for string with only special characters
    assert clean_text("@#$%^&*()") == ""

@patch("data_preprocessing.text_extraction.docx.Document")
def test_extract_text_from_docx(mock_docx):
    mock_doc = MagicMock()
    mock_doc.paragraphs = [MagicMock(text="Paragraph 1"), MagicMock(text="Paragraph 2")]
    mock_docx.return_value = mock_doc
    result = extract_text("sample.docx")
    assert result == "paragraph 1 paragraph 2"

@patch("data_preprocessing.text_extraction.convert_email_to_txt")
@patch("data_preprocessing.text_extraction.extract_text_from_txt")
def test_extract_text_from_email(mock_extract_text_from_txt, mock_convert_email_to_txt):
    # Mock the conversion of email to .txt
    mock_convert_email_to_txt.return_value = "sample_email.txt"
    
    # Mock the text extraction from the .txt file
    mock_extract_text_from_txt.return_value = "Extracted email content"
    
    # Call the function with a sample .eml file
    result = extract_text("sample.eml")
    
    # Assertions
    mock_convert_email_to_txt.assert_called_once_with("sample.eml")
    mock_extract_text_from_txt.assert_called_once_with("sample_email.txt")
    assert result == "Extracted email content"

@patch("data_preprocessing.text_extraction.convert_email_to_txt")
@patch("data_preprocessing.text_extraction.extract_text_from_txt")
def test_extract_text_from_msg(mock_extract_text_from_txt, mock_convert_email_to_txt):
    # Mock the conversion of .msg to .txt
    mock_convert_email_to_txt.return_value = "sample_msg.txt"
    
    # Mock the text extraction from the .txt file
    mock_extract_text_from_txt.return_value = "Extracted message content"
    
    # Call the function with a sample .msg file
    result = extract_text("sample.msg")
    
    # Assertions
    mock_convert_email_to_txt.assert_called_once_with("sample.msg")
    mock_extract_text_from_txt.assert_called_once_with("sample_msg.txt")
    assert result == "Extracted message content"

@patch("data_preprocessing.text_extraction.convert_email_to_txt")
@patch("data_preprocessing.text_extraction.extract_text_from_txt")
def test_extract_text_from_email_file(mock_extract_text_from_txt, mock_convert_email_to_txt):
    # Mock the conversion of .email to .txt
    mock_convert_email_to_txt.return_value = "sample_email_file.txt"
    
    # Mock the text extraction from the .txt file
    mock_extract_text_from_txt.return_value = "Extracted email file content"
    
    # Call the function with a sample .email file
    result = extract_text("sample.email")
    
    # Assertions
    mock_convert_email_to_txt.assert_called_once_with("sample.email")
    mock_extract_text_from_txt.assert_called_once_with("sample_email_file.txt")
    assert result == "Extracted email file content"

@patch("data_preprocessing.data_construction.extract_text")
@patch("data_preprocessing.data_construction.HumanMessage")
@patch("data_preprocessing.data_construction.SystemMessage")
@patch("data_preprocessing.data_construction.json.loads")
@patch("data_preprocessing.data_construction.re.search")
def test_data_construction_func(mock_re_search, mock_json_loads, mock_system_message, mock_human_message, mock_extract_text):
    mock_extract_text.return_value = "Sample text"
    mock_re_search.return_value.group.return_value = '{"request_type": "Money Movement", "sub_request_type": "Inbound"}'
    mock_json_loads.return_value = {"request_type": "Money Movement", "sub_request_type": "Inbound"}
    mock_model = MagicMock()
    result = data_construction_func(mock_model, {"Money Movement": ["Inbound"]}, "sample.txt")
    assert result["request_type"] == "Money Movement"
    assert result["sub_request_type"] == "Inbound"

@patch("classifier.llm_classifier.SystemMessage")
@patch("classifier.llm_classifier.HumanMessage")
@patch("classifier.llm_classifier.json.loads")
@patch("classifier.llm_classifier.re.search")
def test_call_llm(mock_re_search, mock_json_loads, mock_human_message, mock_system_message):
    mock_re_search.return_value.group.return_value = '{"request_type": "Money Movement", "sub_request_type": "Inbound"}'
    mock_json_loads.return_value = {"request_type": "Money Movement", "sub_request_type": "Inbound"}
    mock_model = MagicMock()
    result = call_llm(mock_model, "test text", {"Money Movement": ["Inbound"]}, [])
    assert result["request_type"] == "Money Movement"
    assert result["sub_request_type"] == "Inbound"