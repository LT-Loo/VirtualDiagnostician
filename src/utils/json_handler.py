import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class JSONHandler:
    """JSON处理工具 - 处理数据的导入导出"""
    
    def __init__(self, export_dir: str = 'exports'):
        import os
        # 确保导出文件存储在项目根目录的exports文件夹中
        if not os.path.isabs(export_dir):
            project_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..')
            self.export_dir = os.path.join(project_root, export_dir)
        else:
            self.export_dir = export_dir
        self._ensure_export_dir()
    
    def _ensure_export_dir(self):
        """确保导出目录存在"""
        if not os.path.exists(self.export_dir):
            os.makedirs(self.export_dir)
            logger.info(f"创建导出目录: {self.export_dir}")
    
    def save_patient_data(self, patient_id: str, data: Dict) -> str:
        """保存患者数据到JSON文件"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"patient_{patient_id}_{timestamp}.json"
            filepath = os.path.join(self.export_dir, filename)
            
            # 格式化数据以便阅读
            formatted_data = self._format_export_data(data)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(formatted_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"患者数据已保存: {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"保存患者数据错误: {str(e)}")
            raise
    
    def load_patient_data(self, filename: str) -> Optional[Dict]:
        """从JSON文件加载患者数据"""
        try:
            filepath = os.path.join(self.export_dir, filename)
            
            if not os.path.exists(filepath):
                logger.error(f"文件不存在: {filepath}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"患者数据已加载: {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"加载患者数据错误: {str(e)}")
            return None
    
    def save_chat_history(self, patient_id: str, chat_history: List[Dict]) -> str:
        """保存聊天历史到JSON文件"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_history_{patient_id}_{timestamp}.json"
            filepath = os.path.join(self.export_dir, filename)
            
            export_data = {
                'patient_id': patient_id,
                'export_timestamp': datetime.now().isoformat(),
                'total_messages': len(chat_history),
                'chat_history': chat_history
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"聊天历史已保存: {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"保存聊天历史错误: {str(e)}")
            raise
    
    def save_diagnosis_report(self, patient_id: str, diagnosis_data: Dict) -> str:
        """保存诊断报告到JSON文件"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"diagnosis_report_{patient_id}_{timestamp}.json"
            filepath = os.path.join(self.export_dir, filename)
            
            report_data = {
                'patient_id': patient_id,
                'report_timestamp': datetime.now().isoformat(),
                'diagnosis': diagnosis_data
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"诊断报告已保存: {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"保存诊断报告错误: {str(e)}")
            raise
    
    def import_patient_data(self, filepath: str) -> Dict:
        """从JSON文件导入患者数据"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 验证数据格式
            if not self._validate_patient_data(data):
                raise ValueError("患者数据格式无效")
            
            logger.info(f"患者数据已导入: {filepath}")
            return data
            
        except Exception as e:
            logger.error(f"导入患者数据错误: {str(e)}")
            raise
    
    def export_database_backup(self, all_patients: List[Dict], all_chats: List[Dict]) -> str:
        """导出数据库备份"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"database_backup_{timestamp}.json"
            filepath = os.path.join(self.export_dir, filename)
            
            backup_data = {
                'backup_timestamp': datetime.now().isoformat(),
                'version': '1.0',
                'total_patients': len(all_patients),
                'total_chat_messages': len(all_chats),
                'patients': all_patients,
                'chat_messages': all_chats
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据库备份已保存: {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"导出数据库备份错误: {str(e)}")
            raise
    
    def _format_export_data(self, data: Dict) -> Dict:
        """格式化导出数据"""
        return {
            'export_info': {
                'system': 'Virtual Diagnostician',
                'version': '1.0',
                'export_timestamp': data.get('export_timestamp'),
                'format': 'JSON'
            },
            'patient_data': data.get('patient_info', {}),
            'chat_interaction': {
                'total_messages': len(data.get('chat_history', [])),
                'messages': data.get('chat_history', [])
            },
            'medical_summary': self._generate_medical_summary(data)
        }
    
    def _generate_medical_summary(self, data: Dict) -> Dict:
        """生成医疗摘要"""
        try:
            patient_info = data.get('patient_info', {})
            chat_history = data.get('chat_history', [])
            
            # 提取症状关键词
            symptoms = []
            for message in chat_history:
                if message.get('type') == 'user':
                    content = message.get('content', '').lower()
                    symptom_keywords = ['头痛', '发烧', '咳嗽', '胃痛', '疲劳', '失眠', '恶心', '呕吐']
                    for symptom in symptom_keywords:
                        if symptom in content and symptom not in symptoms:
                            symptoms.append(symptom)
            
            return {
                'patient_age': patient_info.get('age'),
                'patient_gender': patient_info.get('gender'),
                'reported_symptoms': symptoms,
                'conversation_duration': len(chat_history),
                'last_interaction': chat_history[-1].get('timestamp') if chat_history else None
            }
            
        except Exception as e:
            logger.error(f"生成医疗摘要错误: {str(e)}")
            return {}
    
    def _validate_patient_data(self, data: Dict) -> bool:
        """验证患者数据格式"""
        try:
            # 检查必要字段
            if 'patient_data' not in data:
                return False
            
            patient_data = data['patient_data']
            required_fields = ['name']
            
            for field in required_fields:
                if field not in patient_data:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def get_export_files(self) -> List[Dict]:
        """获取所有导出文件列表"""
        try:
            files = []
            for filename in os.listdir(self.export_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.export_dir, filename)
                    stat = os.stat(filepath)
                    
                    files.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            # 按修改时间排序
            files.sort(key=lambda x: x['modified_time'], reverse=True)
            return files
            
        except Exception as e:
            logger.error(f"获取导出文件列表错误: {str(e)}")
            return []
    
    def delete_export_file(self, filename: str) -> bool:
        """删除导出文件"""
        try:
            filepath = os.path.join(self.export_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"删除导出文件: {filepath}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"删除导出文件错误: {str(e)}")
            return False 