import hashlib
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from rank_bm25 import BM25Okapi
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL")
TEMPERATURE = float(os.getenv("TEMPERATURE"))
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS"))
TOP_K = float(os.getenv("TOP_K"))
TOP_P = float(os.getenv("TOP_P"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES"))
BASE_DELAY = int(os.getenv("BASE_DELAY"))
MAX_DOCS = int(os.getenv("MAX_DOCS"))
SEMANTIC_WEIGHT = float(os.getenv("SEMANTIC_WEIGHT"))
KEYWORD_WEIGHT = float(os.getenv("KEYWORD_WEIGHT"))
VECTOR_SEARCH_K = int(os.getenv("VECTOR_SEARCH_K"))
VECTOR_CONTENT_PREVIEW = int(os.getenv("VECTOR_CONTENT_PREVIEW"))
VECTOR_SEARCH_WEIGHT = float(os.getenv("VECTOR_SEARCH_WEIGHT"))

def get_conversational_chain():
    """Tạo chain hỏi đáp cho LLM"""
    
    prompt_template = """
    Bạn là trợ lý AI chuyên gia về phân tích tài liệu. Nhiệm vụ của bạn là trả lời câu hỏi dựa HOÀN TOÀN vào thông tin từ các tài liệu PDF được cung cấp.

    Quy tắc QUAN TRỌNG (phải tuân thủ tuyệt đối):
    1. CHỈ sử dụng thông tin có trong đoạn văn được cung cấp bên dưới
    2. TUYỆT ĐỐI KHÔNG được bịa đặt, thêm thông tin từ kiến thức bên ngoài hoặc tìm kiếm trên internet
    3. Nếu không tìm thấy thông tin trong đoạn văn bản, hãy trả lời rõ ràng: "Không tìm thấy thông tin bạn đưa ra. Vui lòng đặt câu hỏi khác."
    4. Nếu thông tin không đủ để trả lời toàn bộ câu hỏi, hãy trả lời phần có thể và nói rõ phần nào bạn không thể trả lời
    5. Trả lời phải ngắn gọn, đúng trọng tâm, tập trung vào những thông tin quan trọng nhất
    6. KHÔNG THÊM CÂU NÀO VỀ "ĐỘ TIN CẬY" TRONG CÂU TRẢ LỜI CỦA BẠN.

    HƯỚNG DẪN ĐỊNH DẠNG MARKDOWN (sử dụng khi thích hợp):

    1. TIÊU ĐỀ: Sử dụng # cho tiêu đề chính, ## cho tiêu đề phụ, ### cho tiêu đề cấp 3
       # Tiêu đề chính
       ## Tiêu đề phụ
       ### Tiêu đề cấp 3

    2. BẢNG SO SÁNH: Khi so sánh thông tin từ nhiều nguồn hoặc nhiều khía cạnh, sử dụng bảng:
       | Tiêu chí | Nguồn 1 | Nguồn 2 |
       |----------|---------|---------|
       | Tiêu chí 1 | Giá trị 1A | Giá trị 1B |
       | Tiêu chí 2 | Giá trị 2A | Giá trị 2B |

    3. DANH SÁCH: Sử dụng danh sách có số thứ tự (1. 2. 3.) hoặc không có số thứ tự (- * +) khi liệt kê các điểm
       1. Điểm thứ nhất
       2. Điểm thứ hai
          * Điểm con
          * Điểm con khác

    4. TRÍCH DẪN: Sử dụng > để chỉ ra các trích dẫn trực tiếp từ tài liệu
       > Đây là trích dẫn trực tiếp từ tài liệu nguồn

    5. CODE BLOCK: Sử dụng ```language cho mã nguồn hoặc dữ liệu có định dạng đặc biệt
       ```python
       def hello():
           print("Hello world")
       ```

    6. ĐỊNH DẠNG TEXT: Sử dụng **in đậm** cho từ khóa quan trọng, *in nghiêng* cho thuật ngữ kỹ thuật, `đoạn mã` cho biến/tham số

    7. BIỂU ĐỒ: Mô tả quá trình hoặc quy trình bằng biểu đồ ASCII khi phù hợp
       Start → Bước 1 → Bước 2 → Kết thúc

    Thông tin từ các tài liệu PDF:
    {context}

    Câu hỏi: {question}

    Trả lời (sử dụng định dạng Markdown phù hợp để trình bày rõ ràng nhất, KHÔNG được thêm thông tin từ bên ngoài và KHÔNG ĐƯỢC NHẮC ĐẾN ĐỘ TIN CẬY):
    """

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=TEMPERATURE,
        max_output_tokens=MAX_OUTPUT_TOKENS,
        top_k=TOP_K,
        top_p=TOP_P
    )
    
    chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)
    return chain

