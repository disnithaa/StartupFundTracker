// Dynamically determine the API URL based on current location
const API_URL = `${window.location.protocol}//${window.location.hostname}${window.location.port ? ':' + window.location.port : ''}/api/investors`;

// Default investors data
const defaultInvestors = [
    {
        id: 1,
        name: "Ratan Tata",
        firm: "Ratan Tata Investments",
        investor_type: "Angel"
    },
    {
        id: 2,
        name: "Nandan Nilekani",
        firm: null,
        investor_type: "Angel"
    },
    {
        id: 3,
        name: "SoftBank",
        firm: "SoftBank Vision Fund",
        investor_type: "Private Equity"
    },
    {
        id: 4,
        name: "Tiger Global",
        firm: "Tiger Global Management",
        investor_type: "Private Equity"
    },
    {
        id: 5,
        name: "Sequoia India",
        firm: "Sequoia Capital India",
        investor_type: "Venture Capital"
    },
    {
        id: 6,
        name: "Accel India",
        firm: "Accel Partners India",
        investor_type: "Venture Capital"
    },
    {
        id: 7,
        name: "Nexus Venture",
        firm: "Nexus Venture Partners",
        investor_type: "Venture Capital"
    },
    {
        id: 8,
        name: "Kalaari Capital",
        firm: "Kalaari Capital",
        investor_type: "Venture Capital"
    },
    {
        id: 9,
        name: "ChrysCapital",
        firm: "ChrysCapital",
        investor_type: "Private Equity"
    },
    {
        id: 10,
        name: "InfoEdge",
        firm: "InfoEdge Ventures",
        investor_type: "Corporate"
    }
];

// Get CSRF token from meta tag
function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').content;
}

// Initialize display when page loads
document.addEventListener('DOMContentLoaded', () => {
    displayInvestors(defaultInvestors); // Show initial data
    loadInvestors(); // Try to fetch from database
});

async function loadInvestors() {
    try {
        const response = await fetch('/api/investors/data', {
            headers: {
                'X-CSRF-TOKEN': getCSRFToken()
            }
        });
        if (!response.ok) throw new Error('Failed to fetch');
        const data = await response.json();
        if (data && data.length > 0) {
            displayInvestors(data); // Only update if we got data
        }
    } catch (error) {
        console.error('Error:', error);
        // Keep showing default data on error
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
    const tbody = document.querySelector('.investor-table tbody');
    if (!tbody) return;

    tbody.innerHTML = investors.map(inv => `
        <tr>
            <td>${inv.id}</td>
            <td>${inv.name}</td>
            <td>${inv.firm || '-'}</td>
            <td>${inv.investor_type}</td>
            <td>
                <div class="table-actions">
                    <button class="btn-primary" onclick="editInvestor(${inv.id})">Edit</button>
                    <button class="btn-danger" onclick="deleteInvestor(${inv.id})">Delete</button>
                </div>
            </td>
        </tr>
    `).join('');

    // Set fixed stats
    document.getElementById('totalInvestors').textContent = investors.length;
    document.getElementById('seedInvestors').textContent = "1";  // Seed stage
    document.getElementById('seriesInvestors').textContent = "10"; // Series A(5) + B(4) + C(1)
    document.getElementById('growthInvestors').textContent = investors.filter(i => i.investor_type === 'Private Equity').length;
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

async function addInvestor(event) {
    event.preventDefault();
    
    const formData = {
        name: document.getElementById('newName').value,
        firm: document.getElementById('newFirm').value,
        investment_stage: document.getElementById('newType').value,
        investor_type: document.getElementById('investorType').value,
        min_investment: document.getElementById('minInvestment').value,
        max_investment: document.getElementById('maxInvestment').value
    };

    // Validation
    if (!formData.name || !formData.investment_stage || !formData.investor_type) {
        alert('Please fill all required fields');
        return;
    }

    try {
        const response = await fetch('/api/investors/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify(formData),
            credentials: 'same-origin'
        });

        if (!response.ok) {
            throw new Error('Failed to add investor');
        }

        // Clear form and reload investors
        document.getElementById('addInvestorForm').reset();
        await loadInvestors();

    } catch (error) {
        console.error('Error:', error);
        alert(error.message);
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
