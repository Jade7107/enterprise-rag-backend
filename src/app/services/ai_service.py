import os
import tempfile
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter

class AIService:
    def __init__(self):
        self.persist_directory = "./chroma_db"
        # Initialize components once to save resources
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        
        # Define the prompt once
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise.\n\n{context}"
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

    async def ingest_document(self, file: UploadFile):
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(await file.read())
                tmp_path = tmp_file.name

            loader = PyPDFLoader(tmp_path)
            documents = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
            texts = text_splitter.split_documents(documents)

            # Modern Chroma usage with pre-initialized embeddings
            Chroma.from_documents(
                documents=texts, 
                embedding=self.embeddings, 
                persist_directory=self.persist_directory
            )
            return {"message": "Document ingested successfully", "chunks": len(texts)}
        
        finally:
            # Clean up the file after ingestion
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)

    async def ask_question(self, query: str):
        # Use existing embeddings to connect to the DB
        vectordb = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
        retriever = vectordb.as_retriever()
        
        # Construct the chain
        question_answer_chain = create_stuff_documents_chain(self.llm, self.prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        
        response = await rag_chain.ainvoke({"input": query}) # Used ainvoke for async
        return response["answer"]

ai_service = AIService()