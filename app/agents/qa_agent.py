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
        
        # 5. Create prompt template
        prompt = ChatPromptTemplate.from_template(
            """Answer the question based only on the following context:

Context:
{context}

Question: {question}

Answer:"""
        )
        
        # 6. Create chain and invoke
        chain = prompt | self.llm | StrOutputParser()
        
        response = chain.invoke({
            "context": context,
            "question": question
        })
        
        return response
