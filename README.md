# HCMUTE Chatbot

Hệ thống chatbot được thiết kế để trả lời câu hỏi dựa trên tài liệu PDF và các cặp câu hỏi-câu trả lời được định nghĩa trước, tập trung vào thông tin sổ tay sinh viên.

## Tính năng

- Xử lý tài liệu PDF và chuyển đổi thành vector
- Tìm kiếm ngữ nghĩa sử dụng cơ sở dữ liệu vector FAISS
- Trả lời câu hỏi sử dụng mô hình Gemini của Google
- Hệ thống cache để phản hồi nhanh hơn
- Xử lý small talk
- Hỗ trợ câu hỏi-trả lời dựa trên JSON
- Giao diện REST API

## Công nghệ sử dụng

### RAG (Retrieval-Augmented Generation)
Hệ thống được xây dựng trên nền tảng RAG - một kỹ thuật kết hợp giữa mô hình ngôn ngữ lớn (LLM) với hệ thống truy xuất thông tin:
- **Truy xuất (Retrieval)**: Khi nhận câu hỏi, hệ thống tìm kiếm thông tin liên quan trong cơ sở dữ liệu vector FAISS thông qua kỹ thuật tìm kiếm ngữ nghĩa. Quá trình này giúp tìm ra những đoạn văn bản liên quan nhất từ tài liệu nguồn.
- **Tăng cường (Augmentation)**: Thông tin được truy xuất sẽ được đưa vào prompt làm ngữ cảnh bổ sung cho mô hình LLM.
- **Sinh nội dung (Generation)**: Mô hình Gemini sẽ sinh câu trả lời dựa trên ngữ cảnh được cung cấp, đảm bảo câu trả lời chính xác và dựa trên thông tin từ tài liệu gốc.

Ưu điểm RAG trong dự án:
- Cải thiện độ chính xác thông tin
- Giảm thiểu "ảo giác" (hallucination) của LLM
- Luôn cập nhật với dữ liệu trong tài liệu nguồn
- Trả lời dựa trên nguồn dữ liệu cụ thể

### LangChain
LangChain được sử dụng như framework chính để xây dựng hệ thống RAG:
- **Text Splitters**: LangChain cung cấp các công cụ chia nhỏ văn bản (RecursiveCharacterTextSplitter) giúp phân đoạn tài liệu PDF thành các phần nhỏ phù hợp.
- **Embeddings**: Tích hợp với Google Generative AI Embeddings để chuyển đổi văn bản thành vector.
- **Vector Stores**: Sử dụng FAISS làm cơ sở dữ liệu vector qua wrapper của LangChain.
- **Retrieval Chains**: Xây dựng chuỗi xử lý để truy xuất tài liệu liên quan và kết hợp với LLM.
- **Prompt Templates**: Định nghĩa template cho prompt để tối ưu hóa câu trả lời.

### Google Gemini
Gemini là mô hình LLM của Google được sử dụng cho hai mục đích chính:
- **Embedding**: Sử dụng Gemini Embedding để chuyển đổi văn bản thành vector ngữ nghĩa chất lượng cao.
- **Text Generation**: Sử dụng Gemini 1.5 Flash để sinh câu trả lời dựa trên ngữ cảnh và câu hỏi.

Ưu điểm của Gemini trong dự án:
- Hiệu suất cao với văn bản tiếng Việt
- Khả năng hiểu ngữ cảnh dài và phức tạp
- Tốc độ xử lý nhanh
- Chi phí hợp lý

## Yêu cầu hệ thống

- Python 3.8 trở lên
- Google API Key cho mô hình Gemini
- Dung lượng lưu trữ đủ cho cơ sở dữ liệu vector
- Tài liệu PDF để xử lý (mặc định: SoTaySinhVien2024.pdf)

## Cài đặt

1. Clone repository về máy:
```bash
git clone https://github.com/quangnghia1110/HCMUTEChatbot.git
cd HCMUTEChatbot
```

