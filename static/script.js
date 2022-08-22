API_URL = '/api'

async function addClap(id) {
    const response = await fetch(`${API_URL}/messages/${id}/claps`, {
        method: 'POST',
        credentials: 'include', 
    });
    if (response.ok) {
        const clapsCount = await response.json();
        return clapsCount.claps;
    } else {
        alert('опаньки...');
    }
}

async function handleClapFormSubmit(e) {
    e.preventDefault();
    const clapForm = e.target;
    const message_id = +clapForm.querySelector('[name="message_id"]').value;

    const button = clapForm.querySelector('.btn');
    button.disabled = true;
    const clapsCount = await addClap(message_id);
    button.disabled = false;

    const span = button.querySelector('.clap-span');
    span.textContent = clapsCount;
}

async function addMessage(message) {
    const response = await fetch(`${API_URL}/messages`, {
        method: 'POST',
        credentials: 'include', 
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(message)
    });

    return [response.ok, await response.json()];
}

async function handleSendFormSubmit(e) {
    e.preventDefault();
    const sendForm = e.target;
    const message = {
        author: sendForm.querySelector('[name="sender"]').value,
        message: sendForm.querySelector('[name="message"]').value
    };

    document.querySelector('#error-alert').style.display = 'none';
    document.querySelector('#success-alert').style.display = 'none';

    document.getElementById('sendButton').disabled = true;
    sendForm.querySelector('[name="sender"]').disabled = true;
    sendForm.querySelector('[name="message"]').disabled = true;

    document.querySelector('#loading-alert').style.display = 'inline';

    const [ok, newMessage] = await addMessage(message);

    if (ok) {

        const template = document.querySelector('#message-template');
        const newMessageNode = template.content.firstElementChild.cloneNode(true);

        //works
        const author = newMessageNode.querySelector('.text-muted');
        author.textContent = newMessage.author;

        //it just works
        const link = newMessageNode.querySelector('[id="message-link"]');
        link.href = link.href.replace('MESSAGE_ID', newMessage.id);

        //works
        const messageText = newMessageNode.querySelector('.card-text');
        messageText.textContent = newMessage.message;

        //works
        const idInput = newMessageNode.querySelector('[name="message_id"]');
        idInput.value = newMessage.id;

        //works
        const span = newMessageNode.querySelector('.clap-span');
        span.textContent = newMessage.claps;

        document.querySelector('.list-unstyled').appendChild(newMessageNode);
        
        document.querySelector('#loading-alert').style.display = 'none';
        document.querySelector('#success-alert').style.display = 'inline';
    } else {
        document.querySelector('#loading-alert').style.display = 'none';
        const errorNode = document.querySelector('#error-alert');
        errorNode.style.display = 'inline';
        errorNode.querySelector('#error-text').textContent = newMessage.message;
    }

    document.getElementById('sendButton').disabled = false;
    sendForm.querySelector('[name="sender"]').disabled = false;
    sendForm.querySelector('[name="message"]').disabled = false;
}

function init() {
    const clapForms = document.querySelector('ul.list-unstyled');
    clapForms.addEventListener('submit', handleClapFormSubmit);

    const sendForm = document.getElementById('sendForm');
    sendForm.addEventListener('submit', handleSendFormSubmit);    
}

init();