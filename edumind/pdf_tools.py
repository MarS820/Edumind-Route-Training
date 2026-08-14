import os
import re
from typing import Generator
import streamlit as st
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

SUGGESTED_PROMPTS = [
    "Summarize this file",
    "Quiz me on this file",
    "Explain the key formula",
]


def get_groq_llm(streaming: bool = False, temperature: float = 0.2):
    api_key = None
    if "GROQ_API_KEY" in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    else:
        api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("Groq API Key is missing! Please configure GROQ_API_KEY in Streamlit Secrets.")

    groq_model = st.secrets.get("GROQ_MODEL", os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"))

    return ChatGroq(
        groq_api_key=api_key,
        model_name=groq_model,
        streaming=streaming,
        temperature=temperature
    )


@st.cache_resource
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


import io  
from PyPDF2 import PdfReader

@st.cache_resource
def process_pdf_to_vectorstore(pdf_file):
    if PdfReader is None:
        raise ImportError("PyPDF2 is not installed.")
    
    # تحويل الـ bytes إلى BytesIO Stream إذا تم تمريرها كـ bytes
    if isinstance(pdf_file, bytes):
        pdf_file = io.BytesIO(pdf_file)
    elif hasattr(pdf_file, "getvalue"):
        pdf_file = io.BytesIO(pdf_file.getvalue())

    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)

    embeddings = get_embeddings()
    vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
    return vectorstore


def _extract_args(arg1, arg2):
    """تعرف تلقائي على ترتيب المتغيرات لمنع خطأ TypeError أو AttributeError"""
    if hasattr(arg1, "similarity_search"):
        return arg1, str(arg2)
    elif hasattr(arg2, "similarity_search"):
        return arg2, str(arg1)
    return None, str(arg1 or arg2)


def get_rag_response(
    vectorstore, 
    query: str, 
    history: list = None, 
    streaming: bool = True
) -> Generator[str, None, None] | str:
    
    if not hasattr(vectorstore, "similarity_search"):
        vectorstore, query = _extract_args(vectorstore, query)

    # 1. رفع عدد Chunks في الأسئلة العادية لـ 5 والتلخيص لـ 7 لجمع معلومات أكثر
    is_summary_request = any(kw in query.lower() for kw in ["summarize", "summary", "overview", "ملخص", "لخص"])
    k_chunks = 7 if is_summary_request else 5

    docs = vectorstore.similarity_search(query, k=k_chunks)
    context = "\n\n".join([doc.page_content for doc in docs])

    # 2. إجبار الموديل على إعطاء ردود مفصلة وشاملة
    messages = [
        ("system", (
            "You are an expert AI learning assistant for university students.\n"
            "Answer strictly based on the provided PDF context.\n\n"
            "FORMATTING & DETAILED EXPLANATION RULES:\n"
            "1. Respond in the EXACT same language as the user's question (Arabic or English).\n"
            "2. Provide COMPREHENSIVE, IN-DEPTH, and DETAILED explanations. Avoid short or overly brief answers.\n"
            "3. Structure answers using **bold key terms**, bullet points, and clean subheadings for high readability.\n"
            "4. Thoroughly explain mechanisms, components, and examples present in the provided context.\n"
            "5. DO NOT repeat standard introductory definitions if already explained in previous turns.\n"
            "6. For summaries, provide an extensive, well-structured breakdown grouped into logical sections."
        ))
    ]

    if history:
        for item in history[-6:]:
            if isinstance(item, dict):
                messages.append((item.get("role", "user"), item.get("content", "")))

    prompt = f"Context from PDF:\n{context}\n\nUser Question:\n{query}"
    messages.append(("user", prompt))

    llm = get_groq_llm(streaming=streaming, temperature=0.2)

    if streaming:
        def stream_generator():
            for chunk in llm.stream(messages):
                if chunk.content:
                    yield chunk.content
        return stream_generator()
    else:
        return llm.invoke(messages).content

