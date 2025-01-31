const username = window.location.pathname.split('/')[1];

document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.card');
    const dropzones = document.querySelectorAll('.dropzone');

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
    
    // Get the new position
    const cards = [...dropzone.querySelectorAll('.card:not(.dragging)')];
    let newOrder = cards.length;
    
    dropzone.appendChild(card);

    // Update in database
    try {
        const response = await fetch(`/${username}/update-card/` , {
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

async function addCard(columnId) {
    const content = 'New Task';
    
    try {
        const response = await fetch(`/${username}/add-card/` , {
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
        newCard.contentEditable = true;
        newCard.dataset.id = data.cardId;
        newCard.textContent = content;
        
        newCard.addEventListener('dragstart', dragStart);
        newCard.addEventListener('dragend', dragEnd);
        
        dropzone.appendChild(newCard);
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