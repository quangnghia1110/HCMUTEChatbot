import hashlib
import time

class QueryCache:
    def __init__(self):
        self.cache = []
    
    def get(self, query):
        key = hashlib.md5(query.lower().strip().encode()).hexdigest()
        for entry in self.cache:
            if entry["key"] == key:
                return entry["result"], True, entry.get("processing_time", 0)
        return None, False, 0
    
    def set(self, query, result, processing_time):
        key = hashlib.md5(query.lower().strip().encode()).hexdigest()
        self.cache.insert(0, {
            "key": key,
            "query": query,
            "result": result,
            "timestamp": time.time(),
            "processing_time": processing_time
        })

query_cache = QueryCache()