2. Tạo và kích hoạt môi trường ảo:
```bash
python -m venv venv
source venv/bin/activate  # Cho Linux/Mac
venv\Scripts\activate     # Cho Windows
```

3. Cài đặt các thư viện phụ thuộc:
```bash
pip install -r requirements.txt
```

4. Tạo tệp `.env` với cấu hình cần thiết (xem phần Cấu hình)

5. Đảm bảo đã đặt tập tin PDF (mặc định SoTaySinhVien2024.pdf) vào thư mục `data/`

6. (Tùy chọn) Tạo file JSON câu hỏi-câu trả lời trong thư mục `data/`

## Cấu hình

Tạo tệp `.env` với các cấu hình sau:

```env
# API Keys
GOOGLE_API_KEY=your_api_key_here

# Cấu hình mô hình
GEMINI_MODEL=gemini-1.5-flash
EMBEDDING_MODEL=models/embedding-001
TEMPERATURE=0.7
MAX_OUTPUT_TOKENS=2048
TOP_K=40
TOP_P=0.8

# Cấu hình PDF
DEFAULT_PDF=SoTaySinhVien2024.pdf

# Cài đặt Cache
CACHE_MAX_AGE_DAYS=30

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
HCMUTEChatbot/
│
├── data/                   # Thư mục chứa dữ liệu
│   ├── SoTaySinhVien2024.pdf   # File PDF mặc định
│   └── output.json         # File JSON chứa cặp câu hỏi-trả lời định nghĩa trước
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
│   └── query_cache.json    # File cache lưu các câu hỏi và câu trả lời đã xử lý
│
├── .env                    # File cấu hình biến môi trường
├── app.py                  # File chính của ứng dụng
├── requirements.txt        # Danh sách thư viện cần cài đặt
└── README.md               # Tài liệu hướng dẫn
```

## Kiến trúc RAG chi tiết

### 1. Quá trình xây dựng Vector Database

```
Tài liệu PDF → PDF Processing → Text Extraction → Text Splitting → Embedding → FAISS Vector DB
```

1. **Tải tài liệu PDF**:
   - Đọc từ thư mục `data/` sử dụng PyPDF2
   - Trích xuất văn bản từ từng trang

2. **Tiền xử lý văn bản**:
   - Làm sạch văn bản
   - Thêm metadata (nguồn, trang)

3. **Phân đoạn văn bản**:
   - Sử dụng LangChain's RecursiveCharacterTextSplitter
   - Cấu hình kích thước đoạn và độ chồng lấp

4. **Tạo Embedding**:
   - Sử dụng GoogleGenerativeAIEmbeddings
   - Chuyển đổi mỗi đoạn văn bản thành vector 768 chiều

5. **Lưu trữ Vector**:
   - Lưu trong FAISS để tìm kiếm hiệu quả
   - Lưu metadata kèm theo vector

### 2. Quá trình truy vấn

```
Câu hỏi → Embedding → Vector Search → BM25 Re-ranking → Context Selection → LLM → Câu trả lời
```

1. **Xử lý câu hỏi**:
   - Kiểm tra cache trước
   - Phát hiện small talk
   - Chuyển câu hỏi thành embedding

2. **Tìm kiếm ngữ nghĩa**:
   - Sử dụng FAISS similarity search
   - Lấy top-k đoạn văn bản liên quan nhất

3. **Re-ranking với BM25**:
   - Kết hợp tìm kiếm vector với BM25
   - Cân bằng tìm kiếm ngữ nghĩa với tìm kiếm từ khóa

4. **Xây dựng ngữ cảnh**:
   - Kết hợp đoạn văn bản được chọn làm ngữ cảnh
   - Đảm bảo không vượt quá giới hạn token

5. **Sinh câu trả lời**:
   - Sử dụng Gemini để tạo câu trả lời
   - Áp dụng prompt template đặc biệt để định hướng mô hình

6. **Lưu cache**:
   - Lưu câu hỏi, câu trả lời và thời gian xử lý vào cache

