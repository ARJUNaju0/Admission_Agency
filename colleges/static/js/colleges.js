// college-list.js

const API_URL = 'http://127.0.0.1:8000/api'; // Adjust to your backend URL

// State Management
const state = {
    colleges: [],
    loading: true,
    filters: {
        city: [],
        type: []
    },
    compareList: []
};

// DOM Elements
const collegeGrid = document.getElementById('college-grid');
const loadingSpinner = document.getElementById('loading');
const emptyState = document.getElementById('empty-state');
const compareBar = document.getElementById('compare-bar');
const compareCountSpan = document.getElementById('compare-count');
const compareActionBtn = document.getElementById('btn-compare-action');
const clearFiltersBtn = document.getElementById('clear-filters');

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    fetchColleges();
    setupEventListeners();
});

// --- Fetch Data ---
async function fetchColleges() {
    state.loading = true;
    updateUI();

    try {
        // Build Query String based on filters
        const params = new URLSearchParams();
        if (state.filters.city.length > 0) params.append('city', state.filters.city[0]); 
        if (state.filters.type.length > 0) params.append('college_type', state.filters.type[0]);

        // FETCH Request
        const response = await fetch(`${API_URL}/colleges/?${params.toString()}`);
        
        if (!response.ok) throw new Error('Network response was not ok');
        
        state.colleges = await response.json();
    } catch (error) {
        console.error("Error fetching colleges:", error);
        // Fallback dummy data if API fails (for demonstration)
        state.colleges = getDummyData(); 
    } finally {
        state.loading = false;
        updateUI();
    }
}

// --- Rendering ---
function updateUI() {
    // 1. Toggle Loading
    if (state.loading) {
        loadingSpinner.classList.remove('hidden');
        collegeGrid.innerHTML = '';
        return;
    }
    loadingSpinner.classList.add('hidden');

    // 2. Check Empty State
    if (state.colleges.length === 0) {
        emptyState.classList.remove('hidden');
        collegeGrid.innerHTML = '';
        return;
    }
    emptyState.classList.add('hidden');

    // 3. Render Cards
    collegeGrid.innerHTML = state.colleges.map(college => createCollegeCard(college)).join('');
    
    // 4. Update Compare Bar
    updateCompareBar();
}

