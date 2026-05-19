// Search and Autocomplete Functionality

(function() {
    const searchInput = document.getElementById('searchInput');
    const autocompleteDropdown = document.createElement('div');
    autocompleteDropdown.className = 'autocomplete-dropdown';
    autocompleteDropdown.id = 'autocompleteDropdown';
    
    if (!searchInput) return;
    
    // Wrap search box in a relative container if not already
    const searchWrapper = searchInput.parentElement;
    if (!searchWrapper.classList.contains('search-box-wrapper')) {
        searchWrapper.style.position = 'relative';
        searchWrapper.classList.add('search-box-wrapper');
    }
    searchWrapper.appendChild(autocompleteDropdown);

    let autocompleteTimeout;
    let currentFilter = 'all';

    // Autocomplete styles
    const style = document.createElement('style');
    style.textContent = `
        .search-box-wrapper {
            position: relative;
            flex: 1;
            max-width: 500px;
        }
        .autocomplete-dropdown {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 5px;
            max-height: 300px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
            margin-top: 5px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.5);
        }
        .autocomplete-item {
            padding: 12px 15px;
            cursor: pointer;
            border-bottom: 1px solid #333;
            color: white;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: background 0.2s;
        }
        .autocomplete-item:last-child {
            border-bottom: none;
        }
        .autocomplete-item:hover {
            background: #333;
        }
        .autocomplete-type {
            color: #e50914;
            font-size: 12px;
            font-weight: 600;
            padding: 2px 8px;
            background: rgba(229, 9, 20, 0.2);
            border-radius: 3px;
        }
        .autocomplete-value {
            flex: 1;
        }
    `;
    document.head.appendChild(style);

    // Filter buttons (if exist)
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            filterButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentFilter = this.dataset.filter || 'all';
            if (searchInput.value.trim().length >= 2) {
                fetchAutocomplete(searchInput.value.trim());
            }
        });
    });

    // Autocomplete on input
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        clearTimeout(autocompleteTimeout);
        
        if (query.length < 2) {
            autocompleteDropdown.style.display = 'none';
            return;
        }

        autocompleteTimeout = setTimeout(() => {
            fetchAutocomplete(query);
        }, 300);
    });

    // Show autocomplete on focus if there's text
    searchInput.addEventListener('focus', function() {
        if (this.value.trim().length >= 2) {
            fetchAutocomplete(this.value.trim());
        }
    });

    // Submit search on Enter
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            performSearch();
        } else if (e.key === 'Escape') {
            autocompleteDropdown.style.display = 'none';
        }
    });

    function fetchAutocomplete(query) {
        const autocompleteUrl = `/autocomplete/?q=${encodeURIComponent(query)}&type=${currentFilter}`;
        
        fetch(autocompleteUrl)
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                displayAutocomplete(data.suggestions || []);
            })
            .catch(error => {
                console.error('Autocomplete error:', error);
                autocompleteDropdown.style.display = 'none';
            });
    }

    function displayAutocomplete(suggestions) {
        if (!suggestions || suggestions.length === 0) {
            autocompleteDropdown.style.display = 'none';
            return;
        }

        autocompleteDropdown.innerHTML = '';
        suggestions.forEach(item => {
            const div = document.createElement('div');
            div.className = 'autocomplete-item';
            div.innerHTML = `
                <span class="autocomplete-value">${escapeHtml(item.value)}</span>
                <span class="autocomplete-type">${item.type}</span>
            `;
            div.addEventListener('click', () => {
                // If star has a URL (from Star model), navigate directly to star page
                if (item.type === 'Star' && item.url && item.id) {
                    window.location.href = item.url;
                } else {
                    // Otherwise, perform normal search
                    searchInput.value = item.value;
                    autocompleteDropdown.style.display = 'none';
                    if (item.url) {
                        window.location.href = item.url;
                    } else {
                        performSearch();
                    }
                }
            });
            autocompleteDropdown.appendChild(div);
        });
        autocompleteDropdown.style.display = 'block';
    }

    function performSearch() {
        const query = searchInput.value.trim();
        if (query) {
            const searchUrl = `/search/?q=${encodeURIComponent(query)}&filter=${currentFilter}`;
            window.location.href = searchUrl;
        }
    }

    // Close autocomplete on outside click
    document.addEventListener('click', function(e) {
        if (!searchWrapper.contains(e.target)) {
            autocompleteDropdown.style.display = 'none';
        }
    });

    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    // Make searchInput submit on button click (if search button exists)
    const searchButton = document.querySelector('.search-button');
    if (searchButton) {
        searchButton.addEventListener('click', performSearch);
    }
})();

