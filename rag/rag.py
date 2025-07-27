import os

from gemini_embedding import GeminiEmbeddingFunction
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Import the PyPDFLoader class from langchain_community's document_loaders module
# This loader is specifically designed to load and parse PDF files
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
import google.generativeai as genai
from chromadb import Documents, EmbeddingFunction, Embeddings
from langchain.vectorstores import Chroma
from typing import List

os.environ["GEMINI_API_KEY"]="AIzaSyBLPAwhM7qGZXdiFUJjPqU0o8wbxSD1OU8"
# Create a PyPDFLoader instance by passing the URL of the PDF file
# The loader will download the PDF from the specified URL and prepare it for loading

# Call the load() method to:
# 1. Download the PDF if needed
# 2. Extract text from each page
# 3. Create a list of Document objects, one for each page of the PDF
# Each Document will contain the text content of a page and metadata including page number


def load_pdf():
    """
    Reads the text content from a PDF file and returns it as a single string.

    Parameters:
    - file_path (str): The file path to the PDF file.

    Returns:
    - str: The concatenated text content of all pages in the PDF.
    """
    # Logic to read pdf
    loader = PyPDFLoader("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/96-FDF8f7coh0ooim7NyEQ/langchain-paper.pdf")


    # Loop over each page and store it in a variable
    document = loader.load()
    print(f"Loaded {len(document)} pages from the PDF.")

    return document

def split_text(document):
    # Create a CharacterTextSplitter with specific configuration:
    # - chunk_size=200: Each chunk will contain approximately 200 characters
    # - chunk_overlap=20: Consecutive chunks will overlap by 20 characters to maintain context
    # - separator="\n": Text will be split at newline characters when possible
    text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20, separator="\n")

    # Split the previously loaded document (PDF or other text) into chunks
    # The split_documents method:
    # 1. Takes a list of Document objects
    # 2. Splits each document's content based on the configured parameters
    # 3. Returns a new list of Document objects where each contains a chunk of text
    # 4. Preserves the original metadata for each chunk
    chunks = text_splitter.split_documents(document)

    # Print the total number of chunks created
    # This shows how many smaller Document objects were generated from the original document(s)
    # The number depends on the original document length and the chunk_size setting
    print(len(chunks))

    return chunks


def create_chroma_db(documents:List, path:str, name:str):
    """
    Creates a Chroma database using the provided documents, path, and collection name.

    Parameters:
    - documents: An iterable of documents to be added to the Chroma database.
    - path (str): The path where the Chroma database will be stored.
    - name (str): The name of the collection within the Chroma database.

    Returns:
    - Tuple[chromadb.Collection, str]: A tuple containing the created Chroma Collection and its name.
    """
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    docsearch = Chroma.from_documents(documents, embedding)
    
    return docsearch

# Example usage:
# db, name = create_chroma_db(
#     documents=chunkedtext,
#     path=r"C:\Repos\RAG\contents",  # replace with your path
#     name="rag_experiment"
# )

def load_chroma_collection(path, name):
    """
    Loads an existing Chroma collection from the specified path with the given name.

    Parameters:
    - path (str): The path where the Chroma database is stored.
    - name (str): The name of the collection within the Chroma database.

    Returns:
    - chromadb.Collection: The loaded Chroma Collection.
    """
    chroma_client = chromadb.PersistentClient(path=path)
    db = chroma_client.get_collection(name=name, embedding_function=GeminiEmbeddingFunction())

    return db

def get_relevant_passage(query, db, n_results):
    passage = db.similarity_search(query)['documents'][0]
    # Use the docsearch vector store as a retriever
    # This converts the vector store into a retriever interface that can fetch relevant documents
    retriever = db.as_retriever()

    # Invoke the retriever with the query "Langchain"
    # This will:
    # 1. Convert the query text "Langchain" into an embedding vector
    # 2. Perform a similarity search in the vector store using this embedding
    # 3. Return the most semantically similar documents to the query
    docs = retriever.invoke("Langchain")

    return passage


def make_rag_prompt(query, relevant_passage):
  escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
  prompt = ("""You are a helpful and informative bot that answers questions using text from the reference passage included below. \
  Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
  However, you are talking to a non-technical audience, so be sure to break down complicated concepts and \
  strike a friendly and converstional tone. \
  If the passage is irrelevant to the answer, you may ignore it.
  QUESTION: '{query}'
  PASSAGE: '{relevant_passage}'

  ANSWER:
  """).format(query=query, relevant_passage=escaped)

  return prompt

def generate_answer(prompt):
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("Gemini API Key not provided. Please provide GEMINI_API_KEY as an environment variable")
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-2.5-pro')
    answer = model.generate_content(prompt)
    return answer.text



def main():
    load_dotenv()
    print("Starting RAG process...")
    # Load the PDF document
    document = load_pdf()

    # Split the document into chunks
    chunked_text = split_text(document)

    # Create a Chroma database with the chunked text
    db = create_chroma_db(chunked_text, path="/Users/nagendragupta/Documents/Workspace/Python/agent-ai/rag/chroma_db", name="rag_experiment")

    # Load the Chroma collection
    # db = load_chroma_collection(path="/Users/nagendragupta/Documents/Workspace/Python/agent-ai/rag/chroma_db", name="rag_experiment")

    # Example query
    query = "What is the main topic of the document?"
    
    # Get relevant passage from the database
    relevant_passage = get_relevant_passage(query, db, n_results=1)

    # Create a prompt for the LLM
    prompt = make_rag_prompt(query, relevant_passage)

    # Generate an answer using the LLM
    answer = generate_answer(prompt)
    
    print("Answer:", answer)

if __name__ == "__main__":
        main()