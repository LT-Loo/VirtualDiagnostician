# Virtual Diagnostician System
A Python Flask–based virtual medical diagnosis system that provides patient chat interaction, medical history management and data export features. Implemented classifiers using machine learning and computer vision to classify medical conditions from clinical data and imaging.

## Features
- **Intelligent Chat Interaction**: Engage in basic conversations with patients and identify symptom information
- **Patient Record Management**: Create, view, and update patient information and medical history
- **Database Storage**: Store patient data and chat logs with SQLite
- **JSON Data Export**: Export patient data and chat records in JSON format
- **Responsive Interface**: Modern UI compatible with desktop and mobile devices

## Project Structure
```
VirtualDiagnostician/
├── src/
│   ├── main.py                 # Main application entry point
│   ├── database/               # Database-related
│   │   ├── __init__.py
│   │   └── db_manager.py       # Database manager
│   ├── services/               
│   │   ├── __init__.py
│   │   ├── chat_service.py     # Chat service
│   │   └── patient_service.py  # Patient service
│   ├── utils/                  
│   │   ├── __init__.py
│   │   └── json_handler.py     # JSON handling
│   ├── templates/              # HTML template
│   │   └── index.html          # Main page
│   └── static/                 
│       ├── css/
│       │   └── styles.css      
│       └── js/
│           └── app.js          # Frontend JavaScript
├── ml-models/                  # Machine learning models
└── training_data/              # Training data
```

## Quick Start
### Install dependencies
```bash
pip install -r requirements.txt
```
### 2. Run system
```bash
cd src
python main.py
```
### 3. Access system
Open your browser and visit http://localhost:5000

## Chat Functionality
The system supports the following types of conversation:
- **Greetings**: "Hello", "Hi"
- **Identity questions**: "What’s your name?", "Who are you?"
- **Status questions**: "How are you?", "How’s it going?"
- **Symptom descriptions**: Automatically detects symptoms such as headache, fever, cough
- **Farewells**: "Goodbye", "Bye"

## Patient Management
### Create a new patient
Click “New Patient” and fill in details, including name (required), age, gender, phone, email

### View patient information
Information displayed include basic personal information and medical history records.

## API
### Chat
- `POST /api/chat` - To send chat message
- `GET /api/chat/history/<patient_id>` - To retrieve chat history
- 
### Patient
- `POST /api/patient` - To create new patient
- `GET /api/patient/<patient_id>` - To retrieve patient information

### Export
- `GET /api/export/patient/<patient_id>` - Export patient data in JSON format

## Frontend Features
- **Responsive design**: Works across desktop and mobile
- **Real-time chat**: Smooth conversation experience
- **Data visualization**: Conversation statistics and patient info display
- **Modern UI**: Built with Tailwind CSS

## Classifiers
### 1. Diabetes
- **Model**: Random Forest
- **Dependencies**: Scikit-learn
- **Data**: Alphanumeric data of blood test records (JSON format)
- **Accuracy**: 85%
- **Total Prediction Time**: 20 seconds for 1000+ blood test records
### 2. COVID
- **Model**: Long Short-Term Memory (LSTM) + CNN
- **Dependencies**: PyTorch, OpenCV
- **Data**: For each patient, five short videos (2s-5s) of lung ultrasonic scans and alphanumeric data of clinical information (JSON format)
- **Accuracy**: 75%
- **Total Prediction Time**: 30 seconds

## Tech Stack
- **Framework**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3 (Tailwind), JavaScript
- **Icons**: Font Awesome
- **Machine Learning**: Random Forest, CNN
- **ML Dependencies**: Scikit-learn, PyTorch, OpenCV

## Disclaimer
- This system is for **supporting medical consultation** only, not a replacement for professional diagnosis
- **Do not** use this system in emergency situations
- All medical decisions should be confirmed with a healthcare professional

## Developer
Hongyuan Wang (Web Development & Patient/Medical Data Management)  
Ler Theng Loo (Disease Classifiers - Data Preprocessing + Model Training & Evaluation)
