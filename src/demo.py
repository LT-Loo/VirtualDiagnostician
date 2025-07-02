#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
虚拟诊断助手系统演示脚本
用于测试系统的各项功能
"""

import sys
import time
from database.db_manager import DatabaseManager
from services.chat_service import ChatService
from services.patient_service import PatientService
from utils.json_handler import JSONHandler

def print_header(text):
    """打印标题"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_section(text):
    """打印章节"""
    print(f"\n--- {text} ---")

def simulate_typing(text, delay=0.03):
    """模拟打字效果"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def demo_database():
    """演示数据库功能"""
    print_section("数据库初始化")
    
    db_manager = DatabaseManager("demo_virtual_diagnostician.db")
    print("✓ 数据库初始化完成")
    print("✓ 创建患者表、聊天记录表、诊断记录表")
    
    return db_manager

def demo_patient_service(db_manager):
    """演示患者服务功能"""
    print_section("患者管理服务演示")
    
    patient_service = PatientService(db_manager)
    
    # 创建示例患者
    print("正在创建示例患者...")
    patient_service.create_sample_patients()
    print("✓ 创建示例患者成功")
    
    # 搜索患者
    print("\n搜索患者 '张':")
    patients = patient_service.search_patients("张")
    for patient in patients:
        print(f"  - {patient['name']} ({patient['age']}岁, {patient['gender']})")
    
    # 获取患者统计
    print("\n患者统计信息:")
    summary = patient_service.get_patients_summary()
    print(f"  总患者数: {summary.get('total_patients', 0)}")
    print(f"  性别分布: {summary.get('gender_distribution', {})}")
    print(f"  年龄分布: {summary.get('age_distribution', {})}")
    
    return patient_service

def demo_chat_service(db_manager):
    """演示聊天服务功能"""
    print_section("聊天服务演示")
    
    chat_service = ChatService(db_manager)
    
    # 模拟对话
    test_messages = [
        ("你好", "问候"),
        ("你叫什么名字", "身份询问"),
        ("我头痛", "症状描述"),
        ("头痛已经两天了", "症状详细描述"),
        ("谢谢", "感谢"),
        ("再见", "告别")
    ]
    
    patient_id = "demo_patient"
    print(f"开始与患者 {patient_id} 的对话演示...\n")
    
    for message, category in test_messages:
        print(f"患者: {message}")
        simulate_typing("AI助手正在思考...", 0.05)
        
        response = chat_service.process_message(message, patient_id)
        print(f"助手: {response}\n")
        time.sleep(1)
    
    # 获取对话历史
    print("获取对话历史:")
    history = chat_service.get_chat_history(patient_id)
    print(f"  共有 {len(history)} 条消息")
    
    # 获取对话摘要
    summary = chat_service.get_conversation_summary(patient_id)
    print(f"  用户消息: {summary.get('user_messages', 0)} 条")
    print(f"  助手回复: {summary.get('assistant_messages', 0)} 条")
    
    return chat_service

def demo_json_handler():
    """演示JSON处理功能"""
    print_section("JSON数据处理演示")
    
    json_handler = JSONHandler("demo_exports")
    
    # 模拟患者数据
    demo_data = {
        'patient_info': {
            'id': 'demo_patient',
            'name': '演示患者',
            'age': 30,
            'gender': '男',
            'phone': '13800138000',
            'medical_history': {
                'allergies': ['青霉素'],
                'chronic_conditions': [],
                'records': [
                    {
                        'date': '2024-01-15',
                        'condition': '头痛',
                        'symptoms': ['头痛', '疲劳'],
                        'treatment': '休息，观察'
                    }
                ]
            }
        },
        'chat_history': [
            {'type': 'user', 'content': '你好', 'timestamp': '2024-01-15T10:00:00'},
            {'type': 'assistant', 'content': '您好！我是您的虚拟诊断助手。', 'timestamp': '2024-01-15T10:00:01'},
            {'type': 'user', 'content': '我头痛', 'timestamp': '2024-01-15T10:01:00'},
            {'type': 'assistant', 'content': '我了解您的症状。能详细描述一下吗？', 'timestamp': '2024-01-15T10:01:01'}
        ],
        'export_timestamp': '2024-01-15T10:05:00'
    }
    
    # 保存数据
    print("正在保存患者数据...")
    filename = json_handler.save_patient_data('demo_patient', demo_data)
    print(f"✓ 数据已保存为: {filename}")
    
    # 获取导出文件列表
    files = json_handler.get_export_files()
    print(f"\n导出文件列表 (共 {len(files)} 个文件):")
    for file_info in files[:3]:  # 只显示前3个
        print(f"  - {file_info['filename']} ({file_info['size']} bytes)")
    
    return json_handler

def demo_integration():
    """演示系统集成测试"""
    print_section("系统集成测试")
    
    # 初始化所有组件
    db_manager = DatabaseManager("integration_test.db")
    patient_service = PatientService(db_manager)
    chat_service = ChatService(db_manager)
    json_handler = JSONHandler("integration_exports")
    
    print("正在执行完整工作流程...")
    
    # 1. 创建患者
    patient_data = {
        'name': '集成测试患者',
        'age': 25,
        'gender': '女',
        'phone': '13900139000',
        'email': 'test@example.com',
        'medical_history': {
            'allergies': [],
            'chronic_conditions': ['偏头痛'],
            'records': []
        }
    }
    
    patient_id = patient_service.create_patient(patient_data)
    print(f"✓ 创建患者: {patient_id}")
    
    # 2. 进行对话
    messages = ["你好", "我偏头痛发作了", "疼痛很严重", "谢谢你的建议"]
    for msg in messages:
        chat_service.process_message(msg, patient_id)
    print("✓ 完成对话交互")
    
    # 3. 获取完整数据
    patient_info = patient_service.get_patient_by_id(patient_id)
    chat_history = chat_service.get_chat_history(patient_id)
    
    # 4. 导出数据
    export_data = {
        'patient_info': patient_info,
        'chat_history': chat_history,
        'export_timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
    }
    
    filename = json_handler.save_patient_data(patient_id, export_data)
    print(f"✓ 数据导出完成: {filename}")
    
    print("\n✅ 系统集成测试完成！")

def main():
    """主函数"""
    print_header("虚拟诊断助手系统演示")
    print("这个演示将展示系统的各项功能...")
    
    try:
        # 1. 数据库演示
        print_header("1. 数据库管理")
        db_manager = demo_database()
        
        # 2. 患者服务演示
        print_header("2. 患者管理")
        patient_service = demo_patient_service(db_manager)
        
        # 3. 聊天服务演示
        print_header("3. 聊天交互")
        chat_service = demo_chat_service(db_manager)
        
        # 4. JSON处理演示
        print_header("4. 数据导出")
        json_handler = demo_json_handler()
        
        # 5. 集成测试
        print_header("5. 系统集成测试")
        demo_integration()
        
        # 完成
        print_header("演示完成")
        print("🎉 所有功能演示完成！")
        print("\n系统功能总结:")
        print("  ✓ SQLite数据库管理")
        print("  ✓ 患者信息CRUD操作")
        print("  ✓ 智能聊天交互")
        print("  ✓ 症状识别和记录")
        print("  ✓ JSON数据导入导出")
        print("  ✓ 完整工作流程集成")
        
        print(f"\n📁 生成的文件:")
        print("  - demo_virtual_diagnostician.db (演示数据库)")
        print("  - integration_test.db (集成测试数据库)")
        print("  - demo_exports/ (演示导出文件)")
        print("  - integration_exports/ (集成测试导出文件)")
        
        print(f"\n🚀 启动完整系统:")
        print("  cd src && python main.py")
        print("  然后访问 http://localhost:5000")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 