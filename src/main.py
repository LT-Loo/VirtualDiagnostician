from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime

from database.db_manager import DatabaseManager
from services.chat_service import ChatService
from services.patient_service import PatientService
from services.training_data_service import TrainingDataService
from utils.json_handler import JSONHandler

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 初始化服务
db_manager = DatabaseManager()
chat_service = ChatService(db_manager)
patient_service = PatientService(db_manager)
training_data_service = TrainingDataService(db_manager)
json_handler = JSONHandler()

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        patient_id = data.get('patient_id', 'default')
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # 处理聊天消息
        response = chat_service.process_message(user_message, patient_id)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })
    
    except Exception as e:
        logger.error(f"Chat processing error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/patient/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    """获取患者信息"""
    try:
        # 检查是否是训练数据患者
        if patient_id.startswith('training_'):
            patient_data = training_data_service.load_patient_from_file(patient_id.replace('training_', ''))
            if patient_data:
                patient_data['id'] = patient_id  # 保持training_前缀
                return jsonify(patient_data)
            else:
                return jsonify({'error': 'Training patient not found'}), 404
        else:
            patient_data = patient_service.get_patient_by_id(patient_id)
            if patient_data:
                return jsonify(patient_data)
            else:
                return jsonify({'error': 'Patient not found'}), 404
    
    except Exception as e:
        logger.error(f"Error getting patient information: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/patient', methods=['POST'])
def create_patient():
    """创建新患者"""
    try:
        data = request.get_json()
        patient_id = patient_service.create_patient(data)
        return jsonify({'patient_id': patient_id, 'status': 'success'})
    
    except Exception as e:
        logger.error(f"Error creating patient: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/patients', methods=['GET'])
def get_patients():
    """获取患者列表（仅普通患者）"""
    try:
        # 只获取普通患者
        patients = patient_service.search_patients()
        return jsonify(patients)
    
    except Exception as e:
        logger.error(f"Error getting patient list: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/chat/history/<patient_id>', methods=['GET'])
def get_chat_history(patient_id):
    """获取聊天历史"""
    try:
        history = chat_service.get_chat_history(patient_id)
        return jsonify(history)
    
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/export/patient/<patient_id>', methods=['GET'])
def export_patient_data(patient_id):
    """导出患者数据为JSON"""
    try:
        # 检查是否是训练数据患者
        if patient_id.startswith('training_'):
            # 导出训练数据格式
            export_data = training_data_service.export_training_patient(patient_id)
            if export_data:
                return jsonify({
                    'status': 'success',
                    'filename': export_data['filename'],
                    'data': export_data['data'],
                    'is_training_data': True
                })
            else:
                return jsonify({'error': 'Training patient not found'}), 404
        else:
            # 原有的导出逻辑
            patient_data = patient_service.get_patient_by_id(patient_id)
            chat_history = chat_service.get_chat_history(patient_id)
            
            export_data = {
                'patient_info': patient_data,
                'chat_history': chat_history,
                'export_timestamp': datetime.now().isoformat()
            }
            
            # 保存到JSON文件
            filename = json_handler.save_patient_data(patient_id, export_data)
            
            return jsonify({
                'status': 'success',
                'filename': filename,
                'data': export_data,
                'is_training_data': False
            })
    
    except Exception as e:
        logger.error(f"Error exporting patient data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# 训练数据相关API端点
@app.route('/api/training/patients', methods=['GET'])
def get_training_patients():
    """获取训练数据患者列表"""
    try:
        limit = request.args.get('limit', 20, type=int)
        patients = training_data_service.load_training_patients(limit)
        return jsonify(patients)
    
    except Exception as e:
        logger.error(f"Error getting training patients: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/training/patient/<patient_id>', methods=['GET'])
def get_training_patient(patient_id):
    """获取单个训练数据患者信息"""
    try:
        # 去掉training_前缀
        original_id = patient_id.replace('training_', '') if patient_id.startswith('training_') else patient_id
        patient_data = training_data_service.load_patient_from_file(original_id)
        
        if patient_data:
            return jsonify(patient_data)
        else:
            return jsonify({'error': 'Training patient not found'}), 404
    
    except Exception as e:
        logger.error(f"Error getting training patient: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/training/summary', methods=['GET'])
def get_training_summary():
    """获取训练数据统计信息"""
    try:
        summary = training_data_service.get_training_patients_summary()
        return jsonify(summary)
    
    except Exception as e:
        logger.error(f"Error getting training summary: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/training/import', methods=['POST'])
def import_training_patients():
    """将训练数据患者导入到数据库"""
    try:
        data = request.get_json()
        limit = data.get('limit', 10)
        
        result = training_data_service.import_training_patients_to_db(limit)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error importing training patients: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/training/import-json', methods=['POST'])
def import_json_to_training():
    """导入JSON文件到训练数据Set-0文件夹"""
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # 检查文件格式
        if not file.filename.endswith('.json'):
            return jsonify({'error': 'File must be a JSON file'}), 400
        
        # 读取文件内容
        file_content = file.read().decode('utf-8')
        
        # 验证JSON格式
        try:
            import json
            data = json.loads(file_content)
            validation_result = training_data_service.validate_json_format(data)
            
            if not validation_result['valid']:
                return jsonify({
                    'error': 'Invalid JSON format',
                    'details': validation_result['errors']
                }), 400
        
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON format'}), 400
        
        # 导入文件到Set-0文件夹
        result = training_data_service.import_json_to_set0(file_content, file.filename)
        
        if result['status'] == 'success':
            return jsonify({
                'status': 'success',
                'message': result['message'],
                'filename': result['filename'],
                'patient_id': result['patient_id']
            })
        else:
            return jsonify({'error': result['error']}), 400
    
    except Exception as e:
        logger.error(f"Error importing JSON file: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/training/rename-patient', methods=['POST'])
def rename_training_patient():
    """重命名训练数据患者文件夹"""
    try:
        data = request.get_json()
        old_id = data.get('old_id')
        new_id = data.get('new_id')
        
        if not old_id or not new_id:
            return jsonify({'error': 'Both old_id and new_id are required'}), 400
        
        result = training_data_service.rename_patient_folder(old_id, new_id)
        
        if result['status'] == 'success':
            return jsonify({
                'status': 'success',
                'message': result['message'],
                'old_id': result['old_id'],
                'new_id': result['new_id']
            })
        else:
            return jsonify({'error': result['error']}), 400
    
    except Exception as e:
        logger.error(f"Error renaming patient: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # 初始化数据库
    db_manager.init_database()
    
    # 创建示例患者数据
    try:
        patient_service.create_sample_patients()
        logger.info("Sample patient data creation completed")
    except Exception as e:
        logger.info("Sample patients already exist or creation failed")
    
    print("🏥 Virtual Diagnostic System Starting...")
    print("📋 System Features:")
    print("   ✓ Patient Chat Interaction")
    print("   ✓ Medical History Management") 
    print("   ✓ Data Export Functions")
    print("   ✓ Training Data Integration")
    print("🌐 Service URL: http://localhost:5000")
    print("📝 Test Conversations:")
    print("   • Hi, how are you?")
    print("   • What is your name?")
    print("   • I have a headache")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 