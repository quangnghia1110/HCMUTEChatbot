from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os

load_dotenv()

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE")) 
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP"))  

def get_text_chunks(text_with_metadata):
    """Chia văn bản thành các đoạn nhỏ hơn"""
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""],  # Giữ các dấu phân tách
        length_function=len,
        keep_separator=True, 
        is_separator_regex=False
    )
    
    docs = []
    for item in text_with_metadata:
        text = item["text"]
        metadata = item["metadata"]
        
        try:
            # Chia văn bản trực tiếp bằng RecursiveCharacterTextSplitter
            splits = recursive_splitter.split_text(text)
            for split in splits:
                docs.append({
                    "page_content": split, 
                    "metadata": metadata
                })
                
        except Exception as e:
            print(f"Lỗi khi xử lý văn bản: {str(e)}")
    
    # Kiểm tra và chia lại nếu chunk vẫn dài hơn CHUNK_SIZE
    final_docs = []
    for doc in docs:
        if len(doc["page_content"]) > CHUNK_SIZE:
            smaller_splits = recursive_splitter.split_text(doc["page_content"])
            for split in smaller_splits:
                final_docs.append({
                    "page_content": split, 
                    "metadata": doc["metadata"]
                })
        else:
            final_docs.append(doc)
    
    return final_docs

