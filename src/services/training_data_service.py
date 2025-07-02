import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)

class TrainingDataService:
    """训练数据服务 - 处理Set-0文件夹下的患者数据读取和导出"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        # 训练数据路径
        self.training_data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            'training_data', 'Set-0'
        )
        logger.info(f"Training data path: {self.training_data_path}")
    
    def load_training_patients(self, limit: int = 20) -> List[Dict]:
        """加载训练数据患者列表"""
        try:
            if not os.path.exists(self.training_data_path):
                logger.warning(f"Training data path does not exist: {self.training_data_path}")
                return []
            
            patients = []
            patient_dirs = [d for d in os.listdir(self.training_data_path) 
                          if d.startswith('patient_') and os.path.isdir(os.path.join(self.training_data_path, d))]
            
            # 限制读取数量
            patient_dirs = patient_dirs[:limit]
            
            for patient_dir in patient_dirs:
                patient_id = patient_dir.replace('patient_', '')
                patient_data = self.load_patient_from_file(patient_id)
                
                if patient_data:
                    # 添加training前缀以区分训练数据
                    patient_data['id'] = f'training_{patient_id}'
                    patient_data['source'] = 'training_data'
                    patients.append(patient_data)
            
            logger.info(f"Loaded {len(patients)} training patients")
            return patients
            
        except Exception as e:
            logger.error(f"Error loading training patients: {str(e)}")
            return []
    
    def load_patient_from_file(self, patient_id: str) -> Optional[Dict]:
        """从文件加载单个患者数据"""
        try:
            # 构造文件路径
            patient_dir = f'patient_{patient_id}'
            patient_file = f'patient_{patient_id}_history.json'
            file_path = os.path.join(self.training_data_path, patient_dir, patient_file)
            
            if not os.path.exists(file_path):
                logger.warning(f"Patient file not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # 转换为统一格式
            formatted_data = self._format_training_patient_data(raw_data, patient_id)
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error loading patient {patient_id}: {str(e)}")
            return None
    
    def _format_training_patient_data(self, raw_data: Dict, patient_id: str) -> Dict:
        """格式化训练数据患者信息"""
        try:
            # 计算年龄（如果有出生日期）
            age = None
            if raw_data.get('birthdate'):
                try:
                    birth_year = int(raw_data['birthdate'].split('-')[0])
                    current_year = datetime.now().year
                    age = current_year - birth_year
                except:
                    pass
            
            # 转换性别格式
            gender_map = {'M': 'Male', 'F': 'Female'}
            raw_gender = raw_data.get('gender', 'Unknown')
            gender = gender_map.get(raw_gender, raw_gender) if raw_gender else 'Unknown'
            
            return {
                'id': patient_id,
                'name': raw_data.get('name', f'Patient {patient_id}'),
                'age': age,
                'gender': gender,
                'birthdate': raw_data.get('birthdate'),
                'blood_type': raw_data.get('blood_type'),
                'address': raw_data.get('address'),
                'weight': raw_data.get('weight'),
                'height': raw_data.get('height'),
                'notes': raw_data.get('notes'),
                'phone': None,  # 训练数据中没有电话
                'email': None,  # 训练数据中没有邮箱
                'medical_history': {
                    'basic_info': {
                        'blood_type': raw_data.get('blood_type'),
                        'weight': raw_data.get('weight'),
                        'height': raw_data.get('height')
                    },
                    'notes': raw_data.get('notes'),
                    'records': []
                },
                'original_format': raw_data,  # 保存原始数据
                'source_file': f'patient_{patient_id}_history.json',
                'is_training_data': True
            }
            
        except Exception as e:
            logger.error(f"Error formatting patient data: {str(e)}")
            return {}
    
    def export_training_patient(self, patient_id: str) -> Optional[Dict]:
        """导出训练数据患者（原格式）"""
        try:
            # 去掉training_前缀
            original_id = patient_id.replace('training_', '') if patient_id.startswith('training_') else patient_id
            
            patient_data = self.load_patient_from_file(original_id)
            if not patient_data:
                return None
            
            # 返回原始格式数据
            export_data = {
                'filename': f'patient_{original_id}_export.json',
                'data': patient_data.get('original_format', {}),
                'patient_info': patient_data,
                'export_timestamp': datetime.now().isoformat(),
                'source': 'training_data'
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting training patient: {str(e)}")
            return None
    
    def get_training_patients_summary(self) -> Dict:
        """获取训练数据患者统计信息"""
        try:
            if not os.path.exists(self.training_data_path):
                return {'error': 'Training data path not found'}
            
            # 统计患者数量
            patient_dirs = [d for d in os.listdir(self.training_data_path) 
                          if d.startswith('patient_') and os.path.isdir(os.path.join(self.training_data_path, d))]
            
            total_patients = len(patient_dirs)
            
            # 读取一些样本数据进行统计
            sample_size = min(50, total_patients)
            sample_patients = []
            
            for i, patient_dir in enumerate(patient_dirs[:sample_size]):
                patient_id = patient_dir.replace('patient_', '')
                patient_data = self.load_patient_from_file(patient_id)
                if patient_data:
                    sample_patients.append(patient_data)
            
            # 统计性别分布
            gender_stats = {}
            age_stats = {'known': 0, 'unknown': 0, 'average': 0.0}
            
            ages = []
            for patient in sample_patients:
                gender = patient.get('gender', 'Unknown')
                gender_stats[gender] = gender_stats.get(gender, 0) + 1
                
                if patient.get('age'):
                    ages.append(patient['age'])
                    age_stats['known'] += 1
                else:
                    age_stats['unknown'] += 1
            
            if ages:
                age_stats['average'] = sum(ages) / len(ages)
            
            return {
                'total_patients': total_patients,
                'sample_size': len(sample_patients),
                'gender_distribution': gender_stats,
                'age_statistics': age_stats,
                'data_path': self.training_data_path,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting training patients summary: {str(e)}")
            return {'error': str(e)}
    
    def import_training_patients_to_db(self, limit: int = 10) -> Dict:
        """将训练数据患者导入到数据库（可选功能）"""
        try:
            patients = self.load_training_patients(limit)
            imported_count = 0
            errors = []
            
            for patient in patients:
                try:
                    # 检查是否已存在
                    existing = self.db_manager.get_patient_by_id(patient['id'])
                    if existing:
                        continue
                    
                    # 导入到数据库
                    self.db_manager.insert_patient(patient)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Error importing {patient['id']}: {str(e)}")
            
            return {
                'imported_count': imported_count,
                'total_processed': len(patients),
                'errors': errors,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error importing training patients: {str(e)}")
            return {'error': str(e), 'status': 'failed'}
    
    def import_json_to_set0(self, file_content: str, original_filename: str) -> Dict:
        """将JSON数据导入到Set-0文件夹"""
        try:
            # 解析JSON数据
            data = json.loads(file_content)
            
            # 验证必要字段
            if not data.get('name'):
                raise ValueError('Missing required field: name')
            
            # 尝试从文件名提取患者ID
            import re
            import time
            
            patient_id = None
            filename_match = re.search(r'patient_(\d+)', original_filename)
            
            if filename_match:
                extracted_id = filename_match.group(1)
                # 检查是否已存在
                patient_dir = f'patient_{extracted_id}'
                patient_dir_path = os.path.join(self.training_data_path, patient_dir)
                
                if not os.path.exists(patient_dir_path):
                    patient_id = extracted_id
                    logger.info(f"Using ID from filename: {patient_id}")
                else:
                    logger.warning(f"Patient {extracted_id} already exists, generating new ID")
            
            # 如果无法从文件名提取ID或ID已存在，则生成新的时间戳ID
            if not patient_id:
                patient_id = str(int(time.time() * 1000))  # 毫秒时间戳
                logger.info(f"Generated new timestamp ID: {patient_id}")
            
            # 确保Set-0目录存在
            if not os.path.exists(self.training_data_path):
                os.makedirs(self.training_data_path, exist_ok=True)
            
            # 创建患者目录
            patient_dir = f'patient_{patient_id}'
            patient_dir_path = os.path.join(self.training_data_path, patient_dir)
            os.makedirs(patient_dir_path, exist_ok=True)
            
            # 创建JSON文件
            filename = f'patient_{patient_id}_history.json'
            file_path = os.path.join(patient_dir_path, filename)
            
            # 保存JSON数据
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            
            logger.info(f"Successfully imported JSON data to: {file_path}")
            
            return {
                'status': 'success',
                'patient_id': patient_id,
                'filename': filename,
                'file_path': file_path,
                'message': f'Data imported successfully as {filename}',
                'id_source': 'filename' if filename_match and patient_id == filename_match.group(1) else 'generated'
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {str(e)}")
            return {'error': f'Invalid JSON format: {str(e)}', 'status': 'failed'}
        
        except Exception as e:
            logger.error(f"Error importing JSON to Set-0: {str(e)}")
            return {'error': str(e), 'status': 'failed'}
    
    def validate_json_format(self, data: Dict) -> Dict:
        """验证JSON数据格式"""
        errors = []
        warnings = []
        
        # 必需字段检查
        required_fields = ['name']
        for field in required_fields:
            if not data.get(field):
                errors.append(f'Missing required field: {field}')
        
        # 推荐字段检查
        recommended_fields = ['birthdate', 'gender', 'blood_type', 'address', 'weight', 'height']
        for field in recommended_fields:
            if not data.get(field):
                warnings.append(f'Missing recommended field: {field}')
        
        # 数据类型检查
        if data.get('weight') and not isinstance(data['weight'], (int, float)):
            errors.append('Weight should be a number')
        
        if data.get('height') and not isinstance(data['height'], (int, float)):
            errors.append('Height should be a number')
        
        if data.get('gender') and data['gender'] not in ['M', 'F', 'Male', 'Female']:
            warnings.append('Gender should be M/F or Male/Female')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def rename_patient_folder(self, old_patient_id: str, new_patient_id: str) -> Dict:
        """重命名患者文件夹和文件"""
        try:
            old_dir = f'patient_{old_patient_id}'
            new_dir = f'patient_{new_patient_id}'
            old_dir_path = os.path.join(self.training_data_path, old_dir)
            new_dir_path = os.path.join(self.training_data_path, new_dir)
            
            # 检查源文件夹是否存在
            if not os.path.exists(old_dir_path):
                return {'error': f'Source patient folder not found: {old_dir}', 'status': 'failed'}
            
            # 检查目标文件夹是否已存在
            if os.path.exists(new_dir_path):
                return {'error': f'Target patient folder already exists: {new_dir}', 'status': 'failed'}
            
            # 重命名文件夹
            os.rename(old_dir_path, new_dir_path)
            
            # 重命名文件夹内的JSON文件
            old_filename = f'patient_{old_patient_id}_history.json'
            new_filename = f'patient_{new_patient_id}_history.json'
            old_file_path = os.path.join(new_dir_path, old_filename)
            new_file_path = os.path.join(new_dir_path, new_filename)
            
            if os.path.exists(old_file_path):
                os.rename(old_file_path, new_file_path)
                logger.info(f"Renamed patient folder from {old_dir} to {new_dir}")
                
                return {
                    'status': 'success',
                    'old_id': old_patient_id,
                    'new_id': new_patient_id,
                    'old_folder': old_dir,
                    'new_folder': new_dir,
                    'message': f'Successfully renamed patient {old_patient_id} to {new_patient_id}'
                }
            else:
                # 如果没有找到JSON文件，回滚文件夹重命名
                os.rename(new_dir_path, old_dir_path)
                return {'error': f'JSON file not found in patient folder: {old_filename}', 'status': 'failed'}
            
        except Exception as e:
            logger.error(f"Error renaming patient folder: {str(e)}")
            return {'error': str(e), 'status': 'failed'} 