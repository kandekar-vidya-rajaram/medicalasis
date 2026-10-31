from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def generate_answer(question: str, context: str) -> str:
    if not GROQ_API_KEY:
        raise ValueError("Missing required environment variable: GROQ_API_KEY")

    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model="openai/gpt-oss-120b"
    )

    prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are MediBot, an assistant that explains medical documents.

Answer the question using the context below.
Give a short, clear answer in simple English.
Do not invent information or provide a diagnosis.

If the context does not contain the answer, say:
"I couldn't find relevant information in the uploaded documents."

Context:
{context}

Question:
{question}

Answer:
"""
)
    response = llm.invoke(prompt.format(context=context, question=question))
    if not isinstance(response.content, str):
        raise TypeError("The LLM returned a non-text response.")
    return response.content.strip()