// API Base URL
const API_BASE = '/api';

function escapeHtml(value) {
    return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

// --- Navigation ---
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('main > section').forEach(sec => sec.classList.add('hidden'));
    
    // Show selected
    const selected = document.getElementById(sectionId);
    if (selected) {
        selected.classList.remove('hidden');
        
        // Auto-load data if needed
        if (sectionId === 'word-list') {
            loadWordList();
        }
    }
}

// --- Add Word Modes ---
function switchAddMode(mode) {
    const smartTab = document.getElementById('tab-smart');
    const manualTab = document.getElementById('tab-manual');
    const smartMode = document.getElementById('mode-smart');
    const manualMode = document.getElementById('add-word-form');
    
    if (mode === 'smart') {
        smartTab.className = 'px-4 py-2 text-sm font-medium text-indigo-600 border-b-2 border-indigo-600 focus:outline-none';
        manualTab.className = 'px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700 focus:outline-none';
        smartMode.classList.remove('hidden');
        manualMode.classList.add('hidden');
    } else {
        manualTab.className = 'px-4 py-2 text-sm font-medium text-indigo-600 border-b-2 border-indigo-600 focus:outline-none';
        smartTab.className = 'px-4 py-2 text-sm font-medium text-gray-500 hover:text-gray-700 focus:outline-none';
        manualMode.classList.remove('hidden');
        smartMode.classList.add('hidden');
    }
}

// --- Image Paste Handling ---
let pastedImageBase64 = null;

document.getElementById('smart-input-text').addEventListener('paste', (e) => {
    const items = (e.clipboardData || e.originalEvent.clipboardData).items;
    
    for (let index in items) {
        const item = items[index];
        if (item.kind === 'file' && item.type.startsWith('image/')) {
            const blob = item.getAsFile();
            const reader = new FileReader();
            
            reader.onload = (event) => {
                pastedImageBase64 = event.target.result; // Data URL (e.g. data:image/jpeg;base64,...)
                showImagePreview(pastedImageBase64);
            };
            
            reader.readAsDataURL(blob);
            // Don't prevent default, allow text paste as well if mixed
        }
    }
});

function showImagePreview(src) {
    const previewContainer = document.getElementById('image-preview-container');
    const previewImg = document.getElementById('pasted-image-preview');
    
    previewImg.src = src;
    previewContainer.classList.remove('hidden');
}

function clearImage() {
    pastedImageBase64 = null;
    document.getElementById('image-preview-container').classList.add('hidden');
}

