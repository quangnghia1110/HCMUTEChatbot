from flask import Flask, request, jsonify
import os
import time
from flask_cors import CORS
import google.generativeai as genai
from config import GOOGLE_API_KEY

genai.configure(api_key=GOOGLE_API_KEY)

from models.managers.pdf import process_directory_pdfs
from models.processors.text_splitter import get_text_chunks
from models.storages.vector_database import get_vector_database
from models.processors.query_processor import process_query

app = Flask(__name__)
CORS(app)

def initialize_data():
    if not (os.path.exists("faiss_index") and os.path.exists("faiss_index/index.faiss")):
        msg, success = process_directory_pdfs(
            force_reprocess=False,
            get_text_chunks_fn=get_text_chunks,
            get_vector_database_fn=get_vector_database
        )
        if not success:
            print(f"❌ Lỗi khi xử lý PDF: {msg}")
        return success
    return True

def create_response(status, message, data):
    """Tạo phản hồi JSON với cấu trúc thống nhất"""
    return jsonify({
        "status": status,
        "message": message,
        "data": data
    })

@app.route('/chat', methods=['GET'])
def chat():
    start_time = time.time()
    question = request.args.get("text", "").strip()
    
    if not question:
        return create_response("fail", "Vui lòng nhập câu hỏi", {"time": round(time.time() - start_time, 2)}), 400

    try:
        answer = process_query(question)
        process_time = round(time.time() - start_time, 2)
        
        if "*(Kết quả từ cache" in answer:
            parts = answer.split("\n\n*(")
            main_answer = parts[0]
            return create_response("success", "Lấy câu trả lời từ cache thành công", {
                "question": question,
                "answer": main_answer,
                "time": process_time
            })

        return create_response("success", "Tìm câu trả lời thành công", {
            "question": question,
            "answer": answer,
            "time": process_time
        })

    except ValueError as ve:
        return create_response("error", f"Lỗi giá trị: {str(ve)}", {"time": round(time.time() - start_time, 2)}), 400
    except ConnectionError as ce:
        return create_response("error", f"Lỗi kết nối: {str(ce)}", {"time": round(time.time() - start_time, 2)}), 503
    except Exception as e:
        return create_response("error", f"Lỗi khi xử lý câu hỏi: {str(e)}", {"time": round(time.time() - start_time, 2)}), 500

if initialize_data():
    print("✅ Dữ liệu đã khởi tạo")
else:
    print("⚠️ Dữ liệu chưa được khởi tạo hoàn chỉnh")

port = int(os.getenv("PORT", 2000))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
else:
    print("🌐 Ứng dụng sẵn sàng cho WSGI server")
