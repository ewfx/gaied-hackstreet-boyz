from data_preprocessing.text_extraction import extract_text
from langchain_core.messages import SystemMessage, HumanMessage
import json
import re
import logging

def data_construction_func(model, mapping, file_path):
    """
    Uses an LLM to extract request_type and sub_request_type from text.
    """
    text_from_file = extract_text(file_path)
    
    prompt = f"""
    Extract the request type and sub-request type from the following text.
    Allowed request(keys), sub-request types(values) in the format of dictionary : {str(mapping)}

    Text: {text_from_file}

    Respond in JSON with request_type and sub_request_type keys and it's corresponding values.
    """

    try:
        response = model.invoke(
            input=[
                SystemMessage(content="You are an expert in document classification."),
                HumanMessage(content=prompt)
            ]
        )

        result=response.content
        result=re.search(r'\{\s*\"request_type\":.*?\}', result, re.DOTALL).group(0)
        response_dict = json.loads(result) 
        response_dict['text']=text_from_file
        return response_dict
    except Exception as e:
        logging.error(f"Error in data_construction_func: {str(e)}")

        # Attempt to parse the error as JSON if possible
        try:
            error_details = json.loads(str(e))
            if "retry_delay" in error_details:
                retry_delay = error_details["retry_delay"]["seconds"]
                logging.warning(f"Rate limit exceeded. Retrying in {retry_delay} seconds.")
                return {"error": "Rate limit exceeded", "retry_after": retry_delay}
        except (json.JSONDecodeError, KeyError):
            pass  # If parsing fails, fall back to generic error handling

        # Return a generic error response
        return {"error": "An unexpected error occurred", "details": str(e)}