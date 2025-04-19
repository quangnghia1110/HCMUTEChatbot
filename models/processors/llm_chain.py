import hashlib
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from config import (
    GEMINI_MODEL, TEMPERATURE, MAX_OUTPUT_TOKENS, 
    TOP_K, TOP_P, MAX_RETRIES, BASE_DELAY, MAX_DOCS,
    VECTOR_SEARCH_K,
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
    - Kết thúc câu trả lời bằng các cụm từ như "Cảm ơn câu hỏi của bạn nếu còn câu hỏi nào vui lòng hỏi để mình giúp bạn trả lời" nếu phù hợp.
    - Không đề cập đến độ tin cậy.
    
    **Hướng dẫn về định dạng**:
    - Khi câu kết thúc bằng "bao gồm:", "như là:", "gồm:", "như sau:", "điều sau:" hoặc dấu hai chấm (:), hãy trình bày thông tin tiếp theo dưới dạng danh sách có cấu trúc với bullet points (sử dụng dấu * hoặc -).
    - Đảm bảo thụt đầu dòng các bullet points để tạo cấu trúc phân cấp rõ ràng.
    
    **Xử lý danh sách từ PDF**:
    - Nhận dạng các dòng bắt đầu bằng "•", "○", "▪", "▫", "►", "➢", "➤", "→", "-" hoặc các dấu tương tự như bullet points.
    - Nhận dạng các dòng bắt đầu bằng "□", "☐", "◯", "○", "⬜" như checkbox chưa chọn.
    - Nhận dạng các dòng bắt đầu bằng "■", "☑", "☒", "●", "⬛" như checkbox đã chọn.
    - Áp dụng cấu trúc phân cấp dựa trên khoảng cách thụt đầu dòng:
      * Nếu dòng thụt vào nhiều hơn so với dòng trên, coi đó là sub-bullet của dòng trên.
      * Nếu một dòng có khoảng cách thụt đầu dòng giống dòng trước, coi chúng cùng cấp.
    - Chuyển đổi từ định dạng PDF sang Markdown bằng cách:
      * Dùng dấu "*" hoặc "-" cho các bullet points.
      * Thụt đầu dòng 2 hoặc 4 khoảng trắng cho sub-bullets.
      * Dùng "- [ ]" cho checkbox chưa chọn và "- [x]" cho checkbox đã chọn.
    
    **Hướng dẫn về bảng**:
    - Khi trình bày dữ liệu dạng bảng, phải sử dụng định dạng Markdown table với cột và hàng rõ ràng.
    - Ghi rõ tiêu đề các cột.
    - Đảm bảo căn chỉnh các cột phù hợp.
    - Không sử dụng bullet points cho dữ liệu bảng.
    - Trình bày đầy đủ giá trị của từng ô trong bảng.
    
    **Ví dụ về định dạng bảng đúng**:
    ```
    | Xếp loại | Điểm số | Điểm quy đổi |
    |----------|---------|--------------|
    | Xuất sắc | 9.50-10 | 18           |
    | Giỏi     | 8.50-8.99 | 16         |
    ```
    
    **Ví dụ về định dạng danh sách có cấu trúc đúng**:
    Các thành phần của quy trình bao gồm:
    * Bước 1: Đăng ký học phần
    * Bước 2: Thanh toán học phí
      * Thanh toán trực tiếp
      * Thanh toán online
    * Bước 3: Xác nhận hoàn tất

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
            docs = [doc for doc_id, doc in vector_database.docstore._dict.items() if doc.metadata.get("source") == filter_pdf]
            if not docs:
                return {"output_text": "Không tìm thấy thông tin. Vui lòng hỏi lại.", "source_documents": [], "structured_tables": []}
            relevant_docs = docs[:MAX_DOCS]
        else:
            vector_docs = vector_database.similarity_search(user_question, k=VECTOR_SEARCH_K)
            relevant_docs = vector_docs[:MAX_DOCS]
        
        for doc in relevant_docs:
            if not hasattr(doc, 'metadata'):
                doc.metadata = {}
            doc.metadata.setdefault('source', 'không xác định')
            doc.metadata.setdefault('page', 'không xác định')
        
        retries = 0
        while retries < MAX_RETRIES:
            try:
                result = chain.invoke({"input_documents": relevant_docs, "question": user_question}, return_only_outputs=True)
                processed_result = post_process_tables(result["output_text"])
                return {"output_text": processed_result["original_response"], "source_documents": relevant_docs, "structured_tables": processed_result["structured_tables"]}
            except Exception as e:
                retries += 1
                if retries == MAX_RETRIES:
                    print(f"Lỗi sau {MAX_RETRIES} lần thử: {str(e)}")
                    return {"output_text": "Không tìm thấy thông tin. Vui lòng hỏi lại.", "source_documents": [], "structured_tables": []}
                print(f"Lỗi lần {retries}: {str(e)}. Thử lại sau {BASE_DELAY} giây...")
                time.sleep(BASE_DELAY)
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return {"output_text": "Không tìm thấy thông tin. Vui lòng hỏi lại.", "source_documents": [], "structured_tables": []}

def post_process_tables(response):
    import re
    table_pattern = r'\|[^\n]+\|\n\|[-|\s]+\|\n(\|[^\n]+\|\n)+'
    tables = re.findall(table_pattern, response)
    structured_tables = []
    for table in tables:
        lines = table.strip().split('\n')
        headers = [h.strip() for h in lines[0].split('|')[1:-1]]
        data = []
        for row in lines[2:]:
            if row.strip():
                values = [cell.strip() for cell in row.split('|')[1:-1]]
                row_data = {headers[i]: values[i] for i in range(min(len(headers), len(values)))}
                data.append(row_data)
        structured_tables.append({'headers': headers, 'data': data})
    return {'original_response': response, 'structured_tables': structured_tables}