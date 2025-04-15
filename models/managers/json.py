import os
import json
from difflib import SequenceMatcher

class JsonQAHandler:
    def __init__(self, json_file="output.json", json_dir="data"):
        self.json_file = os.path.join(json_dir, json_file)
        self.qa_pairs = []
        self.cache = {}  
        self.load_data()
    
    def load_data(self):
        self.qa_pairs = []
        try:
            if os.path.exists(self.json_file):
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for idx, item in enumerate(data, 1):
                            if "question" in item and "answer" in item:
                                self.qa_pairs.append({
                                    "question": item["question"].lower(),
                                    "answer": item["answer"],
                                    "source": self.json_file,
                                    "line_number": idx
                                })
                    else:
                        for idx, (q, a) in enumerate(data.items(), 1):
                            self.qa_pairs.append({
                                "question": q.lower(),
                                "answer": a,
                                "source": self.json_file,
                                "line_number": idx
                            })
        except Exception as e:
            print(f"Lỗi file {self.json_file}: {e}")
                
    def similarity_ratio(self, a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def find_best_match(self, question, threshold=0.55):
        if not self.qa_pairs:
            print("WARNING: No QA pairs loaded")
            return None
        question_key = question.lower()
        keywords = set(question_key.split())
        best_match = None
        best_score = 0
        for qa in self.qa_pairs:
            seq_score = SequenceMatcher(None, question_key, qa["question"]).ratio()
            kw_score = len(keywords.intersection(qa["question"].split())) / len(keywords) if keywords else 0
            score = seq_score * 0.6 + kw_score * 0.4
            if score > best_score:
                best_score = score
                best_match = qa
        if best_match and best_score >= threshold:
            return {
                "answer": best_match["answer"],
                "source": best_match["source"],
                "line_number": best_match["line_number"]
            }
        return None