def get_gemini_response(vector_database, user_question, filter_pdf=None):
    """Truy vấn tài liệu dựa trên câu hỏi của người dùng"""
    
    chain = get_conversational_chain()
    
    try:
        if filter_pdf:
            all_docs = []
            for doc_id, doc in vector_database.docstore._dict.items():
                if doc.metadata.get("source") == filter_pdf:
                    all_docs.append(doc)
            
            
            if not all_docs:
                print(f"Không tìm thấy đoạn văn nào từ {filter_pdf}")
                return {
                    "output_text": "Không tìm thấy thông tin bạn đưa ra. Vui lòng đặt câu hỏi khác.",
                    "source_documents": []
                }
            
            all_texts = [doc.page_content for doc in all_docs]
            tokenized_corpus = [text.lower().split() for text in all_texts]
            tokenized_query = user_question.lower().split()
            bm25 = BM25Okapi(tokenized_corpus)
            bm25_scores = bm25.get_scores(tokenized_query)
            doc_scores = list(zip(all_docs, bm25_scores))
            doc_scores.sort(key=lambda x: x[1], reverse=True)
            
            relevant_docs = [doc for doc, score in doc_scores if score > 0]
            
            if not relevant_docs:
                relevant_docs = all_docs
        else:
            vector_docs = vector_database.similarity_search_with_relevance_scores(
                user_question, 
                k=VECTOR_SEARCH_K
            )
            
            all_texts = []
            doc_mapping = {}
            
            for i, (doc, _) in enumerate(vector_docs):
                all_texts.append(doc.page_content)
                doc_mapping[i] = doc
                
            tokenized_corpus = [text.lower().split() for text in all_texts]
            tokenized_query = user_question.lower().split()
            bm25 = BM25Okapi(tokenized_corpus)
            bm25_scores = bm25.get_scores(tokenized_query)
            top_bm25_indices = [i for i, score in enumerate(bm25_scores) if score > 0]
            bm25_docs = [(doc_mapping[i], bm25_scores[i]) for i in top_bm25_indices]
            combined_docs = {}
            
            for doc, score in vector_docs:
                doc_hash = hashlib.md5(doc.page_content[:VECTOR_CONTENT_PREVIEW].encode()).hexdigest()
                if doc_hash not in combined_docs or score > combined_docs[doc_hash][1]:
                    combined_docs[doc_hash] = (doc, score * VECTOR_SEARCH_WEIGHT)
            
            for doc, score in bm25_docs:
                doc_hash = hashlib.md5(doc.page_content[:VECTOR_CONTENT_PREVIEW].encode()).hexdigest()
                if doc_hash not in combined_docs or score > combined_docs[doc_hash][1]:
                    combined_docs[doc_hash] = (doc, score)
                    
            relevant_docs = [doc for doc, _ in sorted(combined_docs.values(), key=lambda x: x[1], reverse=True)]
        
        for doc in relevant_docs:
            if not hasattr(doc, 'metadata'):
                doc.metadata = {}
            if 'source' not in doc.metadata:
                doc.metadata['source'] = 'không xác định'
            if 'page' not in doc.metadata:
                doc.metadata['page'] = 'không xác định'
        
        if len(relevant_docs) > MAX_DOCS:
            print(f"Giới hạn số lượng đoạn văn từ {len(relevant_docs)} xuống {MAX_DOCS}")
            relevant_docs = relevant_docs[:MAX_DOCS]
            
        source_grouping = {}
        for doc in relevant_docs:
            source_key = f"{doc.metadata.get('source', 'Unknown')}"
            if source_key not in source_grouping:
                source_grouping[source_key] = []
            source_grouping[source_key].append(doc)
        
        result = chain.invoke(
            {"input_documents": relevant_docs, "question": user_question}, 
            return_only_outputs=True
        )
        
        return {
            "output_text": result["output_text"],
            "source_documents": relevant_docs
        }
        
    except Exception as e:
        print(f"Lỗi trong get_gemini_response: {str(e)}")
        return {
            "output_text": "Không tìm thấy thông tin bạn đưa ra. Vui lòng đặt câu hỏi khác.",
            "source_documents": []
        } 