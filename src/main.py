from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime

from database.db_manager import DatabaseManager
from services.chat_service import ChatService
from services.patient_service import PatientService
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
    """获取患者列表"""
    try:
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
            'data': export_data
        })
    
    except Exception as e:
        logger.error(f"Error exporting patient data: {str(e)}")
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
    print("🌐 Service URL: http://localhost:5000")
    print("📝 Test Conversations:")
    print("   • Hi, how are you?")
    print("   • What is your name?")
    print("   • I have a headache")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 