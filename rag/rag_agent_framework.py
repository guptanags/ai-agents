# rag_agent_framework.py
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
load_dotenv()
import dotenv
import PyPDF2
from docx import Document
import requests
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import uvicorn
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGAgentFramework:
    def __init__(self, env_file: str = ".env"):
        """Initialize the RAG framework by loading configuration."""
        load_dotenv(env_file)
        dotenv.load_dotenv()
        self.config = self._load_config()
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_db = self._init_vector_db()
        self.llm = self._init_llm()
        self.documents_processed = False

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from .env file."""
        config = {
            "doc_source_type": os.getenv("DOC_SOURCE_TYPE"),
            "doc_source_path": os.getenv("DOC_SOURCE_PATH"),
            "vector_db_path": os.getenv("VECTOR_DB_PATH"),
            "llm_api_key": os.getenv("LLM_API_KEY"),
            "llm_model": os.getenv("LLM_MODEL", "gemini-1.5-pro"),
            "confluence_url": os.getenv("CONFLUENCE_URL", ""),
            "confluence_token": os.getenv("CONFLUENCE_TOKEN", ""),
            "jira_url": os.getenv("JIRA_URL", ""),
            "jira_token": os.getenv("JIRA_TOKEN", "")
        }
        # Debug: print config
        print("Loaded config:", config)
        # Optionally, raise if required keys are missing
        if not config["doc_source_type"]:
            raise ValueError("DOC_SOURCE_TYPE is not set in .env")
        return config

    def _init_vector_db(self):
        """Initialize Chroma vector database."""
        return chromadb.PersistentClient(
            path=self.config["vector_db_path"],
            settings=Settings(anonymized_telemetry=False)
        )

    def _init_llm(self):
        """Initialize Gemini LLM."""
        genai.configure(api_key=self.config["llm_api_key"])
        return genai.GenerativeModel(self.config["llm_model"])

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from a PDF file."""
        try:
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
            return ""

    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from a Word document."""
        try:
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs if para.text])
        except Exception as e:
            logger.error(f"Error reading DOCX {file_path}: {e}")
            return ""

    def _fetch_confluence_content(self) -> str:
        """Fetch content from Confluence."""
        try:
            headers = {"Authorization": f"Bearer {self.config['confluence_token']}"}
            response = requests.get(self.config["confluence_url"], headers=headers)
            response.raise_for_status()
            return response.json().get("content", "")
        except Exception as e:
            logger.error(f"Error fetching Confluence content: {e}")
            return ""

    def _fetch_jira_issues(self) -> str:
        """Fetch issues from Jira."""
        try:
            headers = {"Authorization": f"Bearer {self.config['jira_token']}"}
            response = requests.get(self.config["jira_url"], headers=headers)
            response.raise_for_status()
            issues = response.json().get("issues", [])
            return "\n".join([issue.get("fields", {}).get("description", "") for issue in issues])
        except Exception as e:
            logger.error(f"Error fetching Jira issues: {e}")
            return ""

    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into chunks for embedding."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        for word in words:
            current_chunk.append(word)
            current_length += len(word) + 1
            if current_length >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    def process_documents(self):
        """Process documents and store in vector database."""
        if self.documents_processed:
            logger.info("Documents already processed, skipping.")
            return

        doc_type = self.config["doc_source_type"]
        texts = []

        if doc_type == "pdf":
            for file in os.listdir(self.config["doc_source_path"]):
                if file.endswith(".pdf"):
                    text = self._extract_text_from_pdf(os.path.join(self.config["doc_source_path"], file))
                    texts.extend(self._chunk_text(text))
        elif doc_type == "docx":
            for file in os.listdir(self.config["doc_source_path"]):
                if file.endswith(".docx"):
                    text = self._extract_text_from_docx(os.path.join(self.config["doc_source_path"], file))
                    texts.extend(self._chunk_text(text))
        elif doc_type == "confluence":
            text = self._fetch_confluence_content()
            texts.extend(self._chunk_text(text))
        elif doc_type == "jira":
            text = self._fetch_jira_issues()
            texts.extend(self._chunk_text(text))
        else:
            raise ValueError(f"Unsupported document source type: {doc_type}")

        # Generate embeddings
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)

        # Store in Chroma
        collection = self.vector_db.get_or_create_collection(name="rag_collection")
        collection.add(
            documents=texts,
            embeddings=embeddings,
            ids=[f"doc_{i}" for i in range(len(texts))]
        )
        self.documents_processed = True
        logger.info("Documents processed and stored in vector database.")

    def retrieve(self, query: str, top_k: int = 5) -> List[str]:
        """Retrieve relevant document chunks for a query."""
        collection = self.vector_db.get_collection("rag_collection")
        query_embedding = self.embedding_model.encode([query])[0]
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
        return results["documents"][0]

    def augment_prompt(self, query: str, context: List[str]) -> str:
        """Augment the user prompt with retrieved context."""
        context_str = "\n".join(context)
        return f"Context:\n{context_str}\n\nQuery:\n{query}\n\nAnswer based on the provided context."

    def query_llm(self, prompt: str) -> str:
        """Query the LLM with the augmented prompt."""
        try:
            response = self.llm.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error querying LLM: {e}")
            return "Error generating response."

# FastAPI Setup
app = FastAPI(title="RAG Agent Framework API", description="API for RAG-based question answering")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

rag_framework = None

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG framework on startup."""
    global rag_framework
    rag_framework = RAGAgentFramework()
    rag_framework.process_documents()

@app.post("/query", summary="Query the RAG system")
async def query(request: QueryRequest):
    """Handle user query via REST API."""
    try:
        context = rag_framework.retrieve(request.query, request.top_k)
        augmented_prompt = rag_framework.augment_prompt(request.query, context)
        response = rag_framework.query_llm(augmented_prompt)
        return {"query": request.query, "response": response, "context": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)