#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
虚拟诊断助手系统启动脚本
"""

import os
import sys
import subprocess

def check_requirements():
    """检查依赖是否安装"""
    try:
        import flask
        import flask_cors
        print("✓ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def start_system():
    """启动系统"""
    print("🏥 虚拟诊断助手系统")
    print("=" * 50)
    
    # 检查依赖
    if not check_requirements():
        return False
    
    # 进入src目录
    src_dir = os.path.join(os.path.dirname(__file__), 'src')
    
    try:
        print("\n🚀 正在启动系统...")
        print("📁 工作目录:", src_dir)
        print("🌐 服务地址: http://localhost:5000")
        print("按 Ctrl+C 停止服务\n")
        
        # 启动Flask应用
        os.chdir(src_dir)
        subprocess.run([sys.executable, 'main.py'])
        
    except KeyboardInterrupt:
        print("\n\n👋 系统已停止")
        return True
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        return False

if __name__ == "__main__":
    success = start_system()
    sys.exit(0 if success else 1) 