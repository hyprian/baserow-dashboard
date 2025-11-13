// static/js/script.js

document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('dashboard-container');
    const timestampEl = document.getElementById('timestamp');
    const loader = document.getElementById('loader'); // Get the loader

    async function fetchData() {
        // Show loader before starting the fetch
        loader.style.display = 'flex'; 
        
        try {
            const response = await fetch('/api/data');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            container.innerHTML = '';

            if (data.error) {
                 container.innerHTML = `<p class="error">${data.error}</p>`;
                 return;
            }

            data.forEach(group => {
                const groupSection = document.createElement('section');
                groupSection.className = 'data-group';
                groupSection.innerHTML = `<h2 class="group-title">${group.group_name}</h2>`;
                const grid = document.createElement('div');
                grid.className = 'dashboard-grid';

                group.tables.forEach(table => {
                    const card = document.createElement('div');
                    card.className = 'card';
                    const footerHTML = table.last_updated
                        ? `<div class="card-footer">Last Push: ${table.last_updated}</div>`
                        : '';
                    card.innerHTML = `
                        <div>
                            <div class="card-header"><h2>${table.table_name}</h2></div>
                            <div class="date-range">
                                <div class="min-date">
                                    <span class="date-label">From</span>
                                    <p class="date-value">${table.min_date}</p>
                                </div>
                                <div class="max-date">
                                    <span class="date-label">To</span>
                                    <p class="date-value">${table.max_date}</p>
                                </div>
                            </div>
                        </div>
                        ${footerHTML}`;
                    grid.appendChild(card);
                });

                groupSection.appendChild(grid);
                container.appendChild(groupSection);
            });
            
            timestampEl.textContent = new Date().toLocaleString();

        } catch (error) {
            container.innerHTML = `<p class="error">Failed to load data. Check the console for details.</p>`;
            console.error('Error fetching dashboard data:', error);
        } finally {
            // Hide loader after the try/catch is complete
            loader.style.display = 'none';
        }
    }

    fetchData();
    setInterval(fetchData, 300000); 
});