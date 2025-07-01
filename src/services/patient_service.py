import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class PatientService:
    """患者服务 - 处理患者档案管理和病史记录"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_patient(self, patient_data: Dict) -> str:
        """创建新患者"""
        try:
            # 生成唯一的患者ID
            patient_id = patient_data.get('id') or str(uuid.uuid4())
            
            # 验证必要字段
            if not patient_data.get('name'):
                raise ValueError("Patient name cannot be empty")
            
            # 准备患者数据
            patient_info = {
                'id': patient_id,
                'name': patient_data.get('name'),
                'age': patient_data.get('age'),
                'gender': patient_data.get('gender'),
                'phone': patient_data.get('phone'),
                'email': patient_data.get('email'),
                'medical_history': patient_data.get('medical_history', {})
            }
            
            # 插入数据库
            self.db_manager.insert_patient(patient_info)
            
            logger.info(f"Created new patient: {patient_id} - {patient_data.get('name')}")
            return patient_id
            
        except Exception as e:
            logger.error(f"Error creating patient: {str(e)}")
            raise
    
    def get_patient_by_id(self, patient_id: str) -> Optional[Dict]:
        """根据ID获取患者信息"""
        try:
            patient = self.db_manager.get_patient_by_id(patient_id)
            if patient:
                # 获取患者的诊断历史
                diagnoses = self.db_manager.get_patient_diagnoses(patient_id)
                patient['diagnoses'] = diagnoses
                
                # 格式化返回数据
                return self._format_patient_data(patient)
            return None
            
        except Exception as e:
            logger.error(f"Error getting patient information: {str(e)}")
            return None
    
    def update_patient(self, patient_id: str, patient_data: Dict) -> bool:
        """更新患者信息"""
        try:
            success = self.db_manager.update_patient(patient_id, patient_data)
            if success:
                logger.info(f"Updated patient information: {patient_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error updating patient information: {str(e)}")
            return False
    
    def add_medical_history(self, patient_id: str, medical_record: Dict) -> bool:
        """添加病史记录"""
        try:
            # 获取当前患者信息
            patient = self.db_manager.get_patient_by_id(patient_id)
            if not patient:
                raise ValueError("Patient does not exist")
            
            # 获取现有病史
            medical_history = patient.get('medical_history', {})
            if isinstance(medical_history, str):
                import json
                medical_history = json.loads(medical_history)
            
            # 添加新的病史记录
            if 'records' not in medical_history:
                medical_history['records'] = []
            
            medical_record['timestamp'] = datetime.now().isoformat()
            medical_record['id'] = str(uuid.uuid4())
            medical_history['records'].append(medical_record)
            
            # 更新患者信息
            updated_data = {'medical_history': medical_history}
            success = self.db_manager.update_patient(patient_id, updated_data)
            
            if success:
                logger.info(f"Added medical history record: {patient_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error adding medical history record: {str(e)}")
            return False
    
    def get_patient_medical_history(self, patient_id: str) -> List[Dict]:
        """获取患者病史"""
        try:
            patient = self.db_manager.get_patient_by_id(patient_id)
            if not patient:
                return []
            
            medical_history = patient.get('medical_history', {})
            if isinstance(medical_history, str):
                import json
                medical_history = json.loads(medical_history)
            
            return medical_history.get('records', [])
            
        except Exception as e:
            logger.error(f"Error getting patient medical history: {str(e)}")
            return []
    
    def search_patients(self, query: str = '', filters: Optional[Dict] = None) -> List[Dict]:
        """搜索患者"""
        try:
            if filters is None:
                filters = {}
            
            # 构建查询语句
            base_query = "SELECT * FROM patients WHERE 1=1"
            params = []
            
            # 按姓名搜索
            if query:
                base_query += " AND name LIKE ?"
                params.append(f"%{query}%")
            
            # 按年龄过滤
            if filters.get('min_age'):
                base_query += " AND age >= ?"
                params.append(filters['min_age'])
            
            if filters.get('max_age'):
                base_query += " AND age <= ?"
                params.append(filters['max_age'])
            
            # 按性别过滤
            if filters.get('gender'):
                base_query += " AND gender = ?"
                params.append(filters['gender'])
            
            base_query += " ORDER BY created_at DESC LIMIT 100"
            
            patients = self.db_manager.execute_query(base_query, tuple(params))
            
            # 格式化返回数据
            return [self._format_patient_data(patient) for patient in patients]
            
        except Exception as e:
            logger.error(f"Error searching patients: {str(e)}")
            return []
    
    def _format_patient_data(self, patient_data: Dict) -> Dict:
        """格式化患者数据"""
        try:
            # 解析医疗历史JSON
            medical_history = patient_data.get('medical_history')
            if isinstance(medical_history, str):
                import json
                medical_history = json.loads(medical_history)
            
            return {
                'id': patient_data.get('id'),
                'name': patient_data.get('name'),
                'age': patient_data.get('age'),
                'gender': patient_data.get('gender'),
                'phone': patient_data.get('phone'),
                'email': patient_data.get('email'),
                'medical_history': medical_history or {},
                'diagnoses': patient_data.get('diagnoses', []),
                'created_at': patient_data.get('created_at'),
                'updated_at': patient_data.get('updated_at')
            }
            
        except Exception as e:
            logger.error(f"Error formatting patient data: {str(e)}")
            return patient_data
    
    def get_patients_summary(self) -> Dict:
        """获取患者统计摘要"""
        try:
            # 获取总患者数
            total_query = "SELECT COUNT(*) as total FROM patients"
            total_result = self.db_manager.execute_query(total_query)
            total_patients = total_result[0]['total'] if total_result else 0
            
            # 按性别统计
            gender_query = """
                SELECT gender, COUNT(*) as count 
                FROM patients 
                WHERE gender IS NOT NULL 
                GROUP BY gender
            """
            gender_stats = self.db_manager.execute_query(gender_query)
            
            # 按年龄段统计
            age_query = """
                SELECT 
                    CASE 
                        WHEN age < 18 THEN 'Child'
                        WHEN age BETWEEN 18 AND 35 THEN 'Young Adult'
                        WHEN age BETWEEN 36 AND 60 THEN 'Middle-aged'
                        WHEN age > 60 THEN 'Senior'
                        ELSE 'Unknown'
                    END as age_group,
                    COUNT(*) as count
                FROM patients
                WHERE age IS NOT NULL
                GROUP BY age_group
            """
            age_stats = self.db_manager.execute_query(age_query)
            
            return {
                'total_patients': total_patients,
                'gender_distribution': {stat['gender']: stat['count'] for stat in gender_stats},
                'age_distribution': {stat['age_group']: stat['count'] for stat in age_stats},
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting patient statistics: {str(e)}")
            return {}
    
    def create_sample_patients(self):
        """创建示例患者数据（用于测试）"""
        sample_patients = [
            {
                'name': 'John Smith',
                'age': 35,
                'gender': 'Male',
                'phone': '13800138001',
                'email': 'john.smith@example.com',
                'medical_history': {
                    'allergies': ['Penicillin'],
                    'chronic_conditions': [],
                    'records': [
                        {
                            'date': '2024-01-15',
                            'condition': 'Common Cold',
                            'symptoms': ['fever', 'cough'],
                            'treatment': 'Rest and plenty of fluids'
                        }
                    ]
                }
            },
            {
                'name': 'Jane Doe',
                'age': 28,
                'gender': 'Female',
                'phone': '13800138002',
                'email': 'jane.doe@example.com',
                'medical_history': {
                    'allergies': [],
                    'chronic_conditions': ['Migraine'],
                    'records': [
                        {
                            'date': '2024-01-10',
                            'condition': 'Migraine Attack',
                            'symptoms': ['headache', 'nausea'],
                            'treatment': 'Pain medication, avoid bright lights'
                        }
                    ]
                }
            }
        ]
        
        created_count = 0
        for patient_data in sample_patients:
            try:
                # Check if patient with this name already exists
                existing_patients = self.db_manager.execute_query(
                    "SELECT id FROM patients WHERE name = ?", 
                    (patient_data['name'],)
                )
                
                if existing_patients:
                    logger.info(f"Sample patient already exists: {patient_data['name']}")
                    continue
                
                # Create patient if doesn't exist
                self.create_patient(patient_data)
                created_count += 1
                logger.info(f"Created sample patient: {patient_data['name']}")
                
            except Exception as e:
                logger.error(f"Failed to create sample patient: {str(e)}")
        
        if created_count > 0:
            logger.info(f"Created {created_count} new sample patients")
        else:
            logger.info("All sample patients already exist, no new patients created") 