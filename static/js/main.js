const API_URL = "http://127.0.0.1:5000/api";
let allStartups = [];

document.addEventListener("DOMContentLoaded", () => {
    fetchStartups();
    const searchInput = document.getElementById("search");
    if (searchInput) {
        searchInput.addEventListener("input", debounce(filterStartups, 300));
    }

    const registerForm = document.getElementById('registerForm');
    const loginForm = document.getElementById('loginForm');
    
    if (registerForm) {
        registerForm.addEventListener('submit', handleFormSubmit);
    }
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleFormSubmit);
    }
});

async function fetchStartups() {
    try {
        // Default startups
        const defaultStartups = [
            ["Flipkart", "E-commerce", 2007, "₹1,60,00,00,000", "₹3,760,00,00,000", "Exited"],
            ["Paytm", "Fintech", 2010, "₹250,00,00,000", "₹5500,00,00,000", "Active"],
            ["Zomato", "Food Delivery", 2008, "₹296,00,00,000", "₹5400,00,00,000", "Active"],
            ["Ola", "Transportation", 2010, "₹320,00,00,000", "₹7300,00,00,000", "Active"],
            ["Byju's", "Edtech", 2011, "₹72,00,00,000", "₹22000,00,00,000", "Active"],
            ["Swiggy", "Food Delivery", 2014, "₹450,00,00,000", "₹10700,00,00,000", "Active"],
            ["Nykaa", "E-commerce", 2012, "₹180,00,00,000", "₹2300,00,00,000", "Active"],
            ["Dream11", "Gaming", 2008, "₹340,00,00,000", "₹8000,00,00,000", "Active"],
            ["PhonePe", "Fintech", 2015, "₹420,00,00,000", "₹12000,00,00,000", "Active"],
            ["Unacademy", "Edtech", 2015, "₹150,00,00,000", "₹3440,00,00,000", "Active"],
            ["Razorpay", "Fintech", 2014, "₹260,00,00,000", "₹7500,00,00,000", "Active"],
            ["CRED", "Fintech", 2018, "₹290,00,00,000", "₹6800,00,00,000", "Active"]
        ];

        // Fetch startups from API first
        const response = await fetch(`${API_URL}/startups`);
        const apiData = await response.json();

        // Map startup data to consistent format
        const formattedStartups = defaultStartups.map(s => ({
            name: s[0],
            industry: s[1],
            founded_year: s[2],
            total_funding: s[3],
            valuation: s[4],
            status: s[5],
            headquarters: s[6] || 'India'  // Add default location if missing
        }));

        // Combine API data with default data
        allStartups = [...formattedStartups, ...apiData];
        
        // Display startups
        displayStartups(allStartups);
    } catch (error) {
        console.error('Error fetching startups:', error);
        // Display default startups if API fails
        displayStartups(formattedStartups);
    }
}

function displayStartups(startups) {
    const tbody = document.querySelector('table tbody');
    if (!tbody) return;

    tbody.innerHTML = '';

    startups.forEach(startup => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${startup.name || 'N/A'}</td>
            <td>${startup.industry || 'N/A'}</td>
            <td>${startup.founded_year || 'N/A'}</td>
            <td>${startup.total_funding || 'N/A'}</td>
            <td>${startup.valuation || 'N/A'}</td>
            <td><span class="status-${startup.status?.toLowerCase()}">${startup.status || 'N/A'}</span></td>
            <td class="actions-cell">
                <button onclick="viewStartup('${encodeURIComponent(startup.name)}')" class="view-btn blue-view-btn">
                    View
                </button>
                <button onclick="openUpdateModal('${startup.name}', '${startup.total_funding}', '${startup.valuation}')" class="details-btn">
                    <i class="fas fa-edit"></i> Update Details
                </button>
                <button onclick="confirmDelete('${startup.name}')" class="delete-btn">
                    <i class="fas fa-trash"></i> Delete
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

async function filterStartups() {
    const searchInput = document.getElementById('search');
    const searchTerm = searchInput.value.toLowerCase().trim();
    const searchUrl = searchInput.dataset.searchUrl;
    const tbody = document.getElementById('startupList');

    try {
        const response = await fetch(`${searchUrl}?q=${encodeURIComponent(searchTerm)}`);
        const data = await response.json();

        if (!response.ok) throw new Error(data.message);

        if (data.startups.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="no-results">No startups found matching "${searchTerm}"</td>
                </tr>
            `;
            return;
        }

        displayStartups(data.startups);
    } catch (error) {
        console.error('Search error:', error);
    }
}

function viewStartup(name) {
    const decodedName = decodeURIComponent(name);
    const startup = allStartups.find(s => s.name === decodedName);
    
    if (startup) {
        document.getElementById('modalStartupName').textContent = startup.name;
        document.getElementById('modalIndustry').textContent = startup.industry;
        document.getElementById('modalFounded').textContent = startup.founded_year;
        document.getElementById('modalFunding').textContent = startup.total_funding;
        document.getElementById('modalValuation').textContent = startup.valuation;
        document.getElementById('modalStatus').textContent = startup.status;
        document.getElementById('startupModal').style.display = 'block';
    }
}

function closeModal() {
    document.getElementById('startupModal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('startupModal');
    if (event.target === modal) {
        closeModal();
    }
};

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function handleFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const isLogin = this.id === 'loginForm';
    
function confirmDelete(startupName) {
    if (confirm(`Are you sure you want to delete "${startupName}"?`)) {
        fetch('/delete_startup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify({ name: startupName })
        }).then(response => {
            if (response.ok) window.location.reload();
            else alert("Failed to delete startup.");
        });
    }
}
    // Client-side validation
    if (!formData.get('email') || !formData.get('password') || (!isLogin && !formData.get('username'))) {
        alert('Please fill in all required fields');
        return;
    }

    fetch(this.action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        },
        body: formData,
        credentials: 'same-origin'
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else if (!response.ok) {
            throw new Error(isLogin ? 'Login failed' : 'Registration failed');
        }
    })
    .catch(error => {
        alert(error.message + '. Please try again.');
    });
}