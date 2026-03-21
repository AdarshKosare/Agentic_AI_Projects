from config import settings

def get_llm():
    if settings.has_gemini:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=settings.primary_model,
            google_api_key=settings.google_api_key,
            temperature=settings.temperature
        )
    else:
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=settings.fallback_model,
            temperature=settings.temperature
        )