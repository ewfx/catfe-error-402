from langchain_groq import ChatGroq
import os
def init_llm():
    """Initialize Llama3 on Groq."""
    api_key = os.getenv("GROQ_API_KEY")

    llm = ChatGroq(
        api_key=api_key,
        model_name="llama3-8b-8192",  # You can use a smaller model if needed
        temperature=0.7,  # Lower temp for deterministic responses
        max_tokens=4096,
    )

    print("✅ LLaMA-3 model initialized successfully!")
    return llm

def init_llm2():
    """Initialize Llama3 on Groq."""
    api_key = os.getenv("GROQ_SECOND_API_KEY")

    llm = ChatGroq(
        api_key=api_key,
        model_name="llama3-8b-8192",  # You can use a smaller model if needed
        temperature=0.7,  # Lower temp for deterministic responses
        max_tokens=2048,
    )

    print("✅ LLaMA-3 2nd model initialized successfully!")
    return llm

def init_llm3():
    """Initialize Llama3 on Groq."""
    api_key = os.getenv("GROQ_SECOND_API_KEY")

    llm = ChatGroq(
        api_key="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",
        model_name="llama3-8b-8192",  # You can use a smaller model if needed
        temperature=0.7,  # Lower temp for deterministic responses
        max_tokens=2048,
    )

    print("✅ LLaMA-3 2nd model initialized successfully!")
    return llm