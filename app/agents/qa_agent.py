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

        # 5. Enhanced prompt — document-aware + conversational
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a friendly and intelligent AI assistant embedded in a document analysis tool. You have two modes:

--- DOCUMENT MODE ---
When the user asks something that can be answered from the document excerpts below:
- Start with a direct, one-sentence answer.
- Elaborate with supporting details from the document.
- Use **bold** for key terms, names, numbers, or critical facts.
- Use bullet points (- item) for lists or multiple facts.
- Use numbered lists (1. step) for processes or sequences.
- Quote short phrases from the document in "quotes" when helpful.
- If the excerpts only partially answer the question, share what's available and note: "The document doesn't go into further detail on [X]."
- If the question truly cannot be answered from the document, say: "This information is not available in the uploaded document."

--- CONVERSATIONAL MODE ---
When the user says something casual — greetings, introduces themselves, jokes, thanks, or asks general questions NOT related to the document:
- Respond naturally and warmly, like a helpful assistant.
- If they share their name, acknowledge it and use it.
- Keep it brief and friendly, then gently guide them back to asking about the document if relevant.
- NEVER say "This information is not available in the uploaded document" for casual messages.

TONE: Warm, confident, and professional. Be human. Never robotic."""),
            ("user", """Document excerpts:
{context}

User message: {question}

Response:""")
        ])

        # 6. Build and invoke chain
        chain = prompt | self.llm | StrOutputParser()
        response = chain.invoke({"context": context, "question": question})
        return response
