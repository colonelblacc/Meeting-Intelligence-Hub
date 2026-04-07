// Initialize Lucide Icons
lucide.createIcons();

// DOM Elements
const uploadView = document.getElementById('upload-view');
const dashboardView = document.getElementById('dashboard-view');
const chatView = document.getElementById('chat-view');

const navDashboard = document.getElementById('nav-dashboard');
const navChat = document.getElementById('nav-chat');

const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const uploadProgress = document.getElementById('upload-progress');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const progressValue = document.getElementById('progress-value');

// Mock Data
let decisions = [];
let actionItems = [];
let currentContext = {};

// Navigation logic
function switchView(viewId) {
    [uploadView, dashboardView, chatView].forEach(view => view.classList.add('hidden'));
    document.getElementById(viewId).classList.remove('hidden');
    
    // Update nav active states
    document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
    
    if (viewId === 'dashboard-view' || viewId === 'upload-view') {
        navDashboard.classList.add('active');
    } else if (viewId === 'chat-view') {
        navChat.classList.add('active');
    }
}

navDashboard.addEventListener('click', (e) => {
    e.preventDefault();
    if(decisions.length > 0 || actionItems.length > 0) {
        switchView('dashboard-view');
    } else {
        switchView('upload-view');
    }
});

navChat.addEventListener('click', (e) => {
    e.preventDefault();
    switchView('chat-view');
});


// File Upload Logic
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => dropzone.classList.add('drag-active'), false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => dropzone.classList.remove('drag-active'), false);
});

dropzone.addEventListener('drop', handleDrop, false);
fileInput.addEventListener('change', (e) => handleFiles(e.target.files));

function handleDrop(e) {
    let dt = e.dataTransfer;
    let files = dt.files;
    handleFiles(files);
}

function handleFiles(files) {
    if (files.length > 0) {
        uploadFile(files[0]);
    }
}

async function uploadFile(file) {
    // Show progress UI Replace upload button with progress
    dropzone.querySelector('h3').innerText = 'Processing ' + file.name;
    dropzone.querySelector('p').classList.add('hidden');
    dropzone.querySelector('.btn-primary').classList.add('hidden');
    dropzone.querySelector('.upload-icon').setAttribute('data-lucide', 'loader-2');
    dropzone.querySelector('.upload-icon').classList.add('lucide-spin');
    
    uploadProgress.classList.remove('hidden');
    progressFill.style.width = '50%';
    progressValue.innerText = '50%';
    progressText.innerText = "Analyzing meeting content with Gemini...";
    
    const formData = new FormData();
    formData.append('file', file);
    
    const attendeesVal = document.getElementById('attendees-input').value.trim();
    if (attendeesVal) {
        formData.append('attendees', attendeesVal);
    }
    
    try {
        const response = await fetch('/api/v1/transcripts/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            progressFill.style.width = '100%';
            progressValue.innerText = '100%';
            progressText.innerText = "Complete!";
            
            setTimeout(() => {
                const data = result.data || { decisions: [], actionItems: [] };
                currentContext = data;
                decisions = data.decisions || [];
                actionItems = data.actionItems || [];
                
                renderDashboard();
                switchView('dashboard-view');
                
                // Reset upload view
                dropzone.querySelector('h3').innerText = 'Drag & drop media or transcript here';
                dropzone.querySelector('p').classList.remove('hidden');
                dropzone.querySelector('.btn-primary').classList.remove('hidden');
                uploadProgress.classList.add('hidden');
            }, 500);
        } else {
            throw new Error(result.detail || 'Upload failed');
        }
    } catch (e) {
        alert("Failed to process file: " + e.message);
        // Reset UI
        dropzone.querySelector('h3').innerText = 'Drag & drop media or transcript here';
        dropzone.querySelector('p').classList.remove('hidden');
        dropzone.querySelector('.btn-primary').classList.remove('hidden');
        uploadProgress.classList.add('hidden');
    }
}

// Dashboard Rendering
function renderDashboard() {
    document.getElementById('decisions-count').innerText = decisions.length;
    document.getElementById('actions-count').innerText = actionItems.length;
    
    const decList = document.getElementById('decisions-list');
    decList.innerHTML = decisions.map(d => `
        <li class="data-item">
            <div class="title">${d.title}</div>
            <div class="desc">${d.desc}</div>
            <div class="meta"><span>Mentioned by: ${d.author}</span></div>
        </li>
    `).join('');
    
    const actList = document.getElementById('actions-list');
    actList.innerHTML = actionItems.map(a => `
        <li class="data-item">
            <div class="title">${a.title}</div>
            <div class="desc">${a.desc}</div>
            <div class="meta">
                <span>Assigned to: ${a.assignee}</span>
                <span class="action-status status-${a.status}">${a.status.toUpperCase()}</span>
            </div>
        </li>
    `).join('');
}

// Chat Logic
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatMessages = document.getElementById('chat-messages');

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if(!msg) return;
    
    // Add user message
    appendMessage(msg, 'user');
    chatInput.value = '';
    
    // Fetch response
    try {
        const response = await fetch('/api/v1/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ message: msg, context: currentContext })
        });
        const result = await response.json();
        appendMessage(result.reply || "No response received.", 'assistant');
    } catch (err) {
        appendMessage("Sorry, I couldn't reach the backend.", 'assistant');
    }
});

function appendMessage(text, role) {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    
    const icon = role === 'user' ? 'user' : 'bot';
    
    div.innerHTML = `
        <div class="avatar"><i data-lucide="${icon}"></i></div>
        <div class="message-content">${text}</div>
    `;
    
    chatMessages.appendChild(div);
    lucide.createIcons({ root: div });
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
