import os
import pickle
import json
import csv
import logging
from dotenv import load_dotenv
from pypdf import PdfReader
import docx2txt
try:
    import openpyxl
except ImportError:
    openpyxl = None
try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
from rank_bm25 import BM25Okapi
from openai import OpenAI
from src.core.database import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("RAG-System")

load_dotenv()

class RAGEngine:
    def __init__(self):
        self.data_dir = os.getenv("DATA_DIR", "./data")
        self.index_file = os.path.join(os.getenv("VECTOR_DB_DIR", "./chroma_db"), "bm25_index.pkl")
        self.model_name = os.getenv("DEFAULT_MODEL", "google/gemma-2-9b-it:free")
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        
        # Initialize OpenAI Client (OpenRouter)
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            default_headers={
                "HTTP-Referer": "https://localhost:3000",
                "X-Title": "Local RAG Chatbot"
            }
        )
        
        self.chunks = []
        self.bm25 = None
        self.load_index()

    def load_index(self):
        """Load the BM25 index and chunks from disk."""
        if os.path.exists(self.index_file):
            print("Loading existing index...")
            try:
                with open(self.index_file, "rb") as f:
                    data = pickle.load(f)
                    self.chunks = data["chunks"]
                    self.bm25 = data["bm25"]
            except Exception as e:
                print(f"Error loading index: {e}")

    def save_index(self):
        """Save the BM25 index and chunks to disk."""
        os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
        with open(self.index_file, "wb") as f:
            pickle.dump({"chunks": self.chunks, "bm25": self.bm25}, f)

    def extract_text(self):
        """Extract text from all supported files in the data directory."""
        all_docs = []
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        for root, dirs, files in os.walk(self.data_dir):
            for file in files:
                file_path = os.path.join(root, file)
                text = ""
                try:
                    if file.endswith(".pdf"):
                        reader = PdfReader(file_path)
                        for page in reader.pages:
                            text += page.extract_text() + "\n"
                    elif file.endswith(".docx"):
                        text = docx2txt.process(file_path)
                    elif file.endswith((".png", ".jpg", ".jpeg")):
                        if pytesseract:
                            try:
                                text = pytesseract.image_to_string(Image.open(file_path), lang='vie+eng')
                            except Exception:
                                text = f"[Loi OCR: Khong the doc file anh {file}]"
                        else:
                            text = "[Loi: Thu vien OCR chua duoc cai dat]"
                    elif file.endswith(".xlsx"):
                        if openpyxl:
                            wb = openpyxl.load_workbook(file_path, data_only=True)
                            text = ""
                            for sheet in wb.sheetnames:
                                ws = wb[sheet]
                                for row in ws.iter_rows(values_only=True):
                                    text += "\t".join([str(c) if c is not None else "" for c in row]) + "\n"
                        else:
                            text = "[Loi: Thu vien openpyxl chua duoc cai dat]"
                    elif file.endswith(".csv"):
                        with open(file_path, "r", encoding="utf-8") as f:
                            reader = csv.reader(f)
                            text = "\n".join(["\t".join(row) for row in reader])
                    elif file.endswith((".txt", ".md")):
                        with open(file_path, "r", encoding="utf-8") as f:
                            text = f.read()
                    
                    if text.strip():
                        all_docs.append({"content": text, "source": file})
                except Exception as e:
                    print(f"Error reading {file}: {e}")
        return all_docs

    def ingest_data(self):
        """Process documents and create the BM25 index."""
        print(f"Ingesting data from {self.data_dir}...")
        docs = self.extract_text()
        
        if not docs:
            return "No documents found in data directory."

        # Simple chunking logic (by lines or paragraphs)
        self.chunks = []
        for doc in docs:
            content = doc["content"]
            # Split by approximately 1000 characters with overlap
            lines = content.split("\n")
            current_chunk = ""
            for line in lines:
                if len(current_chunk) + len(line) < 1000:
                    current_chunk += line + "\n"
                else:
                    self.chunks.append(current_chunk.strip())
                    current_chunk = line + "\n"
            if current_chunk:
                self.chunks.append(current_chunk.strip())

        # Create BM25 index
        tokenized_corpus = [chunk.lower().split() for chunk in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)
        
        self.save_index()
        return f"Successfully ingested {len(docs)} documents and created {len(self.chunks)} chunks."

    def query(self, user_input, session_id="default"):
        """Retrieve relevant chunks and get answer from OpenRouter with Chat Memory."""
        if not self.bm25 or not self.chunks:
            return "He thong du lieu chua duoc khoi tao. Vui long tai tai lieu len trang Admin va nhan Re-index."
            
        # 1. Get Chat History
        history = db.get_history(session_id, limit=6)
        history_str = ""
        for role, content in history:
            history_str += f"{role}: {content}\n"

        # 2. Search for relevant chunks
        tokenized_query = user_input.lower().split()
        top_chunks = self.bm25.get_top_n(tokenized_query, self.chunks, n=3)
        
        context = "\n---\n".join(top_chunks)
        
        # 3. Call OpenRouter
        prompt = f"""Su dung thong tin va lich su tro chuyen sau day de tra loi cau hoi. 
Neu khong co trong thong tin, hay tra loi bang kien thuc cua ban nhung co chu thich la 'Ngoai tai lieu'.
Tra loi bang tieng Viet.

Context:
{context}

Lich su tro chuyen:
{history_str}

Question: {user_input}

Answer:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.choices[0].message.content
            
            # 4. Save to Database
            db.add_message(session_id, "User", user_input)
            db.add_message(session_id, "Assistant", answer)
            
            return answer
        except Exception as e:
            return f"Loi khi goi AI: {str(e)}"

# Singleton instance
rag_engine = RAGEngine()