function createCollegeCard(college) {
    const isChecked = state.compareList.includes(college.id);
    const isDisabled = !isChecked && state.compareList.length >= 4;

    return `
        <div class="flex flex-col md:flex-row bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-all group">
            
            <div class="md:w-80 h-48 md:h-auto relative overflow-hidden bg-gray-200">
                <img src="${college.hero_image || 'https://images.unsplash.com/photo-1562774053-701939374585?q=80&w=1000&auto=format&fit=crop'}" 
                     alt="${college.name}" 
                     class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
                ${college.nirf_rank ? `<div class="absolute top-4 right-4 bg-primary text-white px-3 py-1 rounded-md text-sm font-semibold">NIRF #${college.nirf_rank}</div>` : ''}
            </div>

            <div class="flex-1 p-6">
                <div class="flex items-start justify-between mb-4">
                    <div>
                        <h3 class="text-2xl font-serif font-medium mb-2 text-primary">${college.name}</h3>
                        <p class="text-sm text-gray-500 flex items-center gap-1">
                            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                            ${college.city}
                        </p>
                    </div>
                    
                    <div class="flex items-center">
                        <input type="checkbox" 
                               class="compare-checkbox w-5 h-5 rounded border-gray-300 text-secondary focus:ring-secondary cursor-pointer"
                               data-id="${college.id}"
                               ${isChecked ? 'checked' : ''}
                               ${isDisabled ? 'disabled' : ''}>
                    </div>
                </div>

                <p class="text-sm text-gray-500 mb-4 line-clamp-2">${college.description || 'No description available.'}</p>

                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
                    <div>
                        <p class="text-xs text-gray-400 uppercase">Type</p>
                        <p class="font-medium">${college.institution_type}</p>
                    </div>
                    <div>
                        <p class="text-xs text-gray-400 uppercase">Avg Package</p>
                        <p class="font-medium">₹${college.avg_package} LPA</p>
                    </div>
                    <div>
                        <p class="text-xs text-gray-400 uppercase">Fees</p>
                        <p class="font-medium">₹8-12 L</p>
                    </div>
                    <div>
                        <p class="text-xs text-gray-400 uppercase">Placement</p>
                        <p class="font-medium flex items-center gap-1 text-green-700">
                            <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                            ${college.placement_rate}%
                        </p>
                    </div>
                </div>

                <a href="/colleges/${college.id}" class="inline-block bg-primary text-white px-4 py-2 rounded hover:bg-opacity-90 transition text-sm font-bold">
                    View Details
                </a>
            </div>
        </div>
    `;
}

function updateCompareBar() {
    const count = state.compareList.length;
    
    if (count > 0) {
        compareBar.classList.remove('hidden');
        compareCountSpan.innerText = count;
        
        // Enable button if 2 or more selected
        if (count >= 2) {
            compareActionBtn.disabled = false;
            compareActionBtn.classList.remove('opacity-50', 'cursor-not-allowed');
        } else {
            compareActionBtn.disabled = true;
            compareActionBtn.classList.add('opacity-50', 'cursor-not-allowed');
        }
    } else {
        compareBar.classList.add('hidden');
    }

    // Re-bind checkbox events since HTML was overwritten
    bindCheckboxEvents();
}

// --- Event Listeners ---
function setupEventListeners() {
    // City Checkboxes
    document.querySelectorAll('.filter-city').forEach(cb => {
        cb.addEventListener('change', (e) => {
            // Logic: only one city allowed at a time (per original code logic) or toggle logic
            if (e.target.checked) {
                state.filters.city = [e.target.value];
                // Uncheck others
                document.querySelectorAll('.filter-city').forEach(c => {
                    if(c !== e.target) c.checked = false;
                });
            } else {
                state.filters.city = [];
            }
            fetchColleges();
        });
    });

    // Type Checkboxes
    document.querySelectorAll('.filter-type').forEach(cb => {
        cb.addEventListener('change', (e) => {
            if (e.target.checked) {
                state.filters.type = [e.target.value];
                document.querySelectorAll('.filter-type').forEach(c => {
                    if(c !== e.target) c.checked = false;
                });
            } else {
                state.filters.type = [];
            }
            fetchColleges();
        });
    });

    // Clear Filters
    clearFiltersBtn.addEventListener('click', () => {
        state.filters.city = [];
        state.filters.type = [];
        // Uncheck all UI inputs
        document.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
        fetchColleges();
    });

    // Compare Action
    compareActionBtn.addEventListener('click', () => {
        if (state.compareList.length >= 2) {
            window.location.href = `/compare?ids=${state.compareList.join(',')}`;
        }
    });
}

function bindCheckboxEvents() {
    document.querySelectorAll('.compare-checkbox').forEach(cb => {
        cb.addEventListener('change', (e) => {
            const id = parseInt(e.target.dataset.id);
            
            if (e.target.checked) {
                if (state.compareList.length < 4) {
                    state.compareList.push(id);
                }
            } else {
                state.compareList = state.compareList.filter(item => item !== id);
            }
            
            // Re-render UI to update disabled states
            updateUI(); 
        });
    });
}

// --- Dummy Data Fallback (If API fails) ---
function getDummyData() {
    return [
        {
            id: 1,
            name: "Indian Institute of Science",
            city: "Bengaluru",
            institution_type: "Research",
            nirf_rank: 2,
            avg_package: 28.5,
            placement_rate: 98,
            description: "India's premier institute for advanced scientific and technological research and education."
        },
        {
            id: 2,
            name: "RV College of Engineering",
            city: "Bengaluru",
            institution_type: "Engineering",
            nirf_rank: 89,
            avg_package: 12.5,
            placement_rate: 92,
            description: "Autonomous institution affiliated to Visvesvaraya Technological University."
        }
    ];
}