// --- Analyze & Extract ---
async function analyzeText() {
    const text = document.getElementById('smart-input-text').value.trim();
    
    if (!text && !pastedImageBase64) {
        return alert('Please enter some text or paste an image first.');
    }
    
    const btnText = document.getElementById('analyze-btn-text');
    const spinner = document.getElementById('analyze-spinner');
    const previewDiv = document.getElementById('extraction-preview');
    const cardsDiv = document.getElementById('extracted-cards');
    
    btnText.textContent = 'Analyzing...';
    spinner.classList.remove('hidden');
    previewDiv.classList.add('hidden');
    cardsDiv.innerHTML = '';
    
    try {
        const payload = { text: text };
        
        // If image exists, strip the prefix "data:image/jpeg;base64," to send raw base64 or send full string depending on backend expectation
        // Backend handles "base64," check, so sending full Data URI is safer
        if (pastedImageBase64) {
            payload.image = pastedImageBase64;
        }

        const response = await fetch(`${API_BASE}/word/extract`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (response.ok && data.words && data.words.length > 0) {
            data.words.forEach((word, index) => {
                const card = document.createElement('div');
                card.className = 'bg-gray-50 p-4 rounded-lg border border-gray-200 shadow-sm';
                card.innerHTML = `
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase">Word</label>
                            <input type="text" value="${escapeHtml(word.word)}" class="w-full text-sm border-gray-300 rounded" id="word-${index}-word">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-gray-500 uppercase">Meaning</label>
                            <input type="text" value="${escapeHtml(word.meaning_you_learned)}" class="w-full text-sm border-gray-300 rounded" id="word-${index}-meaning">
                        </div>
                    </div>
                    <div class="mb-3">
                        <label class="block text-xs font-bold text-gray-500 uppercase">Scene</label>
                        <input type="text" value="${escapeHtml(word.learn_scene)}" class="w-full text-sm border-gray-300 rounded" id="word-${index}-scene">
                    </div>
                    <div class="mb-3">
                        <label class="block text-xs font-bold text-gray-500 uppercase">Usage</label>
                        <input type="text" value="${escapeHtml(word.usage_old)}" class="w-full text-sm border-gray-300 rounded" id="word-${index}-usage">
                    </div>
                    <div class="flex justify-end">
                        <button onclick="saveExtractedWord(${index})" class="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700 transition" id="btn-save-${index}">Confirm & Save</button>
                    </div>
                `;
                cardsDiv.appendChild(card);
            });
            previewDiv.classList.remove('hidden');
            
            // Clear image after successful extraction to avoid reusing it for next query
            // Keep text for reference, or user can clear it manually
            if (pastedImageBase64) {
                clearImage(); 
            }
            
        } else {
            alert('No words found. Please try describing more clearly.');
        }
    } catch (err) {
        console.error(err);
        alert('Analysis failed.');
    } finally {
        btnText.textContent = '✨ Analyze & Extract';
        spinner.classList.add('hidden');
    }
}

async function saveExtractedWord(index) {
    const btn = document.getElementById(`btn-save-${index}`);
    
    const payload = {
        word: document.getElementById(`word-${index}-word`).value,
        meaning_you_learned: document.getElementById(`word-${index}-meaning`).value,
        learn_scene: document.getElementById(`word-${index}-scene`).value,
        usage_old: document.getElementById(`word-${index}-usage`).value,
        your_note: "Added via Smart Input"
    };
    
    if (!payload.word || !payload.meaning_you_learned) {
        return alert('Word and Meaning are required.');
    }
    
    btn.textContent = 'Saving...';
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/word/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (response.ok) {
            btn.textContent = '✅ Saved';
            btn.className = 'bg-gray-400 text-white px-3 py-1 rounded text-sm cursor-not-allowed';
        } else {
            btn.textContent = '❌ Error';
            btn.disabled = false;
        }
    } catch (err) {
        console.error(err);
        btn.textContent = '❌ Error';
        btn.disabled = false;
    }
}

// --- Add Word (Manual) ---
document.getElementById('add-word-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    // Clean up empty fields
    for (let key in data) {
        if (!data[key]) delete data[key];
    }

    try {
        const response = await fetch(`${API_BASE}/word/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        const resultDiv = document.getElementById('add-result');
        resultDiv.classList.remove('hidden');
        
        if (response.ok) {
            resultDiv.className = 'mt-4 p-3 rounded-md bg-green-100 text-green-800';
            resultDiv.textContent = `✅ Saved! Word: ${data.word}`;
            form.reset();
        } else {
            resultDiv.className = 'mt-4 p-3 rounded-md bg-red-100 text-red-800';
            resultDiv.textContent = `Error: ${result.detail || 'Failed to save'}`;
        }
        
        setTimeout(() => resultDiv.classList.add('hidden'), 3000);
        
    } catch (err) {
        console.error(err);
        alert('Network error');
    }
});

// --- Retrieve Word ---
function handleEnter(e) {
    if (e.key === 'Enter') retrieveWord();
}

async function retrieveWord() {
    const query = document.getElementById('query-input').value.trim();
    if (!query) return;

    const loadingDiv = document.getElementById('retrieve-loading');
    const resultDiv = document.getElementById('retrieve-result');
    const aiContent = document.getElementById('ai-summary-content');
    const memoryList = document.getElementById('memory-list');

    // Reset UI
    loadingDiv.classList.remove('hidden');
    resultDiv.classList.add('hidden');
    aiContent.innerHTML = '';
    memoryList.innerHTML = '';

    try {
        const response = await fetch(`${API_BASE}/word/retrieve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query, top_k: 5 })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Render AI Summary
            aiContent.textContent = data.ai_summary;
            
            // Render Memories
            if (data.matches && data.matches.length > 0) {
                data.matches.forEach(mem => {
                    const div = document.createElement('div');
                    div.className = 'bg-white p-3 rounded shadow-sm text-sm border-l-4 border-indigo-400';
                    
                    // Show distance if available
                    let distanceBadge = '';
                    if (mem.distance !== undefined) {
                        // Color code distance: <1.0 Green, <1.4 Yellow, >1.4 Red
                        let colorClass = 'bg-green-100 text-green-800';
                        if (mem.distance > 1.4) colorClass = 'bg-red-100 text-red-800';
                        else if (mem.distance > 1.0) colorClass = 'bg-yellow-100 text-yellow-800';
                        
                        distanceBadge = `<span class="float-right text-xs px-2 py-0.5 rounded ${colorClass}">Dist: ${mem.distance}</span>`;
                    }
                    
                    div.innerHTML = `
                        <div class="font-bold text-gray-800">
                            ${escapeHtml(mem.word)}
                            ${distanceBadge}
                        </div>
                        <div class="text-gray-600 italic">"${escapeHtml(mem.meaning_you_learned)}"</div>
                        <div class="text-xs text-gray-400 mt-1">Scene: ${escapeHtml(mem.learn_scene)}</div>
                    `;
                    memoryList.appendChild(div);
                });
            } else {
                memoryList.innerHTML = '<p class="text-gray-500 text-sm">No direct matches found.</p>';
            }
            
            resultDiv.classList.remove('hidden');
        } else {
            alert('Error: ' + (data.detail || 'Unknown error'));
        }
    } catch (err) {
        console.error(err);
        alert('Network error');
    } finally {
        loadingDiv.classList.add('hidden');
    }
}

