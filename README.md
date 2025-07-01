# 虚拟诊断助手系统

这是一个基于Python Flask的虚拟医生诊断系统，提供患者聊天交互、病史管理和数据导出功能。

## 🏥 功能特性

- **智能聊天交互**: 与患者进行基本对话，识别症状信息
- **患者档案管理**: 创建、查看、更新患者信息和病史
- **数据库存储**: 使用SQLite存储患者数据和聊天记录
- **JSON数据导出**: 支持患者数据和聊天记录的JSON格式导出
- **响应式界面**: 兼容桌面和移动设备的现代化UI

## 📁 项目结构

```
VirtualDiagnostician/
├── src/
│   ├── main.py                 # 主应用入口
│   ├── database/               # 数据库相关
│   │   ├── __init__.py
│   │   └── db_manager.py       # 数据库管理器
│   ├── services/               # 业务逻辑
│   │   ├── __init__.py
│   │   ├── chat_service.py     # 聊天服务
│   │   └── patient_service.py  # 患者服务
│   ├── utils/                  # 工具类
│   │   ├── __init__.py
│   │   └── json_handler.py     # JSON处理工具
│   ├── templates/              # HTML模板
│   │   └── index.html          # 主页面
│   └── static/                 # 静态文件
│       ├── css/
│       │   └── styles.css      # 自定义样式
│       └── js/
│           └── app.js          # 前端JavaScript
├── ml-models/                  # 机器学习模型
└── training_data/              # 训练数据
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动系统

```bash
cd src
python main.py
```

### 3. 访问系统

打开浏览器访问: http://localhost:5000

## 💬 聊天功能

系统支持以下类型的对话：

- **问候语**: "你好"、"嗨"、"您好"
- **身份询问**: "你叫什么"、"你是谁"
- **状态询问**: "你好吗"、"你怎么样"
- **症状描述**: 自动识别头痛、发烧、咳嗽等症状
- **告别语**: "再见"、"拜拜"

## 👤 患者管理

### 创建新患者

点击"新患者"按钮，填写患者信息：
- 姓名（必填）
- 年龄
- 性别
- 电话
- 邮箱

### 查看患者信息

- 基本信息显示
- 病史记录查看
- 诊断历史追踪

## 📊 数据库设计

### 患者表 (patients)
- id: 患者唯一标识
- name: 姓名
- age: 年龄
- gender: 性别
- phone: 电话
- email: 邮箱
- medical_history: 病史（JSON格式）
- created_at: 创建时间
- updated_at: 更新时间

### 聊天记录表 (chat_messages)
- id: 消息ID
- patient_id: 患者ID
- message_type: 消息类型（user/assistant）
- content: 消息内容
- timestamp: 时间戳

### 诊断记录表 (diagnosis_records)
- id: 诊断ID
- patient_id: 患者ID
- symptoms: 症状（JSON格式）
- diagnosis: 诊断结果
- confidence: 置信度
- created_at: 创建时间

## 📤 数据导出

### 支持的导出格式

- 患者完整数据（JSON）
- 聊天历史记录（JSON）
- 诊断报告（JSON）
- 数据库完整备份（JSON）

### 导出文件格式示例

```json
{
  "export_info": {
    "system": "Virtual Diagnostician",
    "version": "1.0",
    "export_timestamp": "2024-01-15T10:30:00",
    "format": "JSON"
  },
  "patient_data": {
    "id": "patient_123",
    "name": "张三",
    "age": 35,
    "gender": "男",
    "medical_history": {...}
  },
  "chat_interaction": {
    "total_messages": 10,
    "messages": [...]
  },
  "medical_summary": {
    "reported_symptoms": ["头痛", "发烧"],
    "conversation_duration": 10,
    "last_interaction": "2024-01-15T10:30:00"
  }
}
```

## 🛠️ API 接口

### 聊天接口
- `POST /api/chat` - 发送聊天消息
- `GET /api/chat/history/<patient_id>` - 获取聊天历史

### 患者接口
- `POST /api/patient` - 创建新患者
- `GET /api/patient/<patient_id>` - 获取患者信息

### 导出接口
- `GET /api/export/patient/<patient_id>` - 导出患者数据

## 🎨 前端特性

- **响应式设计**: 适配桌面和移动设备
- **实时聊天**: 流畅的聊天体验
- **症状识别**: 自动高亮显示症状关键词
- **数据可视化**: 对话统计和患者信息展示
- **现代化UI**: 使用Tailwind CSS构建

## 🔧 技术栈

- **后端**: Python Flask
- **数据库**: SQLite
- **前端**: HTML5, CSS3 (Tailwind), JavaScript
- **图标**: Font Awesome
- **响应式**: Mobile-first设计

## 📝 使用示例

### 基本对话流程

1. 打开系统，选择或创建患者
2. 在聊天界面输入症状描述
3. AI助手会回复并记录症状
4. 继续对话获取更多信息
5. 导出对话记录或患者数据

### 示例对话

```
患者: 你好
助手: 您好！我是您的虚拟诊断助手。今天感觉怎么样？

患者: 我头痛
助手: 我了解您的症状。能详细描述一下症状的持续时间和严重程度吗？

患者: 头痛已经两天了，比较严重
助手: 谢谢您的描述。这些症状什么时候开始的？有没有其他伴随症状？
```

## ⚠️ 重要说明

- 本系统仅用于辅助医疗咨询，不能替代专业医生诊断
- 请勿将此系统用于紧急医疗情况
- 所有医疗决策应咨询专业医生

## 🤝 贡献

欢迎提交问题和改进建议！

## �� 许可证

MIT License 