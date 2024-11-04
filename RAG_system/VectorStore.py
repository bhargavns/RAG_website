
import os
import time
import logging
import pickle
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain.text_splitter import RecursiveCharacterTextSplitter


class VectorStore:
    def __init__(self, chunk_size=300, chunk_overlap=40, max_retries=3, embeddings_file='embeddings.pkl'):
        self.document_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.max_retries = max_retries
        self.embeddings_file = embeddings_file

    def create_embeddings(self):
        try:
            return OpenAIEmbeddings()
        except Exception as e:
            logging.warning(f"Failed to create OpenAIEmbeddings: {e}. Falling back to HuggingFaceEmbeddings.")
            return HuggingFaceEmbeddings()

    def create_vectorstore(self, documents):
        splits = self.document_splitter.split_documents(documents)
        
        for attempt in range(self.max_retries):
            try:
                embeddings = self.create_embeddings()
                
                # Create Chroma vectorstore
                vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
                
                # Store embeddings in a file
                self.store_embeddings(embeddings)
                
                return vectorstore
            except Exception as e:
                if attempt < self.max_retries - 1:
                    logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logging.error(f"Failed to create vectorstore after {self.max_retries} attempts: {e}")
                    raise

    def store_embeddings(self, embeddings):
        try:
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(embeddings, f)
            logging.info(f"Embeddings stored in {self.embeddings_file}")
        except Exception as e:
            logging.error(f"Failed to store embeddings: {e}")

    def load_embeddings(self):
        if os.path.exists(self.embeddings_file):
            try:
                with open(self.embeddings_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logging.error(f"Failed to load embeddings: {e}")
        return None

    def get_vectorstore(self, documents):
        # Try to load existing embeddings
        embeddings = self.load_embeddings()
        
        # if embeddings:
        #     logging.info("Using existing embeddings")
        #     splits = self.document_splitter.split_documents(documents)
        #     return Chroma.from_documents(documents=splits, embedding=embeddings)
        # else:
        logging.info("Creating new vectorstore")
        return self.create_vectorstore(documents)