## Luồng hoạt động của hệ thống

### 1. Khởi động và chuẩn bị dữ liệu

```
app.py (initialize_data)
  ↓
models/managers/pdf.py (process_directory_pdfs)
  ↓
models/processors/text_splitter.py (get_text_chunks)
  ↓
models/storages/vector_database.py (get_vector_database)
```

- **app.py**: Khởi động ứng dụng Flask, kiểm tra xem đã có faiss_index chưa
- **pdf.py**: Đọc và xử lý file PDF, trích xuất nội dung văn bản
- **text_splitter.py**: Chia nhỏ văn bản thành các đoạn phù hợp
- **vector_database.py**: Tạo embeddings và lưu trữ trong database FAISS

### 2. Xử lý truy vấn người dùng

```
app.py (route /chat)
  ↓
models/processors/query_processor.py (process_query)
  ↓
models/managers/cache.py (query_cache.get)
  |
  ├─ [Cache hit] → Trả về kết quả từ cache
  │
  └─ [Cache miss] → models/processors/small_talk.py (is_small_talk)
      |
      ├─ [Small talk] → Trả về câu trả lời small talk
      │
      └─ [Không phải small talk] → models/storages/vector_database.py (load_vector_database)
          ↓
          models/processors/llm_chain.py (get_gemini_response)
          ↓
          models/managers/json.py (find_best_match)
          ↓
          models/managers/cache.py (query_cache.set)
          ↓
          Trả về kết quả cho người dùng
```

- **app.py**: Nhận request từ người dùng và gọi process_query
- **query_processor.py**: Điều phối quá trình xử lý truy vấn
- **cache.py**: Kiểm tra cache trước khi xử lý (tối ưu hiệu suất)
- **small_talk.py**: Xác định và xử lý câu hỏi chào hỏi, tạm biệt, v.v.
- **vector_database.py**: Tải cơ sở dữ liệu vector để tìm kiếm
- **llm_chain.py**: Xử lý câu hỏi bằng mô hình LLM Gemini
- **json.py**: Tìm kiếm câu trả lời từ dữ liệu JSON định nghĩa trước

## Chi tiết các thành phần

### 1. PDF Processing (`models/managers/pdf.py`)
- Xử lý file PDF từ thư mục `data/`
- Trích xuất nội dung văn bản từ từng trang PDF
- Lưu thông tin metadata về nguồn tài liệu và số trang
- Trả về nội dung để xử lý tiếp theo

### 2. Text Splitter (`models/processors/text_splitter.py`)
- Nhận văn bản đã trích xuất từ PDF
- Chia nhỏ thành các đoạn (chunks) có độ dài phù hợp
- Đảm bảo các đoạn có độ chồng lấp (overlap) để không mất thông tin
- Giữ nguyên metadata trong quá trình xử lý

### 3. Vector Database (`models/storages/vector_database.py`)
- Tạo vector embeddings cho các đoạn văn bản
- Sử dụng Google Generative AI Embeddings
- Lưu trữ trong cơ sở dữ liệu FAISS cho tìm kiếm tương tự
- Cung cấp chức năng tìm kiếm tương tự (similarity search)

### 4. Cache System (`models/managers/cache.py`)
- Lưu trữ kết quả truy vấn vào bộ nhớ cache
- Sử dụng hash MD5 cho việc tìm kiếm trong cache
- Quản lý thời hạn cache (mặc định 30 ngày)
- Lưu cache trong file query_cache.json trong thư mục output/
- Tiết kiệm thời gian và tài nguyên khi có truy vấn lặp lại

### 5. JSON Q&A Handler (`models/managers/json.py`)
- Tải dữ liệu câu hỏi-trả lời từ file output.json trong thư mục data/
- Tìm kiếm câu hỏi tương tự sử dụng thuật toán SequenceMatcher
- Cung cấp câu trả lời cho câu hỏi phổ biến mà không cần gọi mô hình LLM
- Tối ưu hóa thời gian phản hồi

