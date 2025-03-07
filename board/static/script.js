const username = window.location.pathname.split('/')[1];

document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card');
    const dropzones = document.querySelectorAll('.dropzone');
    
    document.getElementById("dropdown-menu").style.display = "none";

    // Drag events for cards
    cards.forEach(card => {
        card.addEventListener('dragstart', dragStart);
        card.addEventListener('dragend', dragEnd);
    });

    // Drop events for dropzones
    dropzones.forEach(dropzone => {
        dropzone.addEventListener('dragover', dragOver);
        dropzone.addEventListener('dragleave', dragLeave);
        dropzone.addEventListener('drop', drop);
    });

    // ตรวจสอบ due date ของแต่ละ card
    const dueElements = document.querySelectorAll('.due-date');
    dueElements.forEach(el => {
        const dueStr = el.dataset.due;
        if(dueStr){
            const dueDate = new Date(dueStr);
            const today = new Date();
            const diffTime = dueDate - today;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            if(diffDays < 5){
                el.style.color = "red";
            }
            else if(5 <= diffDays && diffDays <= 12){
                el.style.color = "#ccb839";
            }
            else {
                el.style.color = "green";
            }
        }
    });
    dropzones.forEach(dropzone => {
        sortCardsByRemainingTime(dropzone);
    });
});

function dragStart(e) {
    e.target.classList.add('dragging');
}

function dragEnd(e) {
    e.target.classList.remove('dragging');
}

function dragOver(e) {
    e.preventDefault();
    e.target.classList.add('drag-over');
}

function dragLeave(e) {
    e.target.classList.remove('drag-over');
}

async function drop(e) {
    e.preventDefault();
    e.target.classList.remove('drag-over');

    const card = document.querySelector('.dragging');
    const dropzone = e.target.closest('.dropzone');
    const columnId = dropzone.dataset.status;
    
    const cards = [...dropzone.querySelectorAll('.card:not(.dragging)')];
    let newOrder = cards.length;
    
    dropzone.appendChild(card);

    // Update in database (ตำแหน่ง card)
    try {
        const response = await fetch(`/${username}/update-card/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                cardId: card.dataset.id,
                columnId: columnId,
                order: newOrder
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update card position');
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function sortCardsByRemainingTime(dropzone) {
    const cards = Array.from(dropzone.querySelectorAll('.card'));
    const now = new Date();
    cards.sort((a, b) => {
        const dueA = a.dataset.due_date ? new Date(a.dataset.due_date) : null;
        const dueB = b.dataset.due_date ? new Date(b.dataset.due_date) : null;
        const diffA = dueA ? dueA - now : Infinity;
        const diffB = dueB ? dueB - now : Infinity;
        return diffA - diffB;
    });
    cards.forEach(card => dropzone.appendChild(card));
}

async function addCard(columnId) {
    const content = 'New Task';
    
    try {
        const response = await fetch(`/${username}/add-card/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                columnId: columnId,
                content: content
            })
        });

        if (!response.ok) {
            throw new Error('Failed to add card');
        }

        const data = await response.json();
        const dropzone = document.querySelector(`.dropzone[data-status="${columnId}"]`);
        
        const newCard = document.createElement('div');
        newCard.className = 'card';
        newCard.draggable = true;
        newCard.dataset.id = data.cardId;
        newCard.dataset.title = content;
        newCard.dataset.content = "";
        newCard.dataset.due_date = "";
        newCard.innerHTML = `<strong>${content}</strong><div class="due-date"></div>`;
        
        newCard.addEventListener('dragstart', dragStart);
        newCard.addEventListener('dragend', dragEnd);
        newCard.addEventListener('click', function() {
            openCardModal(newCard);
        });
        
        dropzone.appendChild(newCard);
    } catch (error) {
        console.error('Error:', error);
    }
}


function openCardModal(cardElement) {
    const modal = document.getElementById('card-modal');
    modal.style.display = "block";

    // กำหนดค่าลงในฟอร์ม modal จาก data attributes ของ card
    document.getElementById('modal-card-id').value = cardElement.dataset.id;
    document.getElementById('card-title').value = cardElement.dataset.title;
    document.getElementById('card-content').value = cardElement.dataset.content;
    document.getElementById('card-due-date').value = cardElement.dataset.due_date;

    // โหลด subtasks สำหรับ card นี้
    loadSubtasks(cardElement.dataset.id);
}

function closeCardModal() {
    const modal = document.getElementById('card-modal');
    modal.style.display = "none";
}

function toggleDropdown() {
    var dropdownMenu = document.getElementById("dropdown-menu");
    if (dropdownMenu.style.display === "block") {
        dropdownMenu.style.display = "none";
    } else {
        dropdownMenu.style.display = "block";
    }
}

document.addEventListener('click', function(event) {
    var dropdown = document.querySelector('.dropdown');
    if (dropdown && !dropdown.contains(event.target)) {
        document.getElementById("dropdown-menu").style.display = "none";
    }
});


