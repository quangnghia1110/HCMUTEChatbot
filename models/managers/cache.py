import os
import json
import hashlib
import time
from dotenv import load_dotenv

load_dotenv()

CACHE_MAX_AGE_DAYS = int(os.getenv("CACHE_MAX_AGE_DAYS")) 

class QueryCache:
    def __init__(self, cache_file="query_cache.json", cache_dir="output"):
        """Khởi tạo cache manager"""
        self.cache_file = os.path.join(cache_dir, cache_file)
        self.max_age_days = CACHE_MAX_AGE_DAYS
        self.cache = []  # Thay đổi từ dict sang list
        self._load_cache() 
    
    def _load_cache(self):
        """Tải và lọc cache hết hạn"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    current_time = time.time()
                    # Nếu data là dict (format cũ), chuyển sang list
                    if isinstance(data, dict):
                        data = [
                            {
                                "key": k,
                                "result": v["result"],
                                "timestamp": v["timestamp"],
                                "processing_time": v.get("processing_time", 0),
                                "query": v.get("query", "")  # Thêm query để dễ debug
                            }
                            for k, v in data.items()
                        ]
                    # Lọc các entry hết hạn
                    self.cache = [
                        entry for entry in data
                        if current_time - entry["timestamp"] < self.max_age_days * 86400
                    ]
        except Exception as e:
            print(f"Cache load error: {e}")
            self.cache = []
    
    def _save_cache(self):
        """Lưu cache với error handling"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Cache save error: {e}")
    
    def get(self, query):
        """Lấy kết quả từ cache"""
        key = hashlib.md5(query.lower().strip().encode()).hexdigest()
        current_time = time.time()
        
        # Tìm trong list
        for entry in self.cache:
            if entry["key"] == key:
                if current_time - entry["timestamp"] < self.max_age_days * 86400:
                    return entry["result"], True, entry.get("processing_time", 0)
                self.cache.remove(entry)
                break
                
        return None, False, 0
    
    def set(self, query, result, processing_time):
        """Lưu kết quả vào cache"""
        key = hashlib.md5(query.lower().strip().encode()).hexdigest()
        
        # Thêm entry mới vào đầu list
        self.cache.insert(0, {
            "key": key,
            "query": query,  # Lưu cả query để dễ debug
            "result": result,
            "timestamp": time.time(),
            "processing_time": processing_time
        })
        
        self._save_cache()
    
    # def clear(self):
    #     """Xóa toàn bộ cache"""
    #     self.cache = []
    #     if os.path.exists(self.cache_file):
    #         os.remove(self.cache_file)

query_cache = QueryCache() 