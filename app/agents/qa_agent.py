import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.services.vector_store import VectorStoreService

class QAAgent:
    def __init__(self):
        self.name = "QAAgent"
        self.llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model_name=os.getenv("GROQ_MODEL_NAME")
        )
        self.vector_service = VectorStoreService()

    def answer(self, question: str, doc_id: str):
        # 1. Load the specific index for this document
        vector_db = self.vector_service.load_index(doc_id)
        if not vector_db:
            return "Knowledge base not found. Please upload the document first."

        # 2. Create retriever
        retriever = vector_db.as_retriever(search_kwargs={"k": 3})
        
        # 3. Retrieve relevant documents
        docs = retriever.invoke(question)
        
        # 4. Format context from retrieved documents
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # 5. Create prompt template with system instructions
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intelligent document analysis assistant. Your role is to provide accurate, concise, and helpful answers based solely on the provided context.

Guidelines:
- Answer questions using ONLY the information from the provided context
- If the context doesn't contain enough information to answer the question, clearly state that
- Be precise and cite specific details from the context when relevant
- If asked about something not in the context, say "I don't have that information in the provided document"
- Maintain a professional and helpful tone
- Structure your answers clearly with bullet points or paragraphs as appropriate"""),
            ("user", """Context from the document:
{context}

Question: {question}

Answer:""")
        ])
        
        # 6. Create chain and invoke
        chain = prompt | self.llm | StrOutputParser()
        
        response = chain.invoke({
            "context": context,
            "question": question
        })
        
        return response
