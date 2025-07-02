import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器 - 处理SQLite数据库的所有操作"""
    
    def __init__(self, db_path: str = 'virtual_diagnostician.db'):
        import os
        # 确保数据库存储在data目录中
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # 如果只传入了文件名，则存储在data目录中
        if not os.path.dirname(db_path):
            self.db_path = os.path.join(data_dir, db_path)
        else:
            self.db_path = db_path
            
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 返回字典格式的结果
        return conn
    
    def init_database(self):
        """初始化数据库表结构"""
        with self.get_connection() as conn:
            # 患者信息表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER,
                    gender TEXT,
                    phone TEXT,
                    email TEXT,
                    medical_history TEXT,  -- JSON格式存储病史
                    -- 训练数据专用字段
                    birthdate TEXT,
                    blood_type TEXT,
                    address TEXT,
                    weight REAL,
                    height REAL,
                    notes TEXT,
                    is_training_data BOOLEAN DEFAULT FALSE,
                    original_format TEXT,  -- JSON格式存储原始数据
                    source_file TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 聊天记录表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT NOT NULL,
                    message_type TEXT NOT NULL,  -- 'user' 或 'assistant'
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')
            
            # 诊断记录表
            conn.execute('''
                CREATE TABLE IF NOT EXISTS diagnosis_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id TEXT NOT NULL,
                    symptoms TEXT,  -- JSON格式存储症状
                    diagnosis TEXT,
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')
            
            conn.commit()
            logger.info("Database initialization completed")
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """执行查询语句"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """执行插入语句，返回插入的ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid or 0
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """执行更新语句，返回受影响的行数"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount
    
    # 患者相关操作
    def insert_patient(self, patient_data: Dict) -> str:
        """插入新患者"""
        query = '''
            INSERT INTO patients (id, name, age, gender, phone, email, medical_history,
                                birthdate, blood_type, address, weight, height, notes,
                                is_training_data, original_format, source_file)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (
            patient_data.get('id'),
            patient_data.get('name'),
            patient_data.get('age'),
            patient_data.get('gender'),
            patient_data.get('phone'),
            patient_data.get('email'),
            json.dumps(patient_data.get('medical_history', {}), ensure_ascii=False),
            patient_data.get('birthdate'),
            patient_data.get('blood_type'),
            patient_data.get('address'),
            patient_data.get('weight'),
            patient_data.get('height'),
            patient_data.get('notes'),
            patient_data.get('is_training_data', False),
            json.dumps(patient_data.get('original_format', {}), ensure_ascii=False) if patient_data.get('original_format') else None,
            patient_data.get('source_file')
        )
        
        self.execute_insert(query, params)
        return str(patient_data.get('id'))
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Dict]:
        """根据ID获取患者信息"""
        query = "SELECT * FROM patients WHERE id = ?"
        results = self.execute_query(query, (patient_id,))
        
        if results:
            patient = results[0]
            # 解析JSON格式的病史
            if patient['medical_history']:
                patient['medical_history'] = json.loads(patient['medical_history'])
            # 解析JSON格式的原始数据
            if patient.get('original_format'):
                patient['original_format'] = json.loads(patient['original_format'])
            return patient
        return None
    
    def update_patient(self, patient_id: str, patient_data: Dict) -> bool:
        """更新患者信息"""
        query = '''
            UPDATE patients 
            SET name = ?, age = ?, gender = ?, phone = ?, email = ?, 
                medical_history = ?, birthdate = ?, blood_type = ?, address = ?,
                weight = ?, height = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        params = (
            patient_data.get('name'),
            patient_data.get('age'),
            patient_data.get('gender'),
            patient_data.get('phone'),
            patient_data.get('email'),
            json.dumps(patient_data.get('medical_history', {}), ensure_ascii=False),
            patient_data.get('birthdate'),
            patient_data.get('blood_type'),
            patient_data.get('address'),
            patient_data.get('weight'),
            patient_data.get('height'),
            patient_data.get('notes'),
            patient_id
        )
        
        rows_affected = self.execute_update(query, params)
        return rows_affected > 0
    
    # 聊天记录相关操作
    def insert_chat_message(self, patient_id: str, message_type: str, content: str) -> int:
        """插入聊天消息"""
        query = '''
            INSERT INTO chat_messages (patient_id, message_type, content)
            VALUES (?, ?, ?)
        '''
        return self.execute_insert(query, (patient_id, message_type, content))
    
    def get_chat_history(self, patient_id: str, limit: int = 100) -> List[Dict]:
        """获取聊天历史"""
        query = '''
            SELECT * FROM chat_messages 
            WHERE patient_id = ? 
            ORDER BY timestamp ASC 
            LIMIT ?
        '''
        return self.execute_query(query, (patient_id, limit))
    
    # 诊断记录相关操作
    def insert_diagnosis(self, patient_id: str, symptoms: Dict, diagnosis: str, confidence: float) -> int:
        """插入诊断记录"""
        query = '''
            INSERT INTO diagnosis_records (patient_id, symptoms, diagnosis, confidence)
            VALUES (?, ?, ?, ?)
        '''
        return self.execute_insert(query, (
            patient_id,
            json.dumps(symptoms, ensure_ascii=False),
            diagnosis,
            confidence
        ))
    
    def get_patient_diagnoses(self, patient_id: str) -> List[Dict]:
        """获取患者的诊断记录"""
        query = '''
            SELECT * FROM diagnosis_records 
            WHERE patient_id = ? 
            ORDER BY created_at DESC
        '''
        results = self.execute_query(query, (patient_id,))
        
        # 解析JSON格式的症状
        for record in results:
            if record['symptoms']:
                record['symptoms'] = json.loads(record['symptoms'])
        
        return results 