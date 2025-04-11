import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from dotenv import load_dotenv
load_dotenv()
# Tải cấu hình mô hình embedding từ biến môi trường
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

def get_vector_database(text_chunks):
    """Tạo và trả về vector store từ các chunks văn bản"""
    # Chuẩn hóa các chunk
    normalized_chunks = []
    for chunk in text_chunks:
        text = chunk["page_content"]
        normalized_chunk = chunk.copy()
        normalized_chunk["page_content"] = text
        normalized_chunks.append(normalized_chunk)
    
    # Tạo embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    
    # Tạo danh sách các đối tượng Document từ chunks
    documents = []
    for chunk in normalized_chunks:
        doc = Document(
            page_content=chunk["page_content"],
            metadata=chunk["metadata"]
        )
        documents.append(doc)
    
    # Kiểm tra thư mục faiss_index
    if not os.path.exists("faiss_index"):
        os.makedirs("faiss_index")
    
    # Tạo FAISS vector store
    vector_database = FAISS.from_documents(
        documents=documents,
        embedding=embeddings,
    )
    
    # Lưu vector store vào ổ đĩa
    vector_database.save_local("faiss_index")
    
    return vector_database

def load_vector_database():
    """Tải vector store từ ổ đĩa"""
    try:
        # Kiểm tra xem faiss_index đã tồn tại chưa
        if not os.path.exists("faiss_index") or not os.path.exists("faiss_index/index.faiss"):
            return None, "Không tìm thấy thông tin bạn đưa ra. Vui lòng đặt câu hỏi khác."
        
        # Tạo embeddings
        embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        
        try:
            vector_database = FAISS.load_local(
                "faiss_index", 
                embeddings
            )
            return vector_database, None
        except Exception as e:
            error_msg = f"ERROR LOADING FAISS INDEX: {str(e)}"
            print(f"\n{'!'*50}")
            print(error_msg)
            print(f"{'!'*50}\n")
            return None, "Đã xảy ra lỗi khi tải dữ liệu vector. Vui lòng tải lại tài liệu PDF."
    
    except Exception as e:
        return None, f"Lỗi: {str(e)}" 