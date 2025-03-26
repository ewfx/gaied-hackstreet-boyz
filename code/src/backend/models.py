from config import OPENAI_API_KEY, DEEPSEEK_API_KEY, HUGGINGFACE_API_KEY, GEMINI_API_KEY
from langchain_openai import ChatOpenAI  # For OpenAI
from langchain_community.chat_models import ChatOpenAI as DeepSeekChatOpenAI  # For DeepSeek
from langchain_community.llms import HuggingFaceHub
from langchain_google_genai import ChatGoogleGenerativeAI

# OpenAI LLM
openai_llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model="gpt-3.5-turbo",
    temperature=0.3
)

# DeepSeek LLM
deepseek_llm = DeepSeekChatOpenAI(
    openai_api_key=DEEPSEEK_API_KEY,
    model="deepseek-chat",
    openai_api_base="https://api.deepseek.com/v1",  # Ensure correct API version
    temperature=0.3
)

# DeepSeek Reasoner
deepseek_reasoner = DeepSeekChatOpenAI(
    openai_api_key=DEEPSEEK_API_KEY,
    model="deepseek-reasoner",
    openai_api_base="https://api.deepseek.com/v1"
)

# Mistral hugging face
huggingface_zephyr_llm = HuggingFaceHub(
    huggingfacehub_api_token=HUGGINGFACE_API_KEY,
    repo_id="HuggingFaceH4/zephyr-7b-beta",  # Replace with another HF model if needed
    model_kwargs={"temperature": 0.3, "max_new_tokens": 256}
)

# Gemini Pro
gemini_llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    google_api_key=GEMINI_API_KEY,
    temperature=0.3
)