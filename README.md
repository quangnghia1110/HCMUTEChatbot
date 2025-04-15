# HCMUTE Chatbot - Trợ lý tư vấn thông minh

Hệ thống chatbot được thiết kế để trả lời câu hỏi dựa trên tài liệu PDF và các cặp câu hỏi-câu trả lời được định nghĩa trước, tập trung vào thông tin sổ tay sinh viên.

## Tính năng

- **Xử lý tài liệu PDF**: Chuyển đổi tài liệu thành các đoạn văn bản (chunk) và vector để tìm kiếm
- **Tìm kiếm ngữ nghĩa**: Sử dụng cơ sở dữ liệu vector FAISS kết hợp với BM25 để tìm kiếm thông tin chính xác
- **Trả lời thông minh**: Sử dụng mô hình Gemini của Google để sinh câu trả lời dựa trên ngữ cảnh
- **Hệ thống cache**: Giảm thời gian phản hồi và tài nguyên xử lý lặp lại
- **Small Talk**: Khả năng nhận diện và trả lời các câu hỏi chào hỏi, tạm biệt, cảm ơn...
- **Câu hỏi-trả lời định nghĩa trước**: Hỗ trợ dữ liệu JSON để trả lời nhanh các câu hỏi phổ biến
- **Giao diện API**: REST API dễ dàng tích hợp với các ứng dụng khác

## Công nghệ sử dụng

### RAG (Retrieval-Augmented Generation)
Hệ thống hoạt động trên nền tảng RAG - kết hợp giữa mô hình ngôn ngữ lớn (LLM) với hệ thống truy xuất thông tin:
- **Truy xuất (Retrieval)**: Khi nhận câu hỏi, hệ thống tìm kiếm thông tin liên quan trong cơ sở dữ liệu vector FAISS qua kỹ thuật tìm kiếm ngữ nghĩa, kết hợp với tìm kiếm từ khóa BM25.
- **Tăng cường (Augmentation)**: Thông tin được truy xuất sẽ trở thành ngữ cảnh bổ sung cho prompt gửi đến mô hình LLM.
- **Sinh nội dung (Generation)**: Mô hình Gemini sinh câu trả lời dựa trên ngữ cảnh được cung cấp, đảm bảo chính xác và căn cứ vào tài liệu.

### LangChain
LangChain được sử dụng làm framework chính để xây dựng hệ thống RAG:
- **Text Splitters**: Sử dụng RecursiveCharacterTextSplitter để phân đoạn tài liệu thành các phần nhỏ với kích thước và độ chồng lấp có thể tùy chỉnh
- **Embeddings**: Tích hợp với Google Generative AI Embeddings để chuyển đổi văn bản thành vector
- **Vector Stores**: Sử dụng FAISS làm cơ sở dữ liệu vector qua wrapper của LangChain
- **Retrieval Chains**: Xây dựng chuỗi xử lý để truy xuất tài liệu và kết hợp với LLM
- **Prompt Templates**: Template chuyên biệt tối ưu hóa chất lượng câu trả lời

### Google Gemini
Mô hình LLM của Google được sử dụng cho:
- **Embedding**: Chuyển đổi văn bản thành vector ngữ nghĩa 
- **Text Generation**: Sinh câu trả lời từ ngữ cảnh và câu hỏi

## Yêu cầu hệ thống

- Python 3.8 trở lên
- Google API Key cho mô hình Gemini
- Dung lượng lưu trữ đủ cho cơ sở dữ liệu vector
- Tài liệu PDF để xử lý (mặc định: SoTaySinhVien2024.pdf)

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/yourusername/hcmute-consultant-chatbot.git
cd hcmute-consultant-chatbot
```

2. Tạo và kích hoạt môi trường ảo:
```bash
python -m venv venv
source venv/bin/activate  # Cho Linux/Mac
venv\Scripts\activate     # Cho Windows
```

3. Cài đặt thư viện phụ thuộc:
```bash
pip install -r requirements.txt
```

4. Tạo tệp `.env` với cấu hình cần thiết (xem phần Cấu hình)

5. Đặt tài liệu PDF vào thư mục `data/`

6. (Tùy chọn) Tạo file JSON câu hỏi-câu trả lời trong thư mục `data/`

## Cấu hình

Tạo tệp `.env` với các cấu hình sau:

```env
# Google API
GOOGLE_API_KEY=your_api_key_here

