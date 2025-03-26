import re
import json
from langchain_core.messages import SystemMessage, HumanMessage
import logging

def format_few_shot_prompt(text, similar_cases):
    """Format past cases as few-shot learning examples."""
    examples = "\n\n".join([
        f"Example {i+1}:\nRequest: {case['text']}\nClassified as: {case['request_type']} - {case['sub_request_type']}"
        for i, case in enumerate(similar_cases)
    ])
    
    return f"{examples}\n\nNew Request:\n{text}\nClassify this request amongst the available request and sub request types told in beginning and provide value of request type, sub request type(empty string if not applicable) and reasoning in json format"

def call_llm(model, text, allowed_types, similar_cases):
    """Call LLM API with few-shot learning examples."""
    prompt = f"""
    Allowed request(keys), sub-request types(values) in the format of dictionary : {str(allowed_types)}
    """
    prompt += format_few_shot_prompt(text, similar_cases)
    
    try:
        response = model.invoke(
            input=[SystemMessage(content="You are an expert in classifying loan service requests."),
                   HumanMessage(content=prompt)]
        )
        result = re.search(r'\{\s*\"request_type\":.*?\}', response.content, re.DOTALL).group(0)
        response_dict = json.loads(result)
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