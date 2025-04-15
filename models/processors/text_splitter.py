from langchain.text_splitter import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP

def get_text_chunks(text_with_metadata):
    recursive_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""],
        length_function=len,
        keep_separator=True,
        is_separator_regex=False
    )
    
    docs = []
    for item in text_with_metadata:
        text = item["text"]
        metadata = item["metadata"]
        
        try:
            splits = recursive_splitter.split_text(text)
            for split in splits:
                docs.append({
                    "page_content": split,
                    "metadata": metadata
                })
                
        except Exception as e:
            print(f"Lỗi khi xử lý văn bản: {str(e)}")
    
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
    
    print(f"\n{'='*50}")
    print(f"Tổng số chunk được tạo từ PDF: {len(final_docs)}")
    print(f"{'='*50}\n")
    
    return final_docs
