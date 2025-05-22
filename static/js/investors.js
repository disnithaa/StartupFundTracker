// Dynamically determine the API URL based on current location
const API_URL = `${window.location.protocol}//${window.location.hostname}${window.location.port ? ':' + window.location.port : ''}/api/investors`;

// Load investors when page loads
document.addEventListener('DOMContentLoaded', loadInvestors);

async function loadInvestors() {
    try {
        const response = await fetch(API_URL);
        const investors = await response.json();
        displayInvestors(investors);
    } catch (error) {
        console.error('Error loading investors:', error);
    }
}

function updateDashboardStats(investors) {
    const totalInvestors = investors.length;
    const seedInvestors = investors.filter(inv => inv.investment_stage === 'Seed').length;
    const seriesInvestors = investors.filter(inv => 
        ['Series A', 'Series B', 'Series C'].includes(inv.investment_stage)
    ).length;
    const growthInvestors = investors.filter(inv => inv.investment_stage === 'Growth').length;

    document.getElementById('totalInvestors').textContent = totalInvestors;
    document.getElementById('seedInvestors').textContent = seedInvestors;
    document.getElementById('seriesInvestors').textContent = seriesInvestors;
    document.getElementById('growthInvestors').textContent = growthInvestors;
}

function displayInvestors(investors) {
    // Update dashboard stats
    updateDashboardStats(investors);
    
    const grid = document.getElementById('investorsGrid');
    grid.innerHTML = '';
    
    investors.forEach(investor => {
        const card = document.createElement('div');
        card.className = 'investor-card';
        
        // Format investment range
        const minInvestment = formatCurrency(investor.min_investment);
        const maxInvestment = formatCurrency(investor.max_investment);
        const investmentRange = `${minInvestment} - ${maxInvestment}`;
        
        card.innerHTML = `
            <h3>${investor.name}</h3>
            <p><strong>Firm:</strong> ${investor.firm || '-'}</p>
            <p><strong>Type:</strong> ${investor.investor_type || '-'}</p>
            <p><strong>Stage:</strong> ${investor.investment_stage}</p>
            <p><strong>Investment Range:</strong> ${investmentRange}</p>
            <div class="card-actions">
                <button onclick="editInvestor(${investor.id})" class="btn-primary">Edit</button>
                <button onclick="deleteInvestor(${investor.id})" class="btn-danger">Delete</button>
            </div>
        `;
        grid.appendChild(card);
    });
}

// Helper function to format currency in Indian format
function formatCurrency(amount) {
    if (!amount) return '₹0';
    
    // Convert to number if it's a string
    const num = typeof amount === 'string' ? parseFloat(amount) : amount;
    
    // Format in Indian currency system (with lakhs and crores)
    const formatter = new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    });
    
    return formatter.format(num);
}

async function addInvestor() {
    const name = document.getElementById('newName').value;
    const firm = document.getElementById('newFirm').value;
    const investment_stage = document.getElementById('newType').value;
    const investor_type = document.getElementById('investorType').value;
    const min_investment = document.getElementById('minInvestment').value;
    const max_investment = document.getElementById('maxInvestment').value;
    
    if (!name || !investment_stage || !investor_type || !min_investment || !max_investment) {
        alert('Please fill in all required fields');
        return;
    }

    if (parseFloat(min_investment) > parseFloat(max_investment)) {
        alert('Minimum investment cannot be greater than maximum investment');
        return;
    }
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name,
                firm,
                investment_stage,
                investor_type,
                min_investment: parseFloat(min_investment),
                max_investment: parseFloat(max_investment)
            })
        });
        
        if (response.ok) {
            loadInvestors();
            // Clear form
            document.getElementById('newName').value = '';
            document.getElementById('newFirm').value = '';
            document.getElementById('newType').value = '';
            document.getElementById('investorType').value = '';
            document.getElementById('minInvestment').value = '';
            document.getElementById('maxInvestment').value = '';
        } else {
            alert('Error adding investor');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error adding investor');
    }
}

async function deleteInvestor(id) {
    if (!confirm('Are you sure you want to delete this investor?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadInvestors();
        } else {
            alert('Error deleting investor');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error deleting investor');
    }
}

async function searchInvestors() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const typeFilter = document.getElementById('typeFilter').value;
    
    try {
        let response;
        if (searchTerm || typeFilter) {
            const url = new URL(`${API_URL}/search`);
            if (searchTerm) url.searchParams.append('term', searchTerm);
            if (typeFilter) url.searchParams.append('type', typeFilter);
            response = await fetch(url);
        } else {
            response = await fetch(API_URL);
        }
        
        const investors = await response.json();
        displayInvestors(investors);
    } catch (error) {
        console.error('Error searching investors:', error);
    }
}
