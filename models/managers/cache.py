import hashlib
import time

class QueryCache:
    def __init__(self):
        """Khởi tạo cache manager chỉ lưu trong RAM"""
        self.cache = []  # Lưu cache trong list
    
    def get(self, query):
        """Lấy kết quả từ cache"""
        key = hashlib.md5(query.lower().strip().encode()).hexdigest()
        
        # Tìm trong list
        for entry in self.cache:
            if entry["key"] == key:
                return entry["result"], True, entry.get("processing_time", 0)
                
        return None, False, 0
    
    def set(self, query, result, processing_time):
        """Lưu kết quả vào cache RAM"""
        key = hashlib.md5(query.lower().strip().encode()).hexdigest()
        
        # Thêm entry mới vào đầu list
        self.cache.insert(0, {
            "key": key,
            "query": query,  # Lưu cả query để dễ debug
            "result": result,
            "timestamp": time.time(),
            "processing_time": processing_time
        })

query_cache = QueryCache() 