def get_formula_response(question: str, vectorstore, history=None, **kwargs) -> str:
    if not hasattr(vectorstore, "similarity_search"):
        vectorstore, question = _extract_args(question, vectorstore)

    if not vectorstore:
        return "Error: Vectorstore not initialized."

    search_query = f"formula equation mathematical expression {question}"
    docs = vectorstore.similarity_search(search_query, k=5)
    context = "\n\n".join([doc.page_content for doc in docs])

    if not context or len(context) < 50:
        return "I couldn't find any formula-related content in the PDF. Please make sure the PDF contains mathematical content."

    prompt = f"""You are a precise AI assistant. The user is asking about a formula or equation from the PDF.

PDF CONTENT (USE THIS EXACTLY):
{context}

User Question: {question}

IMPORTANT INSTRUCTIONS:
1. Extract the formula or equation EXACTLY as it appears in the PDF CONTENT above.
2. If you don't see a formula in the PDF CONTENT above, state: "No formula was found in the PDF content."
3. PRESERVE ALL special characters, mathematical symbols (like ∑, ∫, √, π, θ, α, β, γ, Δ, etc.)
4. Use proper mathematical notation.
5. Explain the formula using ONLY the PDF CONTENT above.
6. Do NOT use your general knowledge or invent formulas.

Response format:
- First show the formula as it appears in the PDF
- Then explain what each part means based on the PDF
- Finally, explain the significance of the formula from the PDF context
"""
    messages = [
        ("system", "You are a strict assistant that ONLY uses the provided PDF content. Never use external knowledge."),
        ("user", prompt)
    ]

    llm = get_groq_llm(temperature=0.1)
    response = llm.invoke(messages)
    return response.content.strip()


def generate_quiz_questions(vectorstore, num_questions: int = 5, **kwargs) -> list[dict]:
    if not hasattr(vectorstore, "similarity_search"):
        return [{"question": "Error: Invalid vectorstore object.", "answer": "Re-upload PDF."}]

    search_query = "key concepts definitions main ideas important details core principles"
    docs = vectorstore.similarity_search(search_query, k=6)
    context = "\n\n---\n\n".join([doc.page_content for doc in docs])

    if not context or len(context) < 100:
        return [{
            "question": "I couldn't find enough content in your PDF to generate questions. Please make sure the PDF contains readable text.",
            "answer": "Upload a PDF with more content."
        }]

    if len(context) > 5000:
        context = context[:5000] + "..."

    prompt = f"""You are creating a quiz based ONLY on the PDF content below.

PDF CONTENT (USE THIS EXACTLY):
{context}

Generate {num_questions} different quiz questions based ONLY on the content above.

FORMAT YOUR RESPONSE EXACTLY AS:
Q1: [question 1]
A1: [answer 1]

Q2: [question 2]
A2: [answer 2]

...and so on for all {num_questions} questions.

IMPORTANT RULES:
- ONLY use information from the PDF CONTENT above
- DO NOT use your general knowledge
- Questions must be answerable from the PDF content
- Each question should have ONE correct answer
- Answers should be directly from the PDF text
"""
    messages = [
        ("system", "You are a strict assistant that ONLY uses the provided PDF content to create quiz questions."),
        ("user", prompt)
    ]

    llm = get_groq_llm(temperature=0.2)
    response_text = llm.invoke(messages).content

    questions = []
    q_pattern = r'Q(\d+):\s*(.*?)\s*A\1:\s*(.*?)(?=Q\d+:|$)'
    matches = re.findall(q_pattern, response_text, re.DOTALL)

    if matches:
        for match in matches:
            _, question_text, answer_text = match
            questions.append({
                "question": question_text.strip(),
                "answer": answer_text.strip()
            })
    else:
        lines = response_text.strip().split('\n')
        current_q = None
        current_a = None

        for line in lines:
            line = line.strip()
            if re.match(r'^Q\d+:', line):
                if current_q and current_a:
                    questions.append({"question": current_q, "answer": current_a})
                parts = line.split(':', 1)
                current_q = parts[1].strip() if len(parts) > 1 else ""
                current_a = None
            elif re.match(r'^A\d+:', line) and current_q:
                parts = line.split(':', 1)
                current_a = parts[1].strip() if len(parts) > 1 else ""
                questions.append({"question": current_q, "answer": current_a})
                current_q = None
                current_a = None

        if current_q and current_a:
            questions.append({"question": current_q, "answer": current_a})

    if not questions:
        questions = [{
            "question": "What is the main topic of this PDF?",
            "answer": context[:200] if context else "No content found."
        }]

    return questions[:num_questions]


def check_answer(user_answer: str, correct_answer: str) -> bool:
    user_clean = user_answer.lower().strip()
    correct_clean = correct_answer.lower().strip()

    if user_clean == correct_clean:
        return True

    stopwords = {'the', 'a', 'an', 'of', 'to', 'for', 'with', 'on', 'at', 'from', 'by', 'in', 'as', 'is', 'was', 'are', 'were'}

    correct_words = [word for word in correct_clean.split() if word not in stopwords]
    user_words = [word for word in user_clean.split() if word not in stopwords]

    if correct_words:
        matches = sum(1 for word in correct_words if word in user_words)
        match_percentage = matches / len(correct_words)

        if match_percentage >= 0.6:
            return True

    return False