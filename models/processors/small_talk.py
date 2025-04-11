def is_small_talk(question):
    question_lower = question.lower().strip()
    words = question_lower.split()
    greetings = [
        "xin chào", "chào", "hello", "hi", "hey", "hola", "bonjour", "ciao", "hallo", 
        "good morning", "good afternoon", "good evening", "good day", "chào buổi sáng",
        "chào buổi chiều", "chào buổi tối", "chào ngày mới", "chào bạn", "kính chào",
        "chào mừng", "hế lô", "híu", "hê lô", "alo", "alô", "chào ad", "chào admin"
    ]
    goodbyes = [
        "tạm biệt", "bye", "goodbye", "see you", "see ya", "farewell", "adios", "au revoir",
        "ciao", "auf wiedersehen", "hẹn gặp lại", "chào tạm biệt", "gặp lại sau", "bái bai",
        "bái", "bai", "bai bai", "tạm biệt nhé", "tạm biệt bạn", "tạm biệt admin", "tạm biệt ad"
    ]
    health_questions = [
        "khỏe không", "khỏe chứ", "khỏe hông", "có khỏe", "khoẻ không", "thế nào", "ra sao",
        "how are you", "how do you do", "how are you doing", "how have you been", "what's up", 
        "wassup", "how's it going", "how's life", "how are things", "how are you feeling",
        "dạo này", "dạo này thế nào", "dạo này sao", "dạo này ra sao", "dạo này có khỏe",
        "dạo này có khoẻ", "dạo này khỏe không", "dạo này khỏe chứ", "dạo này khỏe hông",
        "dạo này có ổn", "bạn có khỏe", "bạn có ổn", "khỏe không bạn", "ổn không bạn"
    ]
    weather = [
        "thời tiết", "nhiệt độ", "mưa", "nắng", "giông", "bão", "gió", "climate", "weather",
        "temperature", "rain", "sunny", "stormy", "windy", "nóng", "lạnh", "ấm", "mát",
        "oi", "oi bức", "nồm", "ngột ngạt", "weather", "nhiệt độ bao nhiêu", "mấy độ",
        "bao nhiêu độ", "thời tiết thế nào", "thời tiết ra sao", "thời tiết dạo này",
        "dự báo thời tiết", "thời tiết hôm nay", "thời tiết ngày mai", "thời tiết tuần này"
    ]
    out_of_scope = [
        "viết code", "lập trình", "code giúp", "viết giúp", "viết cho", "thiết kế", "phát triển",
        "xây dựng", "tạo ra", "code", "script", "algorithm", "thuật toán", "function", "app",
        "ứng dụng", "phần mềm", "software", "hệ thống", "system", "tự động", "automated",
        "quản lý", "manage", "phân tích", "analytics", "máy học", "machine learning", "AI",
        "artificial intelligence", "trí tuệ nhân tạo", "database", "cơ sở dữ liệu", "SQL", 
        "NoSQL", "MongoDB", "MySQL", "PostgreSQL", "DevOps", "cloud", "đám mây", "AWS",
        "Azure", "Google Cloud", "server", "máy chủ", "frontend", "backend", "fullstack",
        "web", "website", "mobile", "iOS", "Android", "giúp mình", "hack", "crack", "jailbreak"
    ]
    thanks = [
        "cảm ơn", "thanks", "thank you", "thank", "gracias", "merci", "grazie", "danke",
        "appreciate", "grateful", "cám ơn", "thank u", "nice", "hay", "tuyệt", "chuẩn",
        "chính xác", "đúng vậy", "đúng rồi", "tốt", "tuyệt vời", "xuất sắc", "giỏi quá",
        "giỏi thật", "giỏi ghê", "tài thật", "tài quá", "đỉnh", "pro"
    ]
    apologies = [
        "xin lỗi", "sorry", "my bad", "my fault", "I apologize", "excuse me", "pardon",
        "forgive me", "lo siento", "desculpe", "scusa", "entschuldigung", "mình xin lỗi",
        "mình sai", "tôi sai", "tôi xin lỗi", "lỗi của tôi", "lỗi của mình", "lỗi tại mình",
        "mình có lỗi", "tôi có lỗi", "lỗi nhé", "nhầm", "mình nhầm", "tôi nhầm"
    ]
    opinion_questions = [
        "nghĩ gì", "thích gì", "quan điểm", "ý kiến", "nhận xét", "đánh giá", "nhận định",
        "cho rằng", "đồng ý", "không đồng ý", "bất đồng", "thế nào về", "sao về", "thấy sao",
        "thấy thế nào", "ra sao", "nói gì", "bình luận gì", "comment", "review", "đánh giá",
        "nghĩ về", "thích nhất", "ghét nhất", "tư tưởng", "lập trường", "mong muốn", "ước mơ",
        "ước gì", "mơ ước", "mong ước", "khao khát", "ao ước", "nguyện vọng"
    ]
    echo_statements = [
        "ok", "oke", "okay", "yes", "no", "không", "có", "ừ", "uh", "uhm", "à", "ạ", 
        "vâng", "dạ", "rồi", "oh", "được", "tốt", "hiểu", "hiểu rồi", "rõ", "đã rõ",
        "okie", "ok nha", "um", "hmm", "hm", "ha", "hả", "vậy", "thế", "thế à", "thế hả",
        "à há", "a ha", "ồ", "ừa", "ừm", "yeah", "yep", "nope", "vậy thôi", "thế thôi",
        "được rồi", "xong", "tiếp", "tiếp tục", "next", "đúng", "sai"
    ]
    capability_questions = [
        "làm được gì", "có thể làm", "biết làm", "khả năng", "giúp được", "giúp tôi",
        "what can you do", "biết những gì", "có những chức năng gì", "chức năng", "tính năng",
        "có thể giúp", "hỗ trợ", "năng lực", "kỹ năng", "biết gì", "thông minh không",
        "thông minh thế nào", "hiểu được gì", "ngu hay thông minh", "có tốt không", "có hay không"
    ]
    political_topics = [
        "chính trị", "đảng", "chính phủ", "bầu cử", "chính sách", "quốc hội",
        "thủ tướng", "chủ tịch nước", "tổng bí thư", "tổng thống", "nghị sĩ", "bộ trưởng",
        "dân chủ", "độc tài", "cộng hòa", "xã hội chủ nghĩa", "tư bản", "cách mạng", 
        "biểu tình", "chống đối", "phản động", "đối lập", "quyền lực", "quyền tự do",
        "tuyên truyền", "tham nhũng", "chính quyền", "hiến pháp", "luật pháp", 
        "chiến tranh", "khủng bố", "quân sự", "quân đội", "vũ khí", "thế lực",
        "thế giới", "quốc tế", "liên hiệp quốc", "trump", "biden", "putin", "tập cận bình",
        "kim jong un", "zelenskyy", "ukraine", "nga", "mỹ", "trung quốc", "nato"
    ]
    offensive_words = [
        "đmm", "đụ", "địt", "lồn", "buồi", "cặc", "chim", "cu", "dái", "đéo", "cứt", "ỉa", "đái",
        "đít", "đĩ", "cave", "gái ngành", "gái bán hoa", "bitch", "cưnt", "mẹ mày", "con mẹ", 
        "ngu", "đần", "óc chó", "ngu như bò", "ngu như chó", "thằng điên", "khùng", 
        "dở hơi", "thần kinh", "đầu óc", "mất dạy", "vô học", "chửi bới", "mất nết", 
        "láo", "láo toét", "bịa đặt", "xúc phạm", "nhục", "khinh", "khinh miệt", 
        "hãm", "đểu", "kẹt", "lol", "wtf", "fuck", "shit", "asshole", "dick", "pussy",
        "bastard", "baka", "aho", "kuso", "chết", "giết", "đâm", "chém", "đánh", "hành hạ",
        "tra tấn", "bạo lực", "tự tử", "tự sát"
    ]
    sensitive_topics = [
        "tôn giáo", "phật giáo", "thiên chúa giáo", "công giáo", "hồi giáo", "islam", "hindu",
        "tin lành", "cao đài", "phật", "chúa", "allah", "muhammad", "jesus", "god", "thánh",
        "tín ngưỡng", "mê tín", "đồng bóng", "bùa ngải", "ma quỷ", "thần thánh", "thờ cúng",
        "cờ bạc", "cá độ", "số đề", "xổ số", "đánh bài", "casino", "poker", "blackjack",
        "roulette", "slot machine", "bài bạc", "đỏ đen", "trò chơi may rủi", "gambling",
        "ma túy", "heroin", "cocaine", "cần sa", "marijuana", "weed", "pot", "crack", 
        "thuốc lắc", "ecstasy", "tẩu tán", "buôn bán", "buôn lậu", "tiêm chích", "hút chích",
        "mại dâm", "bán dâm", "gái gọi", "sex", "tình dục", "quan hệ", "khiêu dâm", "porn", 
        "phim người lớn", "phim sex", "phim cấp 3", "khỏa thân", "nude", "ảnh nóng", "clip nóng",
        "hình nhạy cảm", "sexy", "sextoy", "gái xinh", "trai đẹp", "cởi trần", "cởi đồ"
    ]
    for word in greetings:
        if word in question_lower and len(words) < 5:
            return "Xin chào! Bạn có câu hỏi gì cho tôi không? Tôi có thể giúp bạn trả lời các thông tin đó."
    for word in goodbyes:
        if word in question_lower and len(words) < 5:
            return "Tạm biệt! Rất vui được hỗ trợ bạn. Hẹn gặp lại!"
    for word in health_questions:
        if word in question_lower and len(words) < 5:
            return "Tôi là trợ lý AI nên không có khái niệm về sức khỏe, nhưng tôi luôn sẵn sàng hỗ trợ bạn tìm kiếm thông tin trong tài liệu. Bạn cần tìm hiểu về vấn đề gì trong tài liệu?"
    for word in weather:
        if word in question_lower and len(words) < 10:
            return "Tôi không có khả năng theo dõi thời tiết hoặc dữ liệu thời gian thực. Tôi chỉ có thể trả lời câu hỏi dựa trên thông tin trong tài liệu đã được tải lên. Bạn muốn tìm hiểu điều gì từ tài liệu?"
    for word in out_of_scope:
        if word in question_lower and len(words) < 15:
            return "Xin lỗi, tôi được thiết kế để trả lời câu hỏi dựa trên nội dung tài liệu đã tải lên. Tôi không thể thực hiện yêu cầu này. Bạn có thể hỏi tôi về thông tin trong tài liệu không?"
    for word in thanks:
        if word in question_lower and len(words) < 5:
            return "Rất vui khi được giúp đỡ bạn! Bạn còn câu hỏi nào về nội dung tài liệu không?"
    for word in apologies:
        if word in question_lower and len(words) < 5:
            return "Không sao cả! Tôi có thể giúp gì cho bạn về thông tin trong tài liệu không?"
    for word in echo_statements:
        if question_lower == word:
            return "Tôi đang ở đây và sẵn sàng trả lời câu hỏi của bạn về nội dung tài liệu. Bạn muốn biết điều gì?"
    for word in opinion_questions:
        if word in question_lower and len(words) < 10:
            return "Tôi là một trợ lý AI và không có ý kiến cá nhân. Tôi chỉ có thể cung cấp thông tin dựa trên nội dung tài liệu đã được tải lên. Bạn có câu hỏi cụ thể về tài liệu không?"
    for word in capability_questions:
        if word in question_lower and len(words) < 10:
            return "Tôi có thể đọc và phân tích nội dung tài liệu PDF, sau đó trả lời các câu hỏi của bạn dựa trên thông tin tìm thấy. Tôi có thể trích dẫn nguồn, tìm kiếm từ khóa, và tóm tắt thông tin từ tài liệu. Bạn muốn hỏi điều gì về nội dung tài liệu?"
    for word in political_topics:
        if word in question_lower:
            return "Tôi là trợ lý AI được thiết kế để hỗ trợ học tập và cung cấp thông tin từ tài liệu. Tôi không thảo luận về các vấn đề chính trị, nhà nước hoặc các chủ đề nhạy cảm. Hãy hỏi tôi về các thông tin khác hoặc các vấn đề học tập."
    for word in offensive_words:
        if word in question_lower:
            return "Tôi là trợ lý AI được thiết kế để hỗ trợ với các câu hỏi mang tính xây dựng và tích cực. Vui lòng sử dụng ngôn ngữ lịch sự và tôn trọng. Tôi có thể giúp bạn với các câu hỏi khác không?"
    for word in sensitive_topics:
        if word in question_lower:
            return "Tôi là trợ lý AI được thiết kế để cung cấp thông tin học thuật và hỗ trợ học tập. Tôi không thảo luận về các chủ đề nhạy cảm này. Hãy hỏi tôi các câu hỏi khác về học tập hoặc thông tin trong tài liệu."
    if len(words) < 3:
        return "Xin chào! Vui lòng đặt câu hỏi cụ thể liên quan đến nội dung của tài liệu để tôi có thể giúp bạn tốt hơn."
    return None 