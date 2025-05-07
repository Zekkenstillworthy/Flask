// Score viewer functionality
document.addEventListener('DOMContentLoaded', function() {
    // Get all view-scores-btn elements
    const viewScoreBtns = document.querySelectorAll('.view-scores-btn');
    const backToUsersBtn = document.getElementById('back-to-users');
    const usersView = document.getElementById('users-view');
    const userScoresView = document.getElementById('user-scores-view');
    const allScoresView = document.getElementById('all-scores-view');
    const usernameDisplay = document.getElementById('username-display');
    
    // Add click event to each view scores button
    if (viewScoreBtns) {
        viewScoreBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                // Get user ID and username from data attributes
                const userId = this.dataset.userId;
                const username = this.dataset.username;
                
                // Update the username display
                if (usernameDisplay) {
                    usernameDisplay.textContent = username;
                }
                
                // Hide users view and show user scores view
                if (usersView) usersView.classList.remove('view-active');
                if (userScoresView) userScoresView.classList.add('view-active');
                if (allScoresView) allScoresView.classList.remove('view-active');
                
                // Fetch user scores via AJAX
                fetch(`/scores/user/${userId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Populate the scores table
                            populateUserScoresTable(data.scores);
                            
                            // Update category statistics
                            updateUserCategoryStats(data.stats);
                            
                            // Play a sound if available
                            playClickSound();
                        } else {
                            console.error('Error fetching user scores');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
            });
        });
    }
    
    // Back to users list button
    if (backToUsersBtn) {
        backToUsersBtn.addEventListener('click', function() {
            if (usersView) usersView.classList.add('view-active');
            if (userScoresView) userScoresView.classList.remove('view-active');
            if (allScoresView) allScoresView.classList.remove('view-active');
            
            // Play a sound if available
            playClickSound();
        });
    }
    
    // Function to populate user scores table
    function populateUserScoresTable(scores) {
        const tbody = document.getElementById('user-scores-tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (scores.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="5">No scores found for this user.</td>';
            tbody.appendChild(row);
            return;
        }
        
        scores.forEach(score => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${score.id}</td>
                <td>${score.score}</td>
                <td>${score.category}</td>
                <td>${score.date_attempted}</td>
                <td>
                    <form action="/scores/delete/${score.id}" method="POST" id="deleteForm-${score.id}" style="display: inline;">
                        <button type="submit" class="btn btn-danger delete-score-btn" data-score-id="${score.id}">
                            <i class='bx bxs-trash'></i>
                        </button>
                    </form>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        // Re-attach delete confirmation to new buttons
        attachDeleteConfirmation();
    }
    
    // Function to update category statistics
    function updateUserCategoryStats(stats) {
        for (const [category, data] of Object.entries(stats)) {
            const statElement = document.getElementById(`user-stat-${category}`);
            const avgElement = document.getElementById(`user-stat-avg-${category}`);
            
            if (statElement) {
                statElement.textContent = `${data.count} Attempts`;
            }
            
            if (avgElement) {
                avgElement.textContent = `Avg: ${data.avg_score.toFixed(1)} | Max: ${data.max_score}`;
            }
        }
    }
    
    // Function to play click sound
    function playClickSound() {
        const clickSound = document.getElementById('clickSound');
        if (clickSound) {
            clickSound.currentTime = 0;
            clickSound.play().catch(e => {
                console.log('Sound play prevented:', e);
            });
        }
    }
    
    // Function to attach SweetAlert2 confirmation to delete buttons
    function attachDeleteConfirmation() {
        const deleteButtons = document.querySelectorAll('.delete-score-btn');
        
        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const scoreId = this.dataset.scoreId;
                
                Swal.fire({
                    title: 'Are you sure?',
                    text: "You won't be able to recover this score entry!",
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonColor: '#e74c3c',
                    cancelButtonColor: '#3085d6',
                    confirmButtonText: 'Yes, delete it!',
                    background: 'rgba(0, 0, 0, 0.9)',
                    color: '#fff',
                    backdrop: `
                        rgba(0,0,0,0.4)
                        url("{{ url_for('static', filename='img/Logo.png') }}")
                        left top
                        no-repeat
                    `
                }).then((result) => {
                    if (result.isConfirmed) {
                        document.getElementById('deleteForm-' + scoreId).submit();
                        playClickSound();
                    }
                });
            });
        });
    }
    
    // Initial setup - attach delete confirmation to existing buttons
    attachDeleteConfirmation();
});