# Cấu hình mô hình
GEMINI_MODEL=gemini-1.5-flash
EMBEDDING_MODEL=models/embedding-001
TEMPERATURE=0.7
MAX_OUTPUT_TOKENS=2048
TOP_K=40
TOP_P=0.8
MAX_RETRIES=3
BASE_DELAY=2

# Cấu hình PDF
PDF_SOURCE=SoTaySinhVien2024.pdf

# Cài đặt Vector Store
CHUNK_SIZE=8000
CHUNK_OVERLAP=1500
MAX_DOCS=200

# Cài đặt tìm kiếm
SIMILARITY_THRESHOLD=0.5
SEMANTIC_WEIGHT=0.7
KEYWORD_WEIGHT=0.3
VECTOR_SEARCH_K=30
VECTOR_CONTENT_PREVIEW=300
VECTOR_SEARCH_WEIGHT=1.5
```

## Cấu trúc dự án

```
hcmute-consultant-chatbot/
│
├── data/                   # Thư mục chứa dữ liệu
│   ├── SoTaySinhVien2024.pdf   # File PDF mặc định
│   └── output.json         # File JSON chứa cặp câu hỏi-trả lời
│
├── faiss_index/            # Thư mục lưu trữ vector database
│   ├── index.faiss         # File chỉ mục FAISS
│   └── index.pkl           # File pickle cho metadata
│
├── models/
│   ├── managers/           # Các thành phần quản lý
│   │   ├── cache.py        # Quản lý cache
│   │   ├── json.py         # Quản lý JSON Q&A
│   │   └── pdf.py          # Xử lý tài liệu PDF
│   │
│   ├── processors/         # Các thành phần xử lý
│   │   ├── llm_chain.py    # Xử lý chuỗi LLM
│   │   ├── query_processor.py  # Xử lý truy vấn
│   │   ├── small_talk.py   # Xử lý small talk
│   │   └── text_splitter.py    # Chia nhỏ văn bản
│   │
│   └── storages/           # Các thành phần lưu trữ
│       └── vector_database.py  # Quản lý FAISS vector database
│
├── output/                 # Thư mục đầu ra và cache
│   └── query_cache.json    # File cache lưu các câu hỏi và câu trả lời
│
├── .env                    # File cấu hình biến môi trường
├── app.py                  # File chính của ứng dụng
├── config.py               # File cấu hình hệ thống
├── requirements.txt        # Danh sách thư viện cần cài đặt
└── README.md               # Tài liệu hướng dẫn
```

## Chi tiết các thành phần

### 1. Quản lý cache (`models/managers/cache.py`)
- Lưu trữ kết quả truy vấn để sử dụng lại khi có truy vấn tương tự
- Sử dụng hash MD5 của câu hỏi để tìm kiếm nhanh trong cache
- Lưu trữ thời gian xử lý để đánh giá hiệu suất và hiển thị thời gian tiết kiệm

### 2. Xử lý JSON Q&A (`models/managers/json.py`)
- Tải dữ liệu câu hỏi-trả lời từ file output.json
- Sử dụng thuật toán SequenceMatcher để tìm câu hỏi tương tự
- Kết hợp score từ matching theo chuỗi và từ khóa cho độ chính xác cao
- Cho phép thiết lập ngưỡng độ tương đồng (threshold)

### 3. Xử lý PDF (`models/managers/pdf.py`)
- Đọc và xử lý file PDF từ thư mục `data/`
- Trích xuất văn bản từ từng trang với metadata đầy đủ
- Quản lý việc tạo lại hoặc sử dụng lại vector store đã lưu

### 4. LLM Chain (`models/processors/llm_chain.py`)
- Định nghĩa prompt template chi tiết với hướng dẫn định dạng bảng, danh sách...
- Khởi tạo và cấu hình mô hình Gemini
- Kết hợp tìm kiếm vector và BM25 cho kết quả tốt nhất
- Xử lý post-processing cho bảng và dữ liệu có cấu trúc

### 5. Xử lý truy vấn (`models/processors/query_processor.py`)
- Điều phối luồng xử lý câu hỏi
- Kiểm tra cache và small talk trước khi truy vấn vector store
- In nguồn tham khảo để dễ dàng debug và đánh giá
- Quản lý việc lưu cache và trả về kết quả

### 6. Xử lý Small Talk (`models/processors/small_talk.py`)
- Phát hiện và phản hồi các câu chào hỏi, tạm biệt, cảm ơn...
- Lọc nội dung không phù hợp hoặc nhạy cảm
- Hướng người dùng về mục đích chính của chatbot
- Phát hiện các câu hỏi ngoài phạm vi

### 7. Phân đoạn văn bản (`models/processors/text_splitter.py`)
- Sử dụng RecursiveCharacterTextSplitter để chia nhỏ văn bản
- Cấu hình kích thước chunk và độ chồng lấp
- Bảo toàn metadata trong quá trình xử lý

### 8. Vector Database (`models/storages/vector_database.py`)
- Tạo và quản lý cơ sở dữ liệu vector FAISS
- Chuyển đổi văn bản thành embeddings
- Lưu trữ và tải vector database từ đĩa

### 9. API (`app.py`)
- Cung cấp REST API endpoint `/chat`
- Khởi tạo dữ liệu khi ứng dụng khởi động
- Xử lý request và định dạng response
- Đo thời gian xử lý cho từng truy vấn

## Luồng xử lý

### 1. Khởi tạo dữ liệu
```
app.py (initialize_data) → pdf.py (process_directory_pdfs) → text_splitter.py (get_text_chunks) → vector_database.py (get_vector_database)
```

### 2. Xử lý truy vấn
```
app.py (/chat) → query_processor.py (process_query) → 
  ├─ cache.py (query_cache.get) → [Cache hit] → Trả về kết quả
  └─ [Cache miss] → small_talk.py (is_small_talk) →
      ├─ [Small talk] → Trả về câu trả lời small talk
      └─ [Không phải small talk] → 
          ├─ vector_database.py (load_vector_database)
          ├─ llm_chain.py (get_gemini_response)
          ├─ json.py (find_best_match)
          └─ cache.py (query_cache.set)
