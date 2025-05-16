document.addEventListener('DOMContentLoaded', function() {
  // DOM elements for classes popup
  const classesLink = document.getElementById('classes-link');
  const choiceClassesBtn = document.getElementById('choice-classes-btn');
  const classesPopup = document.getElementById('classes-popup');
  const classesExitBtn = document.querySelector('.classes-exit-btn');
  const joinClassForm = document.getElementById('join-class-form');
  const classCodeInput = document.getElementById('class-code');
  const errorAlert = document.getElementById('error-alert');
  const successAlert = document.getElementById('success-alert');
  const joinSpinner = document.getElementById('join-spinner');
  const classesContainer = document.getElementById('classes-container');
  const classTemplate = document.getElementById('class-template');
  const emptyStateTemplate = document.getElementById('empty-state-template');
  const header = document.querySelector('.header');
  const sections = document.querySelectorAll('section');
  
  // Show classes popup
  function showClassesPopup() {
    classesPopup.classList.add('active');
    sections.forEach(section => {
      if (section !== classesPopup) {
        section.classList.add('blur'); 
        header.classList.add('blur'); 
      }
    });
    document.body.style.overflow = 'hidden'; // Disable page scrolling
    
    // Load classes when popup is opened
    loadEnrolledClasses();
  }
  
  // Hide classes popup
  function hideClassesPopup() {
    classesPopup.classList.remove('active');
    sections.forEach(section => {
      section.classList.remove('blur'); // Remove blur from all sections
    });
    header.classList.remove('blur');
    document.body.style.overflow = ''; // Enable page scrolling
  }

  // Event listeners for showing/hiding classes popup
  if (classesLink) {
    classesLink.addEventListener('click', function(e) {
      e.preventDefault();
      showClassesPopup();
    });
  }

  if (choiceClassesBtn) {
    choiceClassesBtn.addEventListener('click', function() {
      // Also close the popup-info if it's open
      const popupInfo = document.querySelector('.popup-info');
      if (popupInfo) {
        popupInfo.classList.remove('active');
        sections.forEach(section => {
          section.classList.remove('blur');
        });
        header.classList.remove('blur');
      }
      
      showClassesPopup();
    });
  }

  if (classesExitBtn) {
    classesExitBtn.addEventListener('click', hideClassesPopup);
  }

  // Join class form submission
  if (joinClassForm) {
    joinClassForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const classCode = classCodeInput.value.trim();
      
      // Validate code format
      if (!classCode || classCode.length !== 6) {
        showError('Please enter a valid 6-character class code');
        return;
      }
      
      // Hide any previous alerts
      hideAlerts();
      
      // Show spinner
      joinSpinner.style.display = 'inline-block';
      
      // API call to join the class
      fetch('/api/join-class', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code: classCode })
      })
      .then(response => response.json())
      .then(data => {
        // Hide spinner
        joinSpinner.style.display = 'none';
        
        if (data.status === 'error') {
          showError(data.message || 'Failed to join class');
          return;
        }
        
        // On success
        showSuccess(data.message || 'Successfully joined the class!');
        classCodeInput.value = ''; // Clear input
        
        // Reload classes
        loadEnrolledClasses();
      })
      .catch(error => {
        // Hide spinner
        joinSpinner.style.display = 'none';
        showError('An error occurred. Please try again.');
        console.error('Error:', error);
      });
    });
  }

  // Helper function to show error message
  function showError(message) {
    if (errorAlert) {
      errorAlert.textContent = message;
      errorAlert.style.display = 'block';
      successAlert.style.display = 'none';
    }
  }
  
  // Helper function to show success message
  function showSuccess(message) {
    if (successAlert) {
      successAlert.textContent = message;
      successAlert.style.display = 'block';
      errorAlert.style.display = 'none';
    }
  }
  
  // Helper function to hide alert messages
  function hideAlerts() {
    if (errorAlert) errorAlert.style.display = 'none';
    if (successAlert) successAlert.style.display = 'none';
  }

  // Function to load enrolled classes
  function loadEnrolledClasses() {
    if (!classesContainer) return;
    
    // Show loading state
    classesContainer.innerHTML = `
      <div class="loading" style="text-align: center; padding: 1rem;">
        <div class="spinner" style="display: inline-block; width: 30px; height: 30px;"></div>
        <p>Loading your classes...</p>
      </div>
    `;
    
    // Fetch classes from API
    fetch('/api/classes')
      .then(response => response.json())
      .then(data => {
        if (data.status === 'error') {
          classesContainer.innerHTML = `<p class="error">${data.message || 'Failed to load classes'}</p>`;
          return;
        }
        
        if (!data.classes || data.classes.length === 0) {
          // Show empty state
          classesContainer.innerHTML = '';
          const emptyState = document.importNode(emptyStateTemplate.content, true);
          classesContainer.appendChild(emptyState);
          return;
        }
        
        // Create class grid
        const classesGrid = document.createElement('div');
        classesGrid.className = 'classes-grid';
        
        // Add each class
        data.classes.forEach(classItem => {
          const classCard = document.importNode(classTemplate.content, true);
          
          // Fill in class details
          classCard.querySelector('.class-name').textContent = classItem.name;
          classCard.querySelector('.class-section').textContent = classItem.section || '';
          classCard.querySelector('.class-description').textContent = classItem.description || 'No description available';
          classCard.querySelector('.start-date').textContent = `Start: ${formatDate(classItem.startDate)}`;
          classCard.querySelector('.end-date').textContent = `End: ${formatDate(classItem.endDate)}`;
          classCard.querySelector('.student-count').textContent = `Students: ${classItem.studentCount || 0}`;
          
          // Set up buttons
          const viewBtn = classCard.querySelector('.view-class-btn');
          viewBtn.href = `/user/class/${classItem.id}`;
          
          const leaveBtn = classCard.querySelector('.leave-class-btn');
          leaveBtn.setAttribute('data-class-id', classItem.id);
          leaveBtn.setAttribute('data-class-name', classItem.name);
          
          // Add to grid
          classesGrid.appendChild(classCard);
        });
        
        // Replace loading with class grid
        classesContainer.innerHTML = '';
        classesContainer.appendChild(classesGrid);
        
        // Add event listeners for leave buttons
        document.querySelectorAll('.leave-class-btn').forEach(btn => {
          btn.addEventListener('click', function() {
            const classId = this.getAttribute('data-class-id');
            const className = this.getAttribute('data-class-name');
            
            if (confirm(`Are you sure you want to leave ${className}? This action cannot be undone.`)) {
              leaveClass(classId);
            }
          });
        });
      })
      .catch(error => {
        classesContainer.innerHTML = `<p class="error">Failed to load classes. Please try again later.</p>`;
        console.error('Error:', error);
      });
  }
  
  // Function to leave a class
  function leaveClass(classId) {
    if (!classId) return;
    
    fetch(`/api/leave-class/${classId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'error') {
        showError(data.message || 'Failed to leave class');
        return;
      }
      
      // On success
      showSuccess(data.message || 'Successfully left the class!');
      
      // Reload classes
      loadEnrolledClasses();
    })
    .catch(error => {
      showError('An error occurred. Please try again.');
      console.error('Error:', error);
    });
  }
  
  // Format date helper
  function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString; // Return as-is if invalid date
    
    return date.toLocaleDateString();
  }
  
  // Make functions available to the window object
  window.showClassesPopup = showClassesPopup;
  window.hideClassesPopup = hideClassesPopup;
  window.loadEnrolledClasses = loadEnrolledClasses;
});
