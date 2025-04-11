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
    - Trả lời thân thiện, đầy đủ nhưng ngắn gọn, dùng bullet nếu cần chia mục.
    - Bắt đầu câu trả lời bằng "Chào bạn," hoặc các từ ngữ thân thiện tương tự.
    - Kết thúc câu trả lời bằng các cụm từ như "Câu trả lời như thế bạn đã hài lòng hay chưa ạ?. Nếu còn câu hỏi nào vui lòng hỏi để mình giúp bạn trả lời" nếu phù hợp.
    - Không đề cập đến độ tin cậy.

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
                    "source_documents": []
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
                return {
                    "output_text": result["output_text"],
                    "source_documents": relevant_docs
                }
            except Exception as e:
                retries += 1
                if retries == MAX_RETRIES:
                    print(f"Lỗi sau {MAX_RETRIES} lần thử: {str(e)}")
                    return {
                        "output_text": "Không tìm thấy thông tin. Vui lòng hỏi lại.",
                        "source_documents": []
                    }
                print(f"Lỗi lần {retries}: {str(e)}. Thử lại sau {BASE_DELAY} giây...")
                time.sleep(BASE_DELAY)
    
    except Exception as e:
        print(f"Lỗi: {str(e)}")
        return {
            "output_text": "Không tìm thấy thông tin. Vui lòng hỏi lại.",
            "source_documents": []
        }