```

## API Endpoints

### Truy vấn chatbot
```
GET /chat?text=<câu_hỏi>
```

#### Tham số
- `text`: Câu hỏi của người dùng

#### Phản hồi
```json
{
    "status": "success",
    "message": "Tìm câu trả lời thành công",
    "data": {
        "question": "Câu hỏi gốc",
        "answer": "Câu trả lời được tạo",
        "source": "search/cache",
        "time": "Thời gian xử lý (giây)"
    }
}
```

## Cách tùy chỉnh

### Thêm tài liệu mới
1. Đặt file PDF mới vào thư mục `data/`
2. Cập nhật biến `PDF_SOURCE` trong file `.env`
3. Khởi động lại ứng dụng

### Thêm câu hỏi-trả lời định sẵn
1. Tạo hoặc cập nhật file `data/output.json` với định dạng:
```json
[
  {
    "question": "Câu hỏi 1",
    "answer": "Câu trả lời 1"
  },
  {
    "question": "Câu hỏi 2",
    "answer": "Câu trả lời 2"
  }
]
```

### Điều chỉnh độ chính xác
- Thay đổi `TEMPERATURE`, `TOP_K`, `TOP_P` trong file `.env` để điều chỉnh tính sáng tạo của mô hình
- Cập nhật `SEMANTIC_WEIGHT`, `KEYWORD_WEIGHT` để thay đổi tỷ lệ giữa tìm kiếm ngữ nghĩa và từ khóa
- Điều chỉnh `VECTOR_SEARCH_K` để tăng/giảm số lượng đoạn văn bản được tìm kiếm

## Khởi động ứng dụng

```bash
python app.py
```

Ứng dụng sẽ chạy trên cổng 2000 theo mặc định: `http://0.0.0.0:2000`

## Lưu ý

- Khi chạy lần đầu, hệ thống sẽ tạo vector database từ tài liệu PDF, quá trình này có thể mất thời gian
- Cần đảm bảo API key Gemini hợp lệ trong file `.env`
- Kết quả tìm kiếm sẽ phụ thuộc vào chất lượng tài liệu PDF và cách phân đoạn văn bản
- Tùy thuộc vào kích thước và độ phức tạp của tài liệu, có thể cần điều chỉnh `CHUNK_SIZE` và `CHUNK_OVERLAP`