// --- List Words ---
async function loadWordList(page = 1) {
    const tbody = document.getElementById('vocab-table-body');
    tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4">Loading...</td></tr>';
    
    try {
        const response = await fetch(`${API_BASE}/word/list?page=${page}&size=10`);
        const data = await response.json();
        
        if (response.ok) {
            tbody.innerHTML = '';
            if (data.items.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-gray-500">No words yet. Add some!</td></tr>';
                return;
            }
            
            data.items.forEach(item => {
                // Currently WordMemory model doesn't strictly expose ID, but we assume it might be returned or we need to fix it.
                // If `item.id` or `item.record_id` is missing, the delete button won't work.
                // We will rely on the backend being updated to include IDs in the list response.
                // For now, let's try to use `item.record_id` if available, or just render the button.
                
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap font-medium text-gray-900">${escapeHtml(item.word)}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-gray-500">${escapeHtml(item.meaning_you_learned)}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-gray-500">${escapeHtml(item.learn_scene)}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-gray-500 text-sm">${escapeHtml(item.your_note || '-')}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-gray-400 text-xs">${escapeHtml(item.create_time?.split(' ')[0] || '')}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium"></td>
                `;
                const actionCell = tr.lastElementChild;
                const deleteButton = document.createElement('button');
                deleteButton.className = 'text-red-600 hover:text-red-900 ml-2';
                deleteButton.textContent = 'Delete';
                deleteButton.addEventListener('click', () => deleteWord(item.record_id || item.id || ''));
                actionCell.appendChild(deleteButton);
                tbody.appendChild(tr);
            });
            
            // ... pagination ...
            // Simple Pagination
            const paginationDiv = document.getElementById('pagination');
            const totalPages = Math.ceil(data.total / data.size);
            
            let buttons = '';
            if (page > 1) {
                buttons += `<button onclick="loadWordList(${page - 1})" class="px-3 py-1 border rounded hover:bg-gray-100">Prev</button>`;
            }
            buttons += `<span class="px-3 py-1 text-gray-600">Page ${page} of ${totalPages || 1}</span>`;
            if (page < totalPages) {
                buttons += `<button onclick="loadWordList(${page + 1})" class="px-3 py-1 border rounded hover:bg-gray-100">Next</button>`;
            }
            paginationDiv.innerHTML = buttons;
        }
    } catch (err) {
        console.error(err);
        tbody.innerHTML = '<tr><td colspan="6" class="text-center py-4 text-red-500">Failed to load data</td></tr>';
    }
}

async function deleteWord(id) {
    if (!id) {
        alert("Error: Cannot delete (Missing ID)");
        return;
    }
    
    if (!confirm("Are you sure you want to delete this word?")) return;
    
    try {
        const response = await fetch(`${API_BASE}/word/delete?record_id=${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            // Reload list
            loadWordList();
        } else {
            const data = await response.json();
            alert("Failed to delete: " + (data.detail || data.msg || "Unknown error"));
        }
    } catch (err) {
        console.error(err);
        alert("Network error during delete");
    }
}

// Init
document.addEventListener('DOMContentLoaded', () => {
    // Show Add Word by default
    showSection('add-word');
    // Ensure Smart Input is active by default
    switchAddMode('smart');
});
