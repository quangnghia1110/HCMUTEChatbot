import hashlib
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from rank_bm25 import BM25Okapi
from config import (
    GEMINI_MODEL, TEMPERATURE, MAX_OUTPUT_TOKENS, 
    TOP_K, TOP_P, MAX_RETRIES, BASE_DELAY, MAX_DOCS,
    SEMANTIC_WEIGHT, KEYWORD_WEIGHT, VECTOR_SEARCH_K,
    VECTOR_CONTENT_PREVIEW, VECTOR_SEARCH_WEIGHT
)

def get_conversational_chain():
    prompt_template = """
    Bạn là trợ lý AI thân thiện, chuyên phân tích tài liệu PDF. Trả lời câu hỏi dựa CHỈ vào nội dung tài liệu được cung cấp.

    **Quy tắc**:
    - Chỉ dùng thông tin từ tài liệu dưới đây.
    - Không bịa đặt hoặc thêm thông tin ngoài tài liệu.
    - Nếu không có thông tin, trả lời: "Xin lỗi, mình không tìm thấy thông tin này trong tài liệu. Bạn có thể hỏi lại hoặc tham khảo thêm từ phòng công tác sinh viên nhé."
    - Trả lời thân thiện, đầy đủ nhưng ngắn gọn.
    - Bắt đầu câu trả lời bằng "Chào bạn," hoặc các từ ngữ thân thiện tương tự.
    - Kết thúc câu trả lời bằng các cụm từ như "Câu trả lời như thế bạn đã hài lòng hay chưa ạ?. Nếu còn câu hỏi nào vui lòng hỏi để mình giúp bạn trả lời" nếu phù hợp.
    - Không đề cập đến độ tin cậy.
    
    **Hướng dẫn về bảng**:
    - Khi trình bày dữ liệu dạng bảng, sử dụng định dạng Markdown table với cột và hàng rõ ràng.
    - Ghi rõ tiêu đề các cột.
    - Đảm bảo căn chỉnh các cột phù hợp.
    - Không sử dụng bullet points cho dữ liệu bảng.
    - Trình bày đầy đủ giá trị của từng ô trong bảng.
    
    **Ví dụ về định dạng bảng**:
    ```
    | Xếp loại | Điểm số | Điểm quy đổi |
    |----------|---------|--------------|
    | Xuất sắc | 9.50-10 | 18           |
    | Giỏi     | 8.50-8.99 | 16         |
    ```

    **Tài liệu**: {context}

    **Câu hỏi**: {question}

    **Trả lời** (dùng Markdown, thân thiện và chi tiết):
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
    
    return load_qa_chain(llm, chain_type="stuff", prompt=prompt)

def get_gemini_response(vector_database, user_question, filter_pdf=None):
    chain = get_conversational_chain()
    
    try:
        if filter_pdf:
            docs = [
                doc for doc_id, doc in vector_database.docstore._dict.items()
                if doc.metadata.get("source") == filter_pdf
            ]
            if not docs:
                return {
                    "output_text": "Không tìm thấy thông tin. Vui lòng hỏi lại.",
                    "source_documents": [],
                    "structured_tables": []
                }
            
            texts = [doc.page_content for doc in docs]
            tokenized_corpus = [text.lower().split() for text in texts]
            bm25 = BM25Okapi(tokenized_corpus)
            bm25_scores = bm25.get_scores(user_question.lower().split())
            scored_docs = sorted(
                [(doc, score) for doc, score in zip(docs, bm25_scores) if score > 0],
                key=lambda x: x[1],
                reverse=True
            )
            relevant_docs = [doc for doc, _ in scored_docs] or docs
        else:
            vector_docs = vector_database.similarity_search_with_relevance_scores(
                user_question, k=VECTOR_SEARCH_K
            )
            
            texts = [doc.page_content for doc, _ in vector_docs]
            tokenized_corpus = [text.lower().split() for text in texts]
            bm25 = BM25Okapi(tokenized_corpus)
            bm25_scores = bm25.get_scores(user_question.lower().split())
            
            combined_docs = {}
            for i, (doc, vector_score) in enumerate(vector_docs):
                doc_hash = hashlib.md5(doc.page_content[:VECTOR_CONTENT_PREVIEW].encode()).hexdigest()
                combined_score = (
                    vector_score * SEMANTIC_WEIGHT +
                    bm25_scores[i] * KEYWORD_WEIGHT
                ) * VECTOR_SEARCH_WEIGHT
                combined_docs[doc_hash] = (
                    doc,
                    max(
                        combined_docs.get(doc_hash, (None, 0))[1],
                        combined_score
                    )
                )
            
            relevant_docs = [
                doc for doc, _ in sorted(combined_docs.values(), key=lambda x: x[1], reverse=True)
            ]
        
        for doc in relevant_docs:
            if not hasattr(doc, 'metadata'):
                doc.metadata = {}
            doc.metadata.setdefault('source', 'không xác định')
            doc.metadata.setdefault('page', 'không xác định')
        
        relevant_docs = relevant_docs[:MAX_DOCS]
        
        retries = 0
        while retries < MAX_RETRIES:
            try:
                result = chain.invoke(
                    {"input_documents": relevant_docs, "question": user_question},
                    return_only_outputs=True
                )
                
                # Áp dụng hậu xử lý cho bảng
                processed_result = post_process_tables(result["output_text"])
                
                return {
                    "output_text": processed_result["original_response"],
                    "source_documents": relevant_docs,
                    "structured_tables": processed_result["structured_tables"]
                }
            except Exception as e:
                retries += 1
                if retries == MAX_RETRIES:
                    print(f"Lỗi sau {MAX_RETRIES} lần thử: {str(e)}")
                    return {
                        "output_text": "Không tìm thấy thông tin. Vui lòng hỏi lại.",
                        "source_documents": [],
                        "structured_tables": []
                    }
                print(f"Lỗi lần {retries}: {str(e)}. Thử lại sau {BASE_DELAY} giây...")
                time.sleep(BASE_DELAY)
    
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return {
            "output_text": "Không tìm thấy thông tin. Vui lòng hỏi lại.",
            "source_documents": [],
            "structured_tables": []
        }

def post_process_tables(response):
    """Xử lý và cấu trúc lại các bảng trong phản hồi để dễ dàng chuyển đổi"""
    # Phát hiện các bảng Markdown trong phản hồi
    import re
    
    # Tìm tất cả các bảng Markdown
    table_pattern = r'\|[^\n]+\|\n\|[-|\s]+\|\n(\|[^\n]+\|\n)+'
    tables = re.findall(table_pattern, response)
    
    structured_tables = []
    for table in tables:
        lines = table.strip().split('\n')
        headers = [h.strip() for h in lines[0].split('|')[1:-1]]
        
        data = []
        for row in lines[2:]:  # Bỏ qua header và dòng phân cách
            if row.strip():
                values = [cell.strip() for cell in row.split('|')[1:-1]]
                row_data = {headers[i]: values[i] for i in range(min(len(headers), len(values)))}
                data.append(row_data)
        
        structured_tables.append({
            'headers': headers,
            'data': data
        })
    
    return {
        'original_response': response,
        'structured_tables': structured_tables
    }