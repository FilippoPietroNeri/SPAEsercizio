document.addEventListener('DOMContentLoaded', () => {
    populateDropdown('/api/aule', 'AulaID');
    populateDropdown('/api/docenti', 'DocenteID');
});

async function populateDropdown(endpoint, selectId) {
    try {
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const data = await response.json();
        const select = document.getElementById(selectId);
        select.innerHTML = data.map(item => `<option value="${item.ID}">${item.ID}</option>`).join('');
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
        document.getElementById(outputId).textContent = `Error: ${error.message}`;
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
        documentEl.style.color = response.status == 200 ? 'green' : 'red'
    } catch (error) {
        document.getElementById(outputId).textContent = `Error: ${error.message}`;
    }
}