### 6. Query Processing (`models/processors/query_processor.py`)
- Điều phối quá trình xử lý câu hỏi
- Kiểm tra cache trước khi xử lý
- Phát hiện small talk và xử lý riêng
- Gọi mô hình LLM khi cần thiết
- Lưu trữ kết quả vào cache

### 7. LLM Chain (`models/processors/llm_chain.py`)
- Khởi tạo và cấu hình mô hình Gemini
- Tạo chuỗi xử lý câu hỏi-trả lời
- Kết hợp kết quả tìm kiếm vector và tìm kiếm BM25
- Quản lý prompt template để tối ưu câu trả lời

### 8. Small Talk Handler (`models/processors/small_talk.py`)
- Nhận diện câu chào hỏi, tạm biệt, cảm ơn, xin lỗi, v.v.
- Lọc nội dung không phù hợp hoặc nhạy cảm
- Cung cấp câu trả lời phù hợp cho small talk
- Chuyển hướng người dùng về các câu hỏi liên quan đến tài liệu

### 9. API Interface (`app.py`)
- Cung cấp giao diện REST API
- Xử lý yêu cầu HTTP
- Định dạng kết quả trả về
- Quản lý các lỗi và exception

## Sử dụng

1. Khởi động server:
```bash
python app.py
```

2. Gửi yêu cầu đến API:
```bash
curl "http://localhost:5000/chat?text=Câu_hỏi_của_bạn_ở_đây"
```

## Định dạng phản hồi

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

## Cách tùy chỉnh và mở rộng

### Thêm tài liệu mới
1. Đặt file PDF mới vào thư mục `data/`
2. Chỉnh sửa biến `PDF_SOURCE` trong file `.env` hoặc trong `models/processors/query_processor.py`
3. Khởi động lại ứng dụng để xử lý tài liệu mới

### Thêm câu hỏi-trả lời định sẵn
1. Chỉnh sửa hoặc tạo file `output.json` trong thư mục `data/` với định dạng:
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

### Điều chỉnh mô hình Gemini
1. Thay đổi model name trong file `.env` (GEMINI_MODEL)
2. Điều chỉnh các tham số như TEMPERATURE, TOP_K, TOP_P để thay đổi đặc tính sinh văn bản

### Tối ưu hóa Vector Search
1. Điều chỉnh CHUNK_SIZE và CHUNK_OVERLAP trong file `.env` để thay đổi kích thước đoạn văn bản
2. Thay đổi VECTOR_SEARCH_K để tăng/giảm số lượng kết quả tìm kiếm
3. Điều chỉnh VECTOR_SEARCH_WEIGHT và KEYWORD_WEIGHT để cân bằng giữa tìm kiếm ngữ nghĩa và từ khóa

## Lưu ý quan trọng

1. **Chuẩn bị dữ liệu**:
   - Đặt file PDF vào thư mục `data/` (mặc định là `SoTaySinhVien2024.pdf`)
   - Tạo file JSON câu hỏi-trả lời trong thư mục `data/` (output.json)

2. **API Key**:
   - Bắt buộc phải có Google API Key cho Gemini trong file `.env`
   - Không chia sẻ API key công khai

3. **Thư mục lưu trữ**:
   - Thư mục `faiss_index/` sẽ được tạo tự động khi chạy lần đầu
   - Thư mục `output/` chứa cache (query_cache.json) và các tệp tạm thời

4. **Tùy chỉnh mô hình**:
   - Có thể thay đổi mô hình Gemini trong file `.env` (mặc định là gemini-1.5-flash)
   - Điều chỉnh các tham số như TEMPERATURE, TOP_K, TOP_P để thay đổi chất lượng câu trả lời

5. **Hiệu suất**:
   - Lần đầu tiên chạy sẽ tốn thời gian để tạo vector database
   - Các lần chạy sau sẽ nhanh hơn nhiều nhờ sử dụng cache
