import re
import logging
from datetime import datetime
from typing import Dict, List, Optional
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class ChatService:
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.conversation_patterns = self._init_conversation_patterns()
    
    def _init_conversation_patterns(self) -> Dict:
        """初始化对话模式"""
        return {
            'greetings': {
                'patterns': [r'hello', r'hi', r'hey', r'good morning', r'good afternoon', r'good evening'],
                'responses': [
                    "Hello! I'm your virtual diagnostic assistant. How are you feeling today?",
                    "Hi! I'm here to help with your health concerns. What symptoms are you experiencing?",
                    "Hello! I'm an AI medical assistant ready to help with your health consultation."
                ]
            },
            'name_inquiry': {
                'patterns': [r'what.*name', r'who are you', r'your name'],
                'responses': [
                    "I'm your Virtual Diagnostic Assistant, an AI medical consultation system. You can call me Doc AI.",
                    "I'm your AI health advisor, specialized in providing medical consultation services.",
                    "I'm Virtual Doctor AI, pleased to serve you!"
                ]
            },
            'how_are_you': {
                'patterns': [r'how are you', r'how do you feel', r'are you okay'],
                'responses': [
                    "I'm doing well, thank you for asking! More importantly, how is your health condition?",
                    "I'm in good condition and ready to provide medical consultation. How are you feeling today?",
                    "I'm fine! Let's focus on your health status."
                ]
            },
            'symptoms': {
                'patterns': [r'headache', r'fever', r'cough', r'stomach.*pain', r'fatigue', r'tired', r'insomnia', r'pain'],
                'responses': [
                    "I understand your symptoms. Can you describe the duration and severity of these symptoms in detail?",
                    "Thank you for the description. When did these symptoms start? Are there any accompanying symptoms?",
                    "I've noted your symptoms. Are there any other areas of discomfort?"
                ]
            },
            'farewell': {
                'patterns': [r'goodbye', r'bye', r'see you', r'take care'],
                'responses': [
                    "Goodbye! I hope you stay healthy. Please contact me anytime if you need help.",
                    "Take care! Remember to rest well and maintain a healthy lifestyle.",
                    "Goodbye! Wishing you a speedy recovery. Feel free to reach out if you have any questions!"
                ]
            }
        }
    
    def process_message(self, user_message: str, patient_id: str = 'default') -> str:
        """处理用户消息"""
        try:
            # 保存用户消息
            self.db_manager.insert_chat_message(patient_id, 'user', user_message)
            
            # 生成回复
            response = self._generate_response(user_message, patient_id)
            
            # 保存AI回复
            self.db_manager.insert_chat_message(patient_id, 'assistant', response)
            
            logger.info(f"Processed message - Patient: {patient_id}, Message: {user_message[:50]}...")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return "Sorry, I encountered a technical issue. Please try again later."
    
    def _generate_response(self, message: str, patient_id: str) -> str:
        """生成AI回复"""
        message_lower = message.lower()
        
        # 检查各种对话模式
        for category, pattern_data in self.conversation_patterns.items():
            for pattern in pattern_data['patterns']:
                if re.search(pattern, message_lower):
                    import random
                    response = random.choice(pattern_data['responses'])
                    
                    # 特殊处理症状相关消息
                    if category == 'symptoms':
                        self._extract_symptoms(message, patient_id)
                    
                    return response
        
        # 如果没有匹配的模式，返回通用回复
        return self._generate_general_response(message, patient_id)
    
    def _generate_general_response(self, message: str, patient_id: str) -> str:
        """生成通用回复"""
        general_responses = [
            "I understand your situation. Can you provide me with more details?",
            "Thank you for the information. Please continue to tell me about your symptoms or concerns.",
            "I'm recording your information. Is there anything else you need to tell me?",
            "I see. If you have any health-related questions, please feel free to let me know."
        ]
        
        import random
        return random.choice(general_responses)
    
    def _extract_symptoms(self, message: str, patient_id: str):
        """提取和记录症状信息"""
        # 简单的症状提取逻辑
        symptoms_keywords = {
            'headache': ['headache', 'head pain', 'migraine'],
            'fever': ['fever', 'high temperature', 'hot'],
            'cough': ['cough', 'coughing', 'dry cough'],
            'stomach pain': ['stomach pain', 'abdominal pain', 'belly ache'],
            'fatigue': ['fatigue', 'tired', 'exhausted'],
            'insomnia': ['insomnia', 'can\'t sleep', 'sleepless']
        }
        
        detected_symptoms = []
        for symptom, keywords in symptoms_keywords.items():
            for keyword in keywords:
                if keyword in message.lower():
                    detected_symptoms.append(symptom)
                    break
        
        if detected_symptoms:
            # 这里可以进一步处理症状信息，比如调用ML模型进行诊断
            logger.info(f"Detected symptoms: {detected_symptoms} - Patient: {patient_id}")
    
    def get_chat_history(self, patient_id: str, limit: int = 50) -> List[Dict]:
        """获取聊天历史"""
        try:
            history = self.db_manager.get_chat_history(patient_id, limit)
            return [
                {
                    'id': msg['id'],
                    'type': msg['message_type'],
                    'content': msg['content'],
                    'timestamp': msg['timestamp']
                }
                for msg in history
            ]
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}")
            return []
    
    def clear_chat_history(self, patient_id: str) -> bool:
        """清除聊天历史"""
        try:
            query = "DELETE FROM chat_messages WHERE patient_id = ?"
            self.db_manager.execute_update(query, (patient_id,))
            return True
        except Exception as e:
            logger.error(f"Error clearing chat history: {str(e)}")
            return False
    
    def get_conversation_summary(self, patient_id: str) -> Dict:
        """获取对话总结"""
        try:
            history = self.get_chat_history(patient_id)
            
            total_messages = len(history)
            user_messages = len([msg for msg in history if msg['type'] == 'user'])
            assistant_messages = len([msg for msg in history if msg['type'] == 'assistant'])
            
            # 获取最后一次对话时间
            last_message_time = None
            if history:
                last_message_time = history[-1]['timestamp']
            
            return {
                'total_messages': total_messages,
                'user_messages': user_messages,
                'assistant_messages': assistant_messages,
                'last_conversation': last_message_time,
                'patient_id': patient_id
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation summary: {str(e)}")
            return {} 