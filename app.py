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
    """Xử lý PDF nếu chưa có FAISS index"""
    if not (os.path.exists("faiss_index") and os.path.exists("faiss_index/index.faiss")):
        msg, success = process_directory_pdfs(
            force_reprocess=False,
            get_text_chunks_fn=get_text_chunks,
            get_vector_database_fn=get_vector_database
        )
        if not success:
            print("❌ Lỗi khi xử lý PDF:", msg)
        return success
    return True

@app.route('/chat', methods=['GET'])
def chat():
    start_time = time.time()
    question = request.args.get("text", "").strip()
    
    if not question:
        return jsonify({
            "status": "fail",
            "message": "Vui lòng nhập câu hỏi",
            "data": {
                "time": round(time.time() - start_time, 2)
            }
        }), 400

    try:
        answer = process_query(question)
        process_time = round(time.time() - start_time, 2)
        
        if "*(Kết quả từ cache" in answer:
            parts = answer.split("\n\n*(")
            main_answer = parts[0]
            return jsonify({
                "status": "success",
                "message": "Lấy câu trả lời từ cache thành công",
                "data": {
                    "question": question,
                    "answer": main_answer,
                    "source": "cache",
                    "time": process_time
                }
            })

        return jsonify({
            "status": "success",
            "message": "Tìm câu trả lời thành công",
            "data": {
                "question": question,
                "answer": answer,
                "source": "search",
                "time": process_time
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Lỗi khi xử lý câu hỏi: {str(e)}",
            "data": {"time": round(time.time() - start_time, 2)}
        }), 500

if initialize_data():
    print("✅ Dữ liệu đã khởi tạo")
else:
    print("⚠️ Dữ liệu chưa được khởi tạo hoàn chỉnh")

port = int(os.getenv("PORT", 5000))
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
else:
    print("🌐 Ứng dụng sẵn sàng cho WSGI server")
