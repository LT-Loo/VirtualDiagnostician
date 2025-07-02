class VirtualDiagnostician {
    constructor() {
        this.currentPatientId = 'default';
        this.messageCount = 0;
        this.chatStartTime = null;
        this.loadedTrainingPatients = [];
        this.trainingDataStats = null;
        
        this.initializeElements();
        this.bindEvents();
        this.loadPatients();
        this.initializeChat();
        this.loadTrainingDataStats();
    }

    initializeElements() {
        // 聊天相关元素
        this.chatContainer = document.getElementById('chatContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        
        // 患者相关元素
        this.patientSelect = document.getElementById('patientSelect');
        this.patientName = document.getElementById('patientName');
        this.patientAge = document.getElementById('patientAge');
        this.patientGender = document.getElementById('patientGender');
        this.patientPhone = document.getElementById('patientPhone');
        this.medicalHistory = document.getElementById('medicalHistory');
        
        // 统计元素
        this.messageCountEl = document.getElementById('messageCount');
        this.chatDurationEl = document.getElementById('chatDuration');
        this.symptomsList = document.getElementById('symptomsList');
        
        // 按钮元素
        this.newPatientBtn = document.getElementById('newPatientBtn');
        this.exportBtn = document.getElementById('exportBtn');
        this.importBtn = document.getElementById('importBtn');
        this.clearChatBtn = document.getElementById('clearChatBtn');
        this.exportChatBtn = document.getElementById('exportChatBtn');
        this.viewHistoryBtn = document.getElementById('viewHistoryBtn');
        
        // 训练数据控制元素
        this.loadedTrainingCount = document.getElementById('loadedTrainingCount');
        this.totalTrainingCount = document.getElementById('totalTrainingCount');
        this.trainingLoadCount = document.getElementById('trainingLoadCount');
        this.loadMoreTrainingBtn = document.getElementById('loadMoreTrainingBtn');
        this.loadingHint = document.getElementById('loadingHint');
        
        // 模态框元素
        this.newPatientModal = document.getElementById('newPatientModal');
        this.savePatientBtn = document.getElementById('savePatientBtn');
        this.cancelPatientBtn = document.getElementById('cancelPatientBtn');
        
        // 导入模态框元素
        this.importDataModal = document.getElementById('importDataModal');
        this.importFileInput = document.getElementById('importFileInput');
        this.importPreview = document.getElementById('importPreview');
        this.importPreviewContent = document.getElementById('importPreviewContent');
        this.confirmImportBtn = document.getElementById('confirmImportBtn');
        this.cancelImportBtn = document.getElementById('cancelImportBtn');
    }

    bindEvents() {
        // 发送消息事件
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 患者选择事件
        this.patientSelect.addEventListener('change', (e) => {
            this.currentPatientId = e.target.value;
            this.loadPatientInfo();
            this.loadChatHistory();
        });

        // 按钮事件
        this.newPatientBtn.addEventListener('click', () => this.showNewPatientModal());
        this.exportBtn.addEventListener('click', () => this.exportPatientData());
        this.importBtn.addEventListener('click', () => this.showImportDataModal());
        this.clearChatBtn.addEventListener('click', () => this.clearChat());
        this.exportChatBtn.addEventListener('click', () => this.exportChatHistory());
        this.viewHistoryBtn.addEventListener('click', () => this.viewHistory());
        
        // 训练数据控制事件
        this.loadMoreTrainingBtn.addEventListener('click', () => this.loadMoreTrainingData());
        this.trainingLoadCount.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.loadMoreTrainingData();
            }
        });
        
        // 模态框事件
        this.savePatientBtn.addEventListener('click', () => this.saveNewPatient());
        this.cancelPatientBtn.addEventListener('click', () => this.hideNewPatientModal());
        
        // 导入模态框事件
        this.importFileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        this.confirmImportBtn.addEventListener('click', () => this.confirmImport());
        this.cancelImportBtn.addEventListener('click', () => this.hideImportDataModal());
        
        // 点击模态框外部关闭
        this.newPatientModal.addEventListener('click', (e) => {
            if (e.target === this.newPatientModal) {
                this.hideNewPatientModal();
            }
        });

        this.importDataModal.addEventListener('click', (e) => {
            if (e.target === this.importDataModal) {
                this.hideImportDataModal();
            }
        });

        // 定时更新对话时长
        setInterval(() => this.updateChatDuration(), 1000);
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;

        // 禁用发送按钮
        this.sendBtn.disabled = true;
        this.messageInput.disabled = true;

        try {
            // 显示用户消息
            this.displayMessage(message, 'user');
            this.messageInput.value = '';

            // 显示输入指示器
            this.showTypingIndicator();

            // 发送API请求
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    patient_id: this.currentPatientId
                })
            });

            const data = await response.json();

            // 隐藏输入指示器
            this.hideTypingIndicator();

            if (response.ok) {
                // 显示AI回复
                this.displayMessage(data.response, 'assistant');
                this.updateMessageCount();
                this.extractSymptoms(message);
            } else {
                this.showError('Failed to send message: ' + data.error);
            }

        } catch (error) {
            this.hideTypingIndicator();
            this.showError('Network error: ' + error.message);
        } finally {
            // 重新启用发送按钮
            this.sendBtn.disabled = false;
            this.messageInput.disabled = false;
            this.messageInput.focus();
        }
    }

    displayMessage(content, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `flex ${type === 'user' ? 'justify-end' : 'justify-start'} fade-in`;

        const messageBubble = document.createElement('div');
        messageBubble.className = `max-w-xs lg:max-w-md px-4 py-2 rounded-lg text-white ${
            type === 'user' ? 'message-user' : 'message-assistant'
        }`;

        // 添加头像和时间戳
        const timestamp = new Date().toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        messageBubble.innerHTML = `
            <div class="flex items-start space-x-2">
                <div class="flex-shrink-0">
                    <i class="fas ${type === 'user' ? 'fa-user' : 'fa-robot'} text-sm"></i>
                </div>
                <div class="flex-1">
                    <div class="text-sm">${content}</div>
                    <div class="text-xs opacity-75 mt-1">${timestamp}</div>
                </div>
            </div>
        `;

        messageDiv.appendChild(messageBubble);
        this.chatContainer.appendChild(messageDiv);
        
        // 滚动到底部
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;

        // 初始化聊天开始时间
        if (!this.chatStartTime) {
            this.chatStartTime = new Date();
        }
    }

    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'typingIndicator';
        indicator.className = 'flex justify-start fade-in';
        indicator.innerHTML = `
            <div class="max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-gray-300 text-gray-600">
                <div class="flex items-center space-x-1">
                    <div class="flex space-x-1">
                        <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                        <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.1s"></div>
                        <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                    </div>
                    <span class="text-sm ml-2">AI is thinking...</span>
                </div>
            </div>
        `;
        this.chatContainer.appendChild(indicator);
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    async loadPatients() {
        try {
            // 只加载普通患者
            const response = await fetch('/api/patients');
            if (response.ok) {
                const allPatients = await response.json();
                const regularPatients = allPatients.filter(p => !p.id.startsWith('training_'));
                
                // 重新填充选择器
                this.updatePatientSelect(regularPatients, this.loadedTrainingPatients);
            }
            
            this.loadPatientInfo();
        } catch (error) {
            console.error('Failed to load patient list:', error);
        }
    }
    
    updatePatientSelect(regularPatients, trainingPatients) {
        // 清空并重新填充选择器
        this.patientSelect.innerHTML = '<option value="default">Default Patient</option>';
        
        // 添加普通患者
        if (regularPatients.length > 0) {
            const regularGroup = document.createElement('optgroup');
            regularGroup.label = 'Regular Patients';
            regularPatients.forEach(patient => {
                const option = document.createElement('option');
                option.value = patient.id;
                option.textContent = patient.name;
                regularGroup.appendChild(option);
            });
            this.patientSelect.appendChild(regularGroup);
        }
        
        // 添加训练数据患者
        if (trainingPatients.length > 0) {
            const trainingGroup = document.createElement('optgroup');
            trainingGroup.label = 'Training Data Patients';
            trainingPatients.forEach(patient => {
                const option = document.createElement('option');
                option.value = patient.id;
                option.textContent = `${patient.name} (Training)`;
                trainingGroup.appendChild(option);
            });
            this.patientSelect.appendChild(trainingGroup);
        }
        
        // 更新统计信息
        this.updateTrainingDataStats();
    }

    async loadPatientInfo() {
        try {
            if (this.currentPatientId === 'default') {
                this.patientName.textContent = 'Default Patient';
                this.patientAge.textContent = '-';
                this.patientGender.textContent = '-';
                this.patientPhone.textContent = '-';
                this.medicalHistory.textContent = 'No medical history recorded';
                return;
            }

            const response = await fetch(`/api/patient/${this.currentPatientId}`);
            if (response.ok) {
                const patient = await response.json();
                this.updatePatientDisplay(patient);
            }
        } catch (error) {
            console.error('Failed to load patient information:', error);
        }
    }

    updatePatientDisplay(patient) {
        // 检查是否是训练数据患者
        const isTrainingData = patient.id && patient.id.startsWith('training_');
        
        this.patientName.textContent = patient.name || '-';
        this.patientAge.textContent = patient.age || '-';
        this.patientGender.textContent = patient.gender || '-';
        this.patientPhone.textContent = patient.phone || '-';
        
        // 训练数据患者不需要特殊标识，保持简洁
        // if (isTrainingData) {
        //     this.patientName.innerHTML = `${patient.name || '-'} <span class="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full ml-2">Training Data</span>`;
        // }
        
        // 显示病史摘要
        if (patient.medical_history && patient.medical_history.records) {
            const historyText = patient.medical_history.records
                .slice(-3)
                .map(record => record.condition)
                .join(', ');
            this.medicalHistory.textContent = historyText || 'No medical history recorded';
        } else if (isTrainingData && patient.medical_history && patient.medical_history.notes) {
            // 训练数据显示notes
            this.medicalHistory.textContent = patient.medical_history.notes || 'No medical history recorded';
        } else {
            this.medicalHistory.textContent = 'No medical history recorded';
        }
        
        // 为训练数据患者显示额外信息
        if (isTrainingData) {
            this.addTrainingDataInfo(patient);
        } else {
            this.removeTrainingDataInfo();
        }
    }

    async loadChatHistory() {
        try {
            const response = await fetch(`/api/chat/history/${this.currentPatientId}`);
            if (response.ok) {
                const history = await response.json();
                this.displayChatHistory(history);
            }
        } catch (error) {
            console.error('Failed to load chat history:', error);
        }
    }

    displayChatHistory(history) {
        // 清空聊天容器
        this.chatContainer.innerHTML = '';
        
        if (history.length === 0) {
            this.chatContainer.innerHTML = `
                <div class="text-center text-gray-500 text-sm">
                    <i class="fas fa-robot text-2xl mb-2"></i>
                    <p>Hello! I'm your Virtual Diagnostic Assistant. Please tell me about your symptoms or concerns.</p>
                </div>
            `;
            return;
        }

        // 显示历史消息
        history.forEach(msg => {
            this.displayMessage(msg.content, msg.type);
        });

        this.messageCount = history.length;
        this.updateMessageCount();
    }

    showNewPatientModal() {
        this.newPatientModal.classList.remove('hidden');
        document.getElementById('newPatientName').focus();
    }

    hideNewPatientModal() {
        this.newPatientModal.classList.add('hidden');
        // 清空表单
        document.getElementById('newPatientName').value = '';
        document.getElementById('newPatientAge').value = '';
        document.getElementById('newPatientGender').value = '';
        document.getElementById('newPatientPhone').value = '';
        document.getElementById('newPatientEmail').value = '';
    }

    async saveNewPatient() {
        const patientData = {
            name: document.getElementById('newPatientName').value.trim(),
            age: parseInt(document.getElementById('newPatientAge').value) || null,
            gender: document.getElementById('newPatientGender').value,
            phone: document.getElementById('newPatientPhone').value.trim(),
            email: document.getElementById('newPatientEmail').value.trim()
        };

        if (!patientData.name) {
            alert('Please enter patient name');
            return;
        }

        try {
            const response = await fetch('/api/patient', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(patientData)
            });

            const data = await response.json();

            if (response.ok) {
                // 重新加载患者列表
                await this.loadPatients();

                // 选择新患者
                this.patientSelect.value = data.patient_id;
                this.currentPatientId = data.patient_id;
                
                this.hideNewPatientModal();
                this.loadPatientInfo();
                this.loadChatHistory();
                
                this.showSuccess('Patient created successfully');
            } else {
                this.showError('Failed to create patient: ' + data.error);
            }

        } catch (error) {
            this.showError('Network error: ' + error.message);
        }
    }

    showImportDataModal() {
        this.importDataModal.classList.remove('hidden');
        this.importFileInput.focus();
    }
    
    hideImportDataModal() {
        this.importDataModal.classList.add('hidden');
        // 清空表单
        this.importFileInput.value = '';
        this.importPreview.classList.add('hidden');
        this.importPreviewContent.textContent = '';
        this.confirmImportBtn.disabled = true;
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) {
            this.importPreview.classList.add('hidden');
            this.confirmImportBtn.disabled = true;
            return;
        }

        if (!file.name.endsWith('.json')) {
            this.showError('Please select a JSON file');
            this.importFileInput.value = '';
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const content = e.target.result;
                const data = JSON.parse(content);
                
                // 验证必要字段
                if (!data.name) {
                    throw new Error('Missing required field: name');
                }
                
                // 显示预览
                this.importPreviewContent.textContent = JSON.stringify(data, null, 2);
                this.importPreview.classList.remove('hidden');
                this.confirmImportBtn.disabled = false;
                
            } catch (error) {
                this.showError('Invalid JSON file: ' + error.message);
                this.importFileInput.value = '';
                this.importPreview.classList.add('hidden');
                this.confirmImportBtn.disabled = true;
            }
        };
        reader.readAsText(file);
    }

    async confirmImport() {
        const file = this.importFileInput.files[0];
        if (!file) {
            this.showError('Please select a file to import');
            return;
        }

        try {
            this.confirmImportBtn.disabled = true;
            this.confirmImportBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Importing...';

            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/training/import-json', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                this.hideImportDataModal();
                
                // 显示成功消息，包含ID来源信息
                let successMessage = `Data imported successfully to Set-0 folder: ${data.filename}`;
                if (data.id_source === 'filename') {
                    successMessage += ` (Used ID from filename)`;
                } else {
                    successMessage += ` (Generated new ID: ${data.patient_id})`;
                }
                this.showSuccess(successMessage);
                
                // 刷新训练数据统计
                await this.loadTrainingDataStats();
                
                // 重新加载患者列表以包含新导入的患者
                await this.refreshPatientLists();
                
                // 如果当前没有加载足够的训练患者，提示用户加载更多
                if (this.trainingDataStats && this.loadedTrainingPatients.length < this.trainingDataStats.total_patients) {
                    setTimeout(() => {
                        this.showNotification('New patient imported. Click "Load" to see it in the patient list.', 'info');
                    }, 2000);
                }
            } else {
                this.showError('Import failed: ' + data.error);
            }
        } catch (error) {
            this.showError('Import failed: ' + error.message);
        } finally {
            this.confirmImportBtn.disabled = false;
            this.confirmImportBtn.innerHTML = '<i class="fas fa-upload mr-2"></i>Import';
        }
    }
    
    async refreshPatientLists() {
        /**
         * 刷新患者列表，包括普通患者和当前已加载的训练患者
         */
        try {
            // 重新加载普通患者
            const regularResponse = await fetch('/api/patients');
            if (regularResponse.ok) {
                const allPatients = await regularResponse.json();
                const regularPatients = allPatients.filter(p => !p.id.startsWith('training_'));
                
                // 更新患者选择器
                this.updatePatientSelect(regularPatients, this.loadedTrainingPatients);
            }
        } catch (error) {
            console.error('Failed to refresh patient lists:', error);
        }
    }

    async exportPatientData() {
        try {
            const response = await fetch(`/api/export/patient/${this.currentPatientId}`);
            const data = await response.json();

            if (response.ok) {
                // 检查是否是训练数据
                const isTrainingData = data.is_training_data;
                const exportType = isTrainingData ? 'Training Data (Original Format)' : 'Patient Data';
                
                this.showSuccess(`${exportType} exported: ${data.filename}`);
                
                // 创建下载链接
                const blob = new Blob([JSON.stringify(data.data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = data.filename;
                a.click();
                URL.revokeObjectURL(url);
                
                // 如果是训练数据，显示额外提示
                if (isTrainingData) {
                    setTimeout(() => {
                        this.showNotification('Training data exported in original JSON format', 'info');
                    }, 1000);
                }
            } else {
                this.showError('Export failed: ' + data.error);
            }

        } catch (error) {
            this.showError('Export failed: ' + error.message);
        }
    }

    async clearChat() {
        if (confirm('Are you sure you want to clear the chat history? This action cannot be undone.')) {
            this.chatContainer.innerHTML = `
                <div class="text-center text-gray-500 text-sm">
                    <i class="fas fa-robot text-2xl mb-2"></i>
                    <p>Hello! I'm your Virtual Diagnostic Assistant. Please tell me about your symptoms or concerns.</p>
                </div>
            `;
            this.messageCount = 0;
            this.chatStartTime = null;
            this.updateMessageCount();
            this.updateChatDuration();
        }
    }

    updateMessageCount() {
        this.messageCountEl.textContent = this.messageCount;
    }

    updateChatDuration() {
        if (!this.chatStartTime) {
            this.chatDurationEl.textContent = '-';
            return;
        }

        const duration = Math.floor((new Date() - this.chatStartTime) / 1000);
        const minutes = Math.floor(duration / 60);
        const seconds = duration % 60;
        this.chatDurationEl.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    }

    extractSymptoms(message) {
        const symptoms = [];
        const symptomKeywords = ['headache', 'fever', 'cough', 'stomach pain', 'fatigue', 'insomnia', 'nausea', 'vomiting', 'pain', 'tired'];
        
        symptomKeywords.forEach(symptom => {
            if (message.toLowerCase().includes(symptom.toLowerCase())) {
                symptoms.push(symptom);
            }
        });

        if (symptoms.length > 0) {
            this.displaySymptoms(symptoms);
        }
    }

    displaySymptoms(symptoms) {
        this.symptomsList.innerHTML = '';
        symptoms.forEach(symptom => {
            const symptomEl = document.createElement('div');
            symptomEl.className = 'flex items-center justify-between bg-red-50 text-red-700 px-2 py-1 rounded text-sm';
            symptomEl.innerHTML = `
                <span><i class="fas fa-exclamation-triangle mr-1"></i>${symptom}</span>
                <span class="text-xs">${new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</span>
            `;
            this.symptomsList.appendChild(symptomEl);
        });
    }

    initializeChat() {
        this.chatStartTime = null;
        this.messageCount = 0;
        this.updateMessageCount();
        this.updateChatDuration();
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        let bgColor = 'bg-red-500'; // default for error
        if (type === 'success') bgColor = 'bg-green-500';
        else if (type === 'info') bgColor = 'bg-blue-500';
        
        notification.className = `fixed top-4 right-4 px-4 py-2 rounded-lg text-white z-50 ${bgColor}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    async exportChatHistory() {
        try {
            const history = await fetch(`/api/chat/history/${this.currentPatientId}`);
            const data = await history.json();
            
            if (history.ok) {
                const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `chat_history_${this.currentPatientId}_${new Date().toISOString().slice(0, 10)}.json`;
                a.click();
                URL.revokeObjectURL(url);
                
                this.showSuccess('Chat history exported successfully');
            }
        } catch (error) {
            this.showError('Failed to export chat history: ' + error.message);
        }
    }

    async viewHistory() {
        try {
            const response = await fetch(`/api/chat/history/${this.currentPatientId}`);
            const history = await response.json();
            
            if (response.ok) {
                if (history.length === 0) {
                    this.showNotification('No chat history found for this patient', 'info');
                    return;
                }

                // Create history modal
                this.showHistoryModal(history);
            } else {
                this.showError('Failed to load chat history');
            }
        } catch (error) {
            this.showError('Failed to load chat history: ' + error.message);
        }
    }

    addTrainingDataInfo(patient) {
        // 移除现有的训练数据信息
        this.removeTrainingDataInfo();
        
        // 获取患者信息容器
        const patientInfoDiv = document.getElementById('patientInfo');
        
        // 创建训练数据额外信息
        const trainingDataDiv = document.createElement('div');
        trainingDataDiv.id = 'trainingDataInfo';
        trainingDataDiv.className = 'mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200';
        
        trainingDataDiv.innerHTML = `
            <h4 class="text-sm font-medium text-blue-800 mb-2">
                <i class="fas fa-database mr-1"></i>Data Details
            </h4>
            <div class="space-y-1 text-sm">
                ${patient.birthdate ? `<div class="flex justify-between"><span class="text-blue-600">Birth Date:</span><span class="font-medium">${patient.birthdate}</span></div>` : ''}
                ${patient.blood_type ? `<div class="flex justify-between"><span class="text-blue-600">Blood Type:</span><span class="font-medium">${patient.blood_type}</span></div>` : ''}
                ${patient.weight ? `<div class="flex justify-between"><span class="text-blue-600">Weight:</span><span class="font-medium">${patient.weight} kg</span></div>` : ''}
                ${patient.height ? `<div class="flex justify-between"><span class="text-blue-600">Height:</span><span class="font-medium">${patient.height} cm</span></div>` : ''}
                ${patient.address ? `<div class="mt-2"><span class="text-blue-600">Address:</span><br><span class="font-medium text-xs">${patient.address}</span></div>` : ''}
            </div>
        `;
        
        patientInfoDiv.appendChild(trainingDataDiv);
    }
    
    removeTrainingDataInfo() {
        const existingDiv = document.getElementById('trainingDataInfo');
        if (existingDiv) {
            existingDiv.remove();
        }
    }
    
    async loadTrainingDataStats() {
        try {
            const response = await fetch('/api/training/summary');
            if (response.ok) {
                this.trainingDataStats = await response.json();
                this.updateTrainingDataStats();
            }
        } catch (error) {
            console.error('Failed to load training data stats:', error);
        }
    }
    
    async loadMoreTrainingData() {
        try {
            const inputValue = this.trainingLoadCount.value.trim();
            
            // 验证输入
            if (!inputValue) {
                this.showError('Please enter the number of patients to load');
                return;
            }
            
            const count = parseInt(inputValue);
            if (isNaN(count) || count < 1) {
                this.showError('Please enter a valid number (minimum 1)');
                return;
            }
            
            if (this.trainingDataStats && count > this.trainingDataStats.total_patients) {
                this.showError(`Cannot load more than ${this.trainingDataStats.total_patients} patients (total available)`);
                return;
            }
            
            const remainingPatients = this.trainingDataStats ? 
                this.trainingDataStats.total_patients - this.loadedTrainingPatients.length : count;
            
            if (remainingPatients <= 0) {
                this.showError('All training patients are already loaded');
                return;
            }
            
            let actualCount = count;
            if (count > remainingPatients) {
                this.showNotification(`Only ${remainingPatients} patients remain. Loading ${remainingPatients} instead.`, 'info');
                actualCount = remainingPatients;
            }
            
            this.loadMoreTrainingBtn.disabled = true;
            this.loadMoreTrainingBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i>Loading...';
            
            const response = await fetch(`/api/training/patients?limit=${actualCount}`);
            if (response.ok) {
                const newTrainingPatients = await response.json();
                
                // 合并新患者（避免重复）
                const existingIds = new Set(this.loadedTrainingPatients.map(p => p.id));
                const uniqueNewPatients = newTrainingPatients.filter(p => !existingIds.has(p.id));
                
                this.loadedTrainingPatients = [...this.loadedTrainingPatients, ...uniqueNewPatients];
                
                // 重新加载普通患者列表
                const regularResponse = await fetch('/api/patients');
                if (regularResponse.ok) {
                    const allPatients = await regularResponse.json();
                    const regularPatients = allPatients.filter(p => !p.id.startsWith('training_'));
                    this.updatePatientSelect(regularPatients, this.loadedTrainingPatients);
                }
                
                this.showSuccess(`Loaded ${uniqueNewPatients.length} new training patients`);
                
                // 清空输入框
                this.trainingLoadCount.value = '';
            } else {
                const error = await response.json();
                this.showError('Failed to load training patients: ' + error.error);
            }
        } catch (error) {
            this.showError('Failed to load training patients: ' + error.message);
        } finally {
            this.loadMoreTrainingBtn.disabled = false;
            this.loadMoreTrainingBtn.innerHTML = 'Load';
        }
    }
    
    updateTrainingDataStats() {
        this.loadedTrainingCount.textContent = this.loadedTrainingPatients.length;
        
        if (this.trainingDataStats) {
            this.totalTrainingCount.textContent = this.trainingDataStats.total_patients || '-';
            
            // 更新加载提示信息
            const loaded = this.loadedTrainingPatients.length;
            const total = this.trainingDataStats.total_patients;
            const remaining = total - loaded;
            
            if (remaining > 0) {
                this.loadingHint.textContent = `${remaining} patients remaining (${loaded}/${total} loaded)`;
                this.trainingLoadCount.placeholder = `1-${remaining}`;
                this.trainingLoadCount.max = remaining;
            } else {
                this.loadingHint.textContent = 'All patients loaded';
                this.trainingLoadCount.placeholder = 'All loaded';
            }
        } else {
            this.loadingHint.textContent = 'Enter number of patients to load';
            this.trainingLoadCount.placeholder = 'Enter count';
        }
        
        // 如果已经加载了所有患者，禁用加载按钮和输入框
        if (this.trainingDataStats && 
            this.loadedTrainingPatients.length >= this.trainingDataStats.total_patients) {
            this.loadMoreTrainingBtn.disabled = true;
            this.loadMoreTrainingBtn.textContent = 'All Loaded';
            this.trainingLoadCount.disabled = true;
        } else {
            this.loadMoreTrainingBtn.disabled = false;
            this.loadMoreTrainingBtn.textContent = 'Load';
            this.trainingLoadCount.disabled = false;
        }
    }

    showHistoryModal(history) {
        // Create modal HTML
        const modal = document.createElement('div');
        modal.id = 'historyModal';
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4';
        
        modal.innerHTML = `
            <div class="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
                <div class="px-6 py-4 border-b flex justify-between items-center">
                    <h3 class="text-lg font-semibold text-gray-900">Chat History</h3>
                    <button id="closeHistoryModal" class="text-gray-500 hover:text-gray-700">
                        <i class="fas fa-times text-xl"></i>
                    </button>
                </div>
                <div class="p-6 max-h-[60vh] overflow-y-auto">
                    <div class="space-y-4" id="historyContent">
                        ${history.map(msg => `
                            <div class="flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}">
                                <div class="max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                                    msg.type === 'user' 
                                        ? 'bg-blue-500 text-white' 
                                        : 'bg-gray-200 text-gray-800'
                                }">
                                    <div class="flex items-start space-x-2">
                                        <div class="flex-shrink-0">
                                            <i class="fas ${msg.type === 'user' ? 'fa-user' : 'fa-robot'} text-sm"></i>
                                        </div>
                                        <div class="flex-1">
                                            <div class="text-sm">${msg.content}</div>
                                            <div class="text-xs opacity-75 mt-1">${new Date(msg.timestamp).toLocaleString()}</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                <div class="px-6 py-4 border-t bg-gray-50 flex justify-between items-center">
                    <span class="text-sm text-gray-600">Total messages: ${history.length}</span>
                    <div class="space-x-2">
                        <button id="refreshHistory" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                            <i class="fas fa-sync-alt mr-2"></i>Refresh
                        </button>
                        <button id="loadHistoryToChat" class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm">
                            <i class="fas fa-comments mr-2"></i>Load to Chat
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Bind modal events
        document.getElementById('closeHistoryModal').addEventListener('click', () => {
            document.body.removeChild(modal);
        });

        document.getElementById('refreshHistory').addEventListener('click', () => {
            document.body.removeChild(modal);
            this.viewHistory();
        });

        document.getElementById('loadHistoryToChat').addEventListener('click', () => {
            this.loadChatHistory();
            document.body.removeChild(modal);
            this.showSuccess('Chat history loaded to conversation');
        });

        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
    }


}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new VirtualDiagnostician();
}); 