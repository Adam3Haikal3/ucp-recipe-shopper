const input = document.getElementById('recipeInput');
const btn = document.getElementById('shopBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const productsGrid = document.getElementById('productsGrid');
const itemCount = document.getElementById('itemCount');
const totalCost = document.getElementById('totalCost');
const missingSection = document.getElementById('missingSection');
const missingList = document.getElementById('missingList');

const AGENT_API = "http://localhost:8000/api/shop";

btn.addEventListener('click', async () => {
    const recipe = input.value.trim();
    if (!recipe) return;

    // UI Reset
    results.classList.add('hidden');
    missingSection.classList.add('hidden');
    productsGrid.innerHTML = '';
    missingList.innerHTML = '';
    loading.classList.remove('hidden');

    try {
        const response = await fetch(AGENT_API, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ recipe })
        });

        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        const data = await response.json();
        renderResults(data);

    } catch (error) {
        alert("Failed to connect to UCP Agent: " + error.message);
    } finally {
        loading.classList.add('hidden');
    }
});

function renderResults(data) {
    results.classList.remove('hidden');

    // Update Summary
    itemCount.textContent = data.items_found.length;
    // Price is in cents, convert to dollars
    totalCost.textContent = `$${(data.total_cost / 100).toFixed(2)}`;

    // Render Products
    data.items_found.forEach(product => {
        const card = document.createElement('div');
        card.className = 'product-card';
        card.innerHTML = `
            <div class="product-image"></div> <!-- Placeholder for image -->
            <div class="product-title">${product.title}</div>
            <div class="product-price">$${(product.price / 100).toFixed(2)}</div>
            <div class="product-source">Found at ${product.source}</div>
        `;
        productsGrid.appendChild(card);
    });

    // Render Missing
    if (data.missing_items.length > 0) {
        missingSection.classList.remove('hidden');
        data.missing_items.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            missingList.appendChild(li);
        });
    }
}