function loadSubtasks(cardId) {
    fetch(`/${username}/get-subtasks/${cardId}/`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success'){
            const container = document.getElementById('subtasks-container');
            container.innerHTML = '';
            data.subtasks.forEach(st => {
                const div = document.createElement('div');
                div.className = 'subtask-item';
                // สร้างโครงสร้าง HTML สำหรับ subtask พร้อม checkbox, ชื่อ และไอคอนถังขยะ
                div.innerHTML = `
                    <input type="checkbox" data-subtask-id="${st.id}" ${st.completed ? 'checked' : ''} onchange="toggleSubtask(this)">
                    <span class="subtask-title ${st.completed ? 'completed' : ''}">${st.title}</span>
                    <span class="delete-subtask-icon" onclick="deleteSubtask(${st.id})">&#128465;</span>
                `;
                container.appendChild(div);
            });
        } else {
            console.error(data.message);
        }
    })
    .catch(error => console.error('Error loading subtasks:', error));
}



function deleteSubtask(subtaskId) {
    if(confirm("คุณแน่ใจหรือไม่ที่จะลบ subtask นี้?")) {
        fetch(`/${username}/delete-subtask/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ subtaskId: subtaskId })
        })
        .then(response => response.json())
        .then(data => {
            if(data.status === 'success'){
                const cardId = document.getElementById('modal-card-id').value;
                loadSubtasks(cardId);
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error deleting subtask:', error));
    }
}


function addSubtask() {
    const cardId = document.getElementById('modal-card-id').value;
    const input = document.getElementById('new-subtask-input');
    const title = input.value.trim();
    if(!title){
        alert("Please enter subtask title");
        return;
    }
    fetch(`/${username}/add-subtask/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            cardId: cardId,
            title: title
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success'){
            // Reload subtasks
            loadSubtasks(cardId);
            input.value = '';
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error('Error adding subtask:', error));
}


function handleSubtaskButtonClick() {
    const input = document.getElementById('new-subtask-input');
    const button = document.getElementById('add-subtask-btn');

    if (input.style.display === 'none' || input.style.display === '') {
        input.style.display = 'block';
        input.focus();
        button.textContent = 'Save';
    } else {
        const cardId = document.getElementById('modal-card-id').value;
        const title = input.value.trim();
        if (!title) {
            alert("Please enter subtask title");
            return;
        }
        fetch(`/${username}/add-subtask/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                cardId: cardId,
                title: title
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                loadSubtasks(cardId);
                input.value = '';
                input.style.display = 'none';
                button.textContent = 'Add Subtask';
            } else {
                alert(data.message);
            }
        })
        .catch(error => console.error('Error adding subtask:', error));
    }
}


function toggleSubtask(checkbox) {
    const subtaskId = checkbox.dataset.subtaskId;
    const completed = checkbox.checked;
    fetch(`/${username}/toggle-subtask/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            subtaskId: subtaskId,
            completed: completed
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.status === 'success'){
            const span = checkbox.nextElementSibling;
            if(completed){
                span.style.textDecoration = 'line-through';
            } else {
                span.style.textDecoration = 'none';
            }
        } else {
            alert(data.message);
        }
    })
    .catch(error => console.error('Error toggling subtask:', error));
}


async function saveCardChanges() {
    const cardId = document.getElementById('modal-card-id').value;
    const title = document.getElementById('card-title').value;
    const content = document.getElementById('card-content').value;
    const dueDate = document.getElementById('card-due-date').value;

    try {
        const response = await fetch(`/${username}/edit-card/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                cardId: cardId,
                title: title,
                content: content,
                dueDate: dueDate
            })
        });
        const result = await response.json();
        if(result.status === "success"){
            const cardElement = document.querySelector(`.card[data-id="${cardId}"]`);
            cardElement.dataset.title = title;
            cardElement.dataset.content = content;
            cardElement.dataset.due_date = dueDate;
            cardElement.innerHTML = `<strong>${title}</strong><div class="due-date" data-due="${dueDate}">${ dueDate ? "Due: " + dueDate : "" }</div>`;

            const dueEl = cardElement.querySelector('.due-date');
            if(dueDate){
                const dueDt = new Date(dueDate);
                const today = new Date();
                const diffTime = dueDt - today;
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                if(diffDays < 5){
                    dueEl.style.color = "red";
                } 
                else if(5 <= diffDays && diffDays <= 12){
                    dueEl.style.color = "#ccb839";
                }
                else {
                    dueEl.style.color = "green";
                }
            }
            closeCardModal();
        } else {
            alert("Error: " + result.message);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

async function deleteCard() {
    const cardId = document.getElementById('modal-card-id').value;
    try {
        const response = await fetch(`/${username}/delete-card/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                cardId: cardId
            })
        });
        const result = await response.json();
        if(result.status === "success"){

            const cardElement = document.querySelector(`.card[data-id="${cardId}"]`);
            cardElement.parentNode.removeChild(cardElement);
            closeCardModal();
        } else {
            alert("Error: " + result.message);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
