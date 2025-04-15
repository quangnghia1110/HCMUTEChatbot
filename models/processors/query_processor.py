from models.processors.llm_chain import get_gemini_response
from models.processors.small_talk import is_small_talk
from models.storages.vector_database import load_vector_database
from models.managers.cache import query_cache
from models.managers.json import JsonQAHandler
from config import PDF_SOURCE

json = JsonQAHandler()
vector_database = None

def load_vector_db_once():
    global vector_database
    if vector_database is None:
        vector_database = load_vector_database()[0]
    return vector_database

def print_reference_sources(response, json_match=None):
    if response and "source_documents" in response:
        source_grouping = {}
        for doc in response["source_documents"]:
            source_key = f"{doc.metadata.get('source', 'Unknown')}"
            if source_key not in source_grouping:
                source_grouping[source_key] = []
            source_grouping[source_key].append(doc)
        
        print("\n" + "="*50)
        print("Nguồn tham khảo:")
        for source, docs in source_grouping.items():
            print(f"- {source}: {len(docs)} đoạn văn")
        print("="*50 + "\n")
    
    if json_match:
        print("\n" + "="*50)
        print("Nguồn tham khảo JSON:")
        print(f"- File: {json_match['source']}")
        print(f"- Dòng số: {json_match['line_number']*4}")
        print("="*50 + "\n")

def process_query(prompt):
    cached_result, cache_hit, time_saved = query_cache.get(prompt)
    if cache_hit:
        return f"{cached_result}\n\n*(Kết quả từ cache, tiết kiệm {time_saved:.2f}s)*"
    
    small_talk_response = is_small_talk(prompt)
    if small_talk_response:
        return small_talk_response
    
    try:
        vector_database = load_vector_db_once()
        if not vector_database:
            return "Xin lỗi, tôi không thể xử lý yêu cầu của bạn. Vui lòng thử lại sau."
            
        context_prompt = f"Dựa trên thông tin trong {PDF_SOURCE}, {prompt}"

        response = get_gemini_response(vector_database, context_prompt, filter_pdf=PDF_SOURCE)
        if not response:
            return "Xin lỗi, tôi không thể xử lý yêu cầu của bạn. Vui lòng thử lại sau."
        
        answer = response["output_text"]
        if not answer:
            return "Xin lỗi, không nhận được câu trả lời. Vui lòng thử lại sau."
            
        if any(phrase in answer.lower() for phrase in ["không tìm thấy thông tin", "không có thông tin"]):
            result = "Không tìm thấy thông tin bạn đưa ra. Vui lòng đặt câu hỏi khác."
        else:
            result = answer
        
        query_cache.set(prompt, result, 0)
        
        json_match = json.find_best_match(prompt)
        print_reference_sources(response, json_match)
        
        if json_match:
            result = json_match["answer"]
            query_cache.set(prompt, result, 0)
            return result
        
        return result
        
    except Exception as e:
        return "Xin lỗi, tôi không thể xử lý yêu cầu của bạn. Vui lòng thử lại sau."
