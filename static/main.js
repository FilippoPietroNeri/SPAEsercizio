document.addEventListener('DOMContentLoaded', () => {
    populateDropdown('/api/aule', 'AulaID');
    populateDropdown('/api/docenti', 'DocenteID');
    populateDropdown('/api/seminari', 'SeminariID');
    updateUI();
});

function isLoggedIn() {
    return !!localStorage.getItem('token');
}

function updateUI() {
    const isLogged = isLoggedIn();

    document.getElementById('form-login-docente').style.display = isLogged ? 'none' : 'block';
    document.getElementById('logout-button').style.display = isLogged ? 'inline-block' : 'none';

    const prenotazioneSection = document.getElementById('seminario-prenotazione-section');
    const protectedMessage = document.getElementById('protected-message');

    if (isLogged) {
        prenotazioneSection.classList.remove('hidden');
        protectedMessage.style.display = 'none';
    } else {
        prenotazioneSection.classList.add('hidden');
        protectedMessage.style.display = 'block';
    }
}

function getDataToShow(select)
{
    let data;
    switch (select) {
        case 'DocenteID':
            data = 'Email'
            break;

        case 'SeminariID':
            data = 'Titolo'
            break;

        default:
            data = 'ID'
            break;
    }
    return data
}

async function populateDropdown(endpoint, selectId) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const data = await response.json();
        const select = document.getElementById(selectId);
        select.innerHTML = data.map(item => `<option value="${item.ID}">[${item.ID}] ${item[getDataToShow(selectId)]}</option>`).join('');
    } catch (error) {
        console.error(`Errore nel popolare il menu a tendina: ${error.message}`);
    }
}

async function OldfetchData(endpoint, outputId) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const data = await response.json();
        document.getElementById(outputId).textContent = JSON.stringify(data, null, 2);
    } catch (error) {
        document.getElementById(outputId).textContent = `C'è stato un errore durante la fetch!`;
    }
}

async function fetchData(endpoint, outputId) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const data = await response.json();

        const table = document.createElement('table');
        table.style.borderCollapse = 'collapse';
        table.style.width = '100%';

        const thead = document.createElement('thead');
        const headers = Object.keys(data[0] || {});
        const headerRow = document.createElement('tr');
        headers.forEach(header => {
            const th = document.createElement('th');
            th.textContent = header;
            th.style.border = '1px solid black';
            th.style.padding = '8px';
            th.style.textAlign = 'left';
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        data.forEach(row => {
            const tr = document.createElement('tr');
            headers.forEach(header => {
                const td = document.createElement('td');
                td.textContent = row[header];
                td.style.border = '1px solid black';
                td.style.padding = '8px';
                tr.appendChild(td);
            });
            tbody.appendChild(tr);
        });
        table.appendChild(tbody);

        const outputElement = document.getElementById(outputId);
        outputElement.innerHTML = '';
        outputElement.appendChild(table);
    } catch (error) {
        document.getElementById(outputId).textContent = `Error: ${error.message}`;
    }
}


async function submitForm(endpoint, formId, outputId) {
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());

    const documentEl = document.getElementById(outputId);
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        const result = await response.json();
        documentEl.textContent = JSON.stringify(result, null, 2);
        documentEl.style.color = response.ok ? 'green' : 'red'
    } catch (error) {
        documentEl.textContent = `Error: ${error.message}`;
        documentEl.style.color = 'red'
    }
}

function handleLogin() {
    const formData = new FormData(document.getElementById('form-login-docente'));
    fetch('/api/login', {
        method: 'POST',
        body: JSON.stringify(Object.fromEntries(formData)),
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(data => {
            console.log(data)
            if (data.success) {
                localStorage.setItem('token', data.token);
                updateUI();
                document.getElementById('output-login').textContent = 'Login riuscito!';
            } else {
                document.getElementById('output-login').textContent = 'Errore: ' + data.message;
            }
        });
}

function handleLogout() {
    localStorage.removeItem('token');
    updateUI();
}