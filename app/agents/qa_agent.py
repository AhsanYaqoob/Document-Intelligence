import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.services.vector_store import VectorStoreService

class QAAgent:
    def __init__(self):
        self.name = "QAAgent"
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name=os.getenv("GROQ_MODEL_NAME"),
            temperature=0.3,
            max_tokens=1024,
        )
        self.vector_service = VectorStoreService()

    def answer(self, question: str, doc_id: str):
        # 1. Load the specific index for this document
        vector_db = self.vector_service.load_index(doc_id)
        if not vector_db:
            return "Knowledge base not found. Please upload the document first."

        # 2. BM25Retriever is already the retriever — no .as_retriever() needed
        retriever = vector_db

        # 3. Retrieve relevant chunks
        docs = retriever.invoke(question)

        # 4. Build context with chunk separators so the model sees boundaries
        context_parts = []
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"[Excerpt {i}]\n{doc.page_content.strip()}")
        context = "\n\n".join(context_parts)

        # 5. Enhanced prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert AI document analyst. Your job is to give clear, accurate, and well-structured answers based strictly on the document excerpts provided.

RESPONSE FORMAT:
- Start with a direct, one-sentence answer to the question when possible.
- Then elaborate with supporting details from the document.
- Use **bold** for key terms, names, numbers, or critical facts.
- Use bullet points (- item) for lists, features, or multiple facts.
- Use numbered lists (1. step) for processes or sequential information.
- Use short paragraphs — never write a wall of text.
- If the answer spans multiple topics, use a short heading like "**Topic:**" to separate them.

CONTENT RULES:
- Answer ONLY using the provided document excerpts. Do not use outside knowledge.
- Quote short phrases from the document (in "quotes") when they directly support your answer.
- If the excerpts partially answer the question, share what is available and clearly state: "The document does not provide further detail on [X]."
- If the question cannot be answered from the document at all, say exactly: "This information is not available in the uploaded document."
- Never fabricate, assume, or guess information.

TONE: Confident, professional, and conversational. Be concise but complete."""),
            ("user", """Document excerpts:
{context}

Question: {question}

Answer:""")
        ])

        # 6. Build and invoke chain
        chain = prompt | self.llm | StrOutputParser()
        response = chain.invoke({"context": context, "question": question})
        return response
