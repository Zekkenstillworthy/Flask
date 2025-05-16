
        // Add audio feedback for better user experience
        function playClickSound() {
            const clickSound = document.getElementById('clickSound');
            if (clickSound) {
                clickSound.currentTime = 0;
                clickSound.play();
            }
        }
        
        document.querySelectorAll('a, button').forEach(element => {
            element.addEventListener('click', playClickSound);
        });

        // Modal functionality
        function openModal(modalId) {
            const modal = document.getElementById(modalId);
            modal.style.display = 'block';
            setTimeout(() => {
                modal.classList.add('active');
            }, 10);
            document.body.style.overflow = 'hidden';
        }

        function closeModal(modalId) {
            const modal = document.getElementById(modalId);
            modal.classList.remove('active');
            setTimeout(() => {
                modal.style.display = 'none';
            }, 300);
            document.body.style.overflow = '';
        }

        // Close modal when clicking on backdrop
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', event => {
                if (event.target === modal) {
                    closeModal(modal.id);
                }
            });
        });

        // Handle question type change
        document.addEventListener('DOMContentLoaded', function() {
            // Add question modal
            const questionTypeSelect = document.getElementById('question-type');
            const optionsContainer = document.getElementById('options-container');
            const matchingContainer = document.getElementById('matching-container');
            const answerField = document.getElementById('answer');
            
            if (questionTypeSelect) {
                questionTypeSelect.addEventListener('change', function() {
                    updateQuestionTypeUI(this.value, optionsContainer, matchingContainer, answerField);
                });
            }
            
            // Edit question modal
            const editQuestionTypeSelect = document.getElementById('edit-question-type');
            const editOptionsContainer = document.getElementById('edit-options-container');
            const editMatchingContainer = document.getElementById('edit-matching-container');
            const editAnswerField = document.getElementById('edit-answer');
            
            if (editQuestionTypeSelect) {
                editQuestionTypeSelect.addEventListener('change', function() {
                    updateQuestionTypeUI(this.value, editOptionsContainer, editMatchingContainer, editAnswerField);
                });
            }
            
            // Function to update UI based on question type
            function updateQuestionTypeUI(type, optionsContainer, matchingContainer, answerField) {
                if (type === 'multiple_choice') {
                    optionsContainer.style.display = 'block';
                    matchingContainer.style.display = 'none';
                    answerField.placeholder = 'Enter the exact text of the correct option';
                    answerField.disabled = false;
                } else if (type === 'matching') {
                    optionsContainer.style.display = 'none';
                    matchingContainer.style.display = 'block';
                    answerField.placeholder = 'Will be auto-generated';
                    answerField.value = 'auto-generated';
                    answerField.disabled = true;
                } else if (type === 'fill_blank' || type === 'short_answer') {
                    optionsContainer.style.display = 'none';
                    matchingContainer.style.display = 'none';
                    answerField.placeholder = 'Enter the correct answer';
                    answerField.disabled = false;
                    if (answerField.value === 'auto-generated') {
                        answerField.value = '';
                    }
                } else if (type === 'essay') {
                    optionsContainer.style.display = 'none';
                    matchingContainer.style.display = 'none';
                    answerField.placeholder = 'N/A for essay questions';
                    answerField.value = 'N/A';
                    answerField.disabled = true;
                }
            }
            
            // Add option button functionality
            const addOptionBtn = document.getElementById('add-option');
            if (addOptionBtn) {
                addOptionBtn.addEventListener('click', function() {
                    const optionInputs = document.querySelector('.option-inputs');
                    const newInput = document.createElement('input');
                    newInput.type = 'text';
                    newInput.name = 'option' + (optionInputs.children.length + 1);
                    newInput.placeholder = `Option ${optionInputs.children.length + 1}`;
                    optionInputs.appendChild(newInput);
                });
            }
            
            // Add matching pair button functionality
            const addPairBtn = document.getElementById('add-pair');
            if (addPairBtn) {
                addPairBtn.addEventListener('click', function() {
                    const matchingPairs = document.querySelector('.matching-pairs');
                    addMatchingPair(matchingPairs);
                });
            }
            
            // Edit modal - Add option button
            const editAddOptionBtn = document.getElementById('edit-add-option');
            if (editAddOptionBtn) {
                editAddOptionBtn.addEventListener('click', function() {
                    const optionInputs = document.getElementById('edit-option-inputs');
                    const newInput = document.createElement('input');
                    newInput.type = 'text';
                    newInput.name = 'option' + (optionInputs.children.length + 1);
                    newInput.placeholder = `Option ${optionInputs.children.length + 1}`;
                    optionInputs.appendChild(newInput);
                });
            }
            
            // Edit modal - Add matching pair button
            const editAddPairBtn = document.getElementById('edit-add-pair');
            if (editAddPairBtn) {
                editAddPairBtn.addEventListener('click', function() {
                    const matchingPairs = document.getElementById('edit-matching-pairs');
                    addMatchingPair(matchingPairs);
                });
            }
            
            // Function to add a new matching pair
            function addMatchingPair(container) {
                const pair = document.createElement('div');
                pair.className = 'matching-pair';
                
                const itemInput = document.createElement('input');
                itemInput.type = 'text';
                itemInput.name = 'matching_item[]';
                itemInput.placeholder = 'Item';
                
                const matchInput = document.createElement('input');
                matchInput.type = 'text';
                matchInput.name = 'matching_match[]';
                matchInput.placeholder = 'Match';
                
                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'btn-remove-pair';
                removeBtn.textContent = '×';
                removeBtn.addEventListener('click', function() {
                    container.removeChild(pair);
                });
                
                pair.appendChild(itemInput);
                pair.appendChild(matchInput);
                pair.appendChild(removeBtn);
                container.appendChild(pair);
            }
            
            // Setup remove pair buttons for initial pairs
            document.querySelectorAll('.btn-remove-pair').forEach(button => {
                button.addEventListener('click', function() {
                    const pair = this.closest('.matching-pair');
                    const container = pair.parentNode;
                    if (container.children.length > 1) {
                        container.removeChild(pair);
                    }
                });
            });
            
            // Setup form submission for add question
            const addQuestionForm = document.getElementById('addQuestionForm');
            if (addQuestionForm) {
                addQuestionForm.addEventListener('submit', function(e) {
                    e.preventDefault();
                    
                    // Format matching question answer if needed
                    const questionType = document.getElementById('question-type').value;
                    if (questionType === 'matching') {
                        const items = Array.from(document.querySelectorAll('input[name="matching_item[]"]')).map(input => input.value);
                        const matches = Array.from(document.querySelectorAll('input[name="matching_match[]"]')).map(input => input.value);
                        
                        // Create pairs array for JSON
                        const pairs = items.map((item, index) => {
                            return {
                                item: item,
                                match: matches[index] || ''
                            };
                        }).filter(pair => pair.item && pair.match); // Remove incomplete pairs
                        
                        if (pairs.length < 2) {
                            alert('Please add at least 2 complete matching pairs.');
                            return;
                        }
                        
                        // Set as JSON string
                        document.getElementById('answer').value = JSON.stringify(pairs);
                    }
                    
                    // Validate based on question type
                    if (!validateQuestionForm(questionType)) {
                        return;
                    }
                    
                    // Submit the form
                    this.submit();
                });
            }
            
            // Setup form submission for edit question
            const editQuestionForm = document.getElementById('editQuestionForm');
            if (editQuestionForm) {
                editQuestionForm.addEventListener('submit', function(e) {
                    e.preventDefault();
                    
                    // Format matching question answer if needed
                    const questionType = document.getElementById('edit-question-type').value;
                    if (questionType === 'matching') {
                        const items = Array.from(document.querySelectorAll('#edit-matching-pairs input[name="matching_item[]"]')).map(input => input.value);
                        const matches = Array.from(document.querySelectorAll('#edit-matching-pairs input[name="matching_match[]"]')).map(input => input.value);
                        
                        // Create pairs array for JSON
                        const pairs = items.map((item, index) => {
                            return {
                                item: item,
                                match: matches[index] || ''
                            };
                        }).filter(pair => pair.item && pair.match); // Remove incomplete pairs
                        
                        if (pairs.length < 2) {
                            alert('Please add at least 2 complete matching pairs.');
                            return;
                        }
                        
                        // Set as JSON string
                        document.getElementById('edit-answer').value = JSON.stringify(pairs);
                    }
                    
                    // Validate based on question type
                    if (!validateEditQuestionForm(questionType)) {
                        return;
                    }
                    
                    // Update form action with question_id
                    const questionId = document.getElementById('edit-question-id').value;
                    this.action = "{{ url_for('question.edit_question', question_id=0) }}".replace('0', questionId);
                    
                    // Submit the form
                    this.submit();
                });
            }
            
            // Form validation functions
            function validateQuestionForm(type) {
                if (type === 'multiple_choice') {
                    const options = [];
                    for (let i = 1; i <= 4; i++) {
                        const option = document.querySelector(`input[name="option${i}"]`);
                        if (option && option.value.trim() !== '') {
                            options.push(option.value.trim());
                        }
                    }
                    
                    if (options.length < 2) {
                        alert('Please add at least 2 options for multiple choice questions.');
                        return false;
                    }
                    
                    const answer = document.getElementById('answer').value;
                    const hasMatchingOption = options.includes(answer);
                    
                    if (!hasMatchingOption) {
                        alert('The correct answer must match one of the options exactly.');
                        return false;
                    }
                }
                
                return true;
            }
            
            function validateEditQuestionForm(type) {
                if (type === 'multiple_choice') {
                    const options = [];
                    for (let i = 1; i <= 4; i++) {
                        const option = document.querySelector(`#edit-option-inputs input[name="option${i}"]`);
                        if (option && option.value.trim() !== '') {
                            options.push(option.value.trim());
                        }
                    }
                    
                    if (options.length < 2) {
                        alert('Please add at least 2 options for multiple choice questions.');
                        return false;
                    }
                    
                    const answer = document.getElementById('edit-answer').value;
                    const hasMatchingOption = options.includes(answer);
                    
                    if (!hasMatchingOption) {
                        alert('The correct answer must match one of the options exactly.');
                        return false;
                    }
                }
                
                return true;
            }
            
            // Setup edit question buttons
            document.querySelectorAll('a.btn[title="Edit question"]').forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    const questionId = this.href.split('/').pop();
                    loadQuestionData(questionId);
                });
            });
            
            // Function to load question data for editing
            function loadQuestionData(questionId) {
                fetch(`/admin/questions/get/${questionId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            const question = data.question;
                            
                            // Set the form action and question ID
                            document.getElementById('edit-question-id').value = question.id;
                            
                            // Fill basic fields
                            document.getElementById('edit-question').value = question.question;
                            document.getElementById('edit-number').value = question.numb;
                            document.getElementById('edit-answer').value = question.answer;
                            document.getElementById('edit-explanation').value = question.explanation;
                            
                            // Set the category
                            const categorySelect = document.getElementById('edit-category');
                            categorySelect.value = question.category;
                            
                            // Set question type
                            const typeSelect = document.getElementById('edit-question-type');
                            typeSelect.value = question.question_type;
                            
                            // Update UI for question type
                            updateQuestionTypeUI(
                                question.question_type,
                                document.getElementById('edit-options-container'),
                                document.getElementById('edit-matching-container'),
                                document.getElementById('edit-answer')
                            );
                            
                            // Handle options for multiple choice
                            const optionInputs = document.getElementById('edit-option-inputs');
                            optionInputs.innerHTML = '';
                            
                            if (question.question_type === 'multiple_choice' && question.options) {
                                question.options.forEach((option, index) => {
                                    const input = document.createElement('input');
                                    input.type = 'text';
                                    input.name = `option${index + 1}`;
                                    input.value = option;
                                    input.placeholder = `Option ${index + 1}`;
                                    optionInputs.appendChild(input);
                                });
                            }
                            
                            // Handle pairs for matching
                            const matchingPairs = document.getElementById('edit-matching-pairs');
                            matchingPairs.innerHTML = '';
                            
                            if (question.question_type === 'matching' && question.matching_pairs) {
                                question.matching_pairs.forEach(pair => {
                                    const pairDiv = document.createElement('div');
                                    pairDiv.className = 'matching-pair';
                                    
                                    const itemInput = document.createElement('input');
                                    itemInput.type = 'text';
                                    itemInput.name = 'matching_item[]';
                                    itemInput.value = pair.item;
                                    itemInput.placeholder = 'Item';
                                    
                                    const matchInput = document.createElement('input');
                                    matchInput.type = 'text';
                                    matchInput.name = 'matching_match[]';
                                    matchInput.value = pair.match;
                                    matchInput.placeholder = 'Match';
                                    
                                    const removeBtn = document.createElement('button');
                                    removeBtn.type = 'button';
                                    removeBtn.className = 'btn-remove-pair';
                                    removeBtn.textContent = '×';
                                    removeBtn.addEventListener('click', function() {
                                        if (matchingPairs.children.length > 2) {
                                            matchingPairs.removeChild(pairDiv);
                                        }
                                    });
                                    
                                    pairDiv.appendChild(itemInput);
                                    pairDiv.appendChild(matchInput);
                                    pairDiv.appendChild(removeBtn);
                                    matchingPairs.appendChild(pairDiv);
                                });
                            }
                            
                            // Show the modal
                            openModal('editQuestionModal');
                        } else {
                            alert('Error loading question: ' + (data.message || 'Unknown error'));
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('An error occurred while loading the question.');
                    });
            }
            
            // Question group functionality
            const questionCategoryFilter = document.getElementById('question-category-filter');
            if (questionCategoryFilter) {
                // Load ungrouped questions when filter changes
                questionCategoryFilter.addEventListener('change', function() {
                    loadUngroupedQuestions(this.value);
                });
                
                // Initial load of all ungrouped questions
                loadUngroupedQuestions('all');
                
                // Setup group form submission
                const addGroupForm = document.getElementById('addGroupForm');
                if (addGroupForm) {
                    addGroupForm.addEventListener('submit', function(e) {
                        e.preventDefault();
                        
                        // Get the group name and description
                        const name = document.getElementById('group-name').value.trim();
                        const description = document.getElementById('group-description').value.trim();
                        
                        if (!name) {
                            alert('Group name is required');
                            return;
                        }
                        
                        // Get selected questions
                        const selectedQuestions = Array.from(document.querySelectorAll('.available-questions input[type="checkbox"]:checked'))
                            .map(checkbox => checkbox.value);
                        
                        // If no questions selected, just create the empty group
                        if (selectedQuestions.length === 0) {
                            // Regular form submission for empty group
                            this.submit();
                            return;
                        }
                        
                        // Create FormData for the request
                        const formData = new FormData();
                        formData.append('action', 'create');
                        formData.append('group_name', name);
                        formData.append('group_description', description);
                        formData.append('question_ids', JSON.stringify(selectedQuestions));
                        
                        // Submit via AJAX
                        fetch('/admin/questions/group_questions', {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                alert(data.message);
                                // Redirect to the questions page
                                window.location.href = "{{ url_for('question.index') }}";
                            } else {
                                alert('Error: ' + (data.error || 'Failed to create group'));
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('An error occurred while creating the group');
                        });
                    });
                }
            }
            
            // Function to load ungrouped questions for the group modal
            function loadUngroupedQuestions(category) {
                const questionsContainer = document.querySelector('.available-questions');
                if (!questionsContainer) return;
                
                questionsContainer.innerHTML = '<div class="no-questions">Loading questions...</div>';
                
                fetch(`/questions/api/ungrouped?category=${category}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Failed to fetch questions: ' + response.status);
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.success && data.questions && data.questions.length > 0) {
                            questionsContainer.innerHTML = '';
                            data.questions.forEach(question => {
                                const questionItem = document.createElement('div');
                                questionItem.className = 'question-item';
                                
                                const checkbox = document.createElement('input');
                                checkbox.type = 'checkbox';
                                checkbox.name = 'question_ids';
                                checkbox.value = question.id;
                                checkbox.id = `question_${question.id}`;
                                
                                const label = document.createElement('label');
                                label.htmlFor = `question_${question.id}`;
                                label.textContent = `[${question.type}] ${question.question}`;
                                
                                // Add category badge
                                const badge = document.createElement('span');
                                badge.className = 'category-badge category-' + question.category;
                                badge.textContent = question.category.charAt(0).toUpperCase() + question.category.slice(1);
                                label.prepend(badge);
                                
                                questionItem.appendChild(checkbox);
                                questionItem.appendChild(label);
                                questionsContainer.appendChild(questionItem);
                            });
                        } else {
                            questionsContainer.innerHTML = '<div class="no-questions">No ungrouped questions found in this category.</div>';
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        questionsContainer.innerHTML = '<div class="no-questions">Error loading questions. Please try again.</div>';
                    });
            }
            
            // Enable "Create New Group" card to open modal
            const createGroupCard = document.querySelector('.create-group-card');
            if (createGroupCard) {
                createGroupCard.addEventListener('click', function() {
                    openModal('addGroupModal');
                });
            }
            
            // Group selected questions button functionality
            const groupSelectedBtn = document.getElementById('groupSelectedBtn');
            if (groupSelectedBtn) {
                groupSelectedBtn.addEventListener('click', function() {
                    // First, get all groups to populate the dropdown
                    fetch('/admin/questions/get_groups')
                        .then(response => response.json())
                        .then(data => {
                            if (data.success && data.groups) {
                                // Create and show a modal for grouping
                                showGroupingModal(data.groups);
                            } else {
                                alert('Error: Failed to load question groups');
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('An error occurred while loading question groups');
                        });
                });
            }
            
            // Function to show a modal for grouping questions
            function showGroupingModal(groups) {
                // Check if the modal already exists
                let groupingModal = document.getElementById('groupQuestionsModal');
                
                // Create the modal if it doesn't exist
                if (!groupingModal) {
                    groupingModal = document.createElement('div');
                    groupingModal.id = 'groupQuestionsModal';
                    groupingModal.className = 'modal';
                    
                    groupingModal.innerHTML = `
                        <div class="modal-content">
                            <div class="modal-header">
                                <h3>Group Selected Questions</h3>
                                <span class="close-modal" onclick="closeModal('groupQuestionsModal')">&times;</span>
                            </div>
                            <div class="modal-body">
                                <form id="groupQuestionsForm">
                                    <div class="form-group">
                                        <label for="group-action">Action</label>
                                        <select id="group-action" name="action">
                                            <option value="add">Add to Existing Group</option>
                                            <option value="create">Create New Group</option>
                                        </select>
                                    </div>
                                    
                                    <div id="existing-group-section">
                                        <div class="form-group">
                                            <label for="existing-group">Select Group</label>
                                            <select id="existing-group" name="group_id"></select>
                                        </div>
                                    </div>
                                    
                                    <div id="new-group-section" style="display: none;">
                                        <div class="form-group">
                                            <label for="new-group-name">Group Name</label>
                                            <input type="text" id="new-group-name" required>
                                        </div>
                                        <div class="form-group">
                                            <label for="new-group-description">Description</label>
                                            <textarea id="new-group-description" rows="3"></textarea>
                                        </div>
                                    </div>
                                    
                                    <div class="modal-footer">
                                        <button type="button" class="btn btn-secondary" onclick="closeModal('groupQuestionsModal')">Cancel</button>
                                        <button type="submit" class="btn">Add to Group</button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    `;
                    
                    document.body.appendChild(groupingModal);
                    
                    // Add event listener for the action select
                    const actionSelect = groupingModal.querySelector('#group-action');
                    actionSelect.addEventListener('change', function() {
                        const existingGroupSection = groupingModal.querySelector('#existing-group-section');
                        const newGroupSection = groupingModal.querySelector('#new-group-section');
                        
                        if (this.value === 'add') {
                            existingGroupSection.style.display = 'block';
                            newGroupSection.style.display = 'none';
                        } else {
                            existingGroupSection.style.display = 'none';
                            newGroupSection.style.display = 'block';
                        }
                    });
                    
                    // Handle form submission
                    const form = groupingModal.querySelector('#groupQuestionsForm');
                    form.addEventListener('submit', function(e) {
                        e.preventDefault();
                        
                        // Get all checked questions
                        const selectedQuestions = Array.from(document.querySelectorAll('input[name="question_checkbox"]:checked'))
                            .map(checkbox => checkbox.value);
                        
                        if (selectedQuestions.length === 0) {
                            alert('Please select at least one question');
                            return;
                        }
                        
                        const action = document.getElementById('group-action').value;
                        
                        // Create FormData for the request
                        const formData = new FormData();
                        formData.append('action', action);
                        formData.append('question_ids', JSON.stringify(selectedQuestions));
                        
                        if (action === 'add') {
                            const groupId = document.getElementById('existing-group').value;
                            if (!groupId) {
                                alert('Please select a group');
                                return;
                            }
                            
                            formData.append('group_id', groupId);
                        } else {
                            const name = document.getElementById('new-group-name').value.trim();
                            const description = document.getElementById('new-group-description').value.trim();
                            
                            if (!name) {
                                alert('Group name is required');
                                return;
                            }
                            
                            formData.append('group_name', name);
                            formData.append('group_description', description);
                        }
                        
                        // Submit via AJAX
                        fetch('/admin/questions/group_questions', {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                alert(data.message);
                                // Reload the page to show the updated groups
                                window.location.reload();
                            } else {
                                alert('Error: ' + (data.error || 'Failed to group questions'));
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('An error occurred while grouping questions');
                        });
                    });
                }
                
                // Populate the groups dropdown
                const groupSelect = groupingModal.querySelector('#existing-group');
                groupSelect.innerHTML = '';
                
                groups.forEach(group => {
                    const option = document.createElement('option');
                    option.value = group.id;
                    option.textContent = group.name;
                    groupSelect.appendChild(option);
                });
                
                // Show the modal
                openModal('groupQuestionsModal');
            }
            
            // Checkbox selection functionality for showing the group button
            document.addEventListener('change', function(e) {
                if (e.target.matches('input[name="question_checkbox"]')) {
                    const checkedBoxes = document.querySelectorAll('input[name="question_checkbox"]:checked');
                    const groupSelectedBtn = document.getElementById('groupSelectedBtn');
                    
                    if (groupSelectedBtn) {
                        if (checkedBoxes.length > 0) {
                            groupSelectedBtn.style.display = 'inline-block';
                        } else {
                            groupSelectedBtn.style.display = 'none';
                        }
                    }
                }
            });
            
            // Add checkboxes to ungrouped questions for group selection
            function addCheckboxesToQuestions() {
                const tables = document.querySelectorAll('.category-section table');
                tables.forEach(table => {
                    const headerRow = table.querySelector('thead tr');
                    
                    // Add checkbox header if needed
                    if (!headerRow.querySelector('th.checkbox-column')) {
                        const checkboxHeader = document.createElement('th');
                        checkboxHeader.className = 'checkbox-column';
                        checkboxHeader.style.width = '30px';
                        headerRow.insertBefore(checkboxHeader, headerRow.firstChild);
                    }
                    
                    // Add checkboxes to each row
                    const rows = table.querySelectorAll('tbody tr');
                    rows.forEach(row => {
                        // Get the question ID from the edit link
                        const editLink = row.querySelector('a[href*="/edit/"]');
                        if (editLink) {
                            const questionId = editLink.href.split('/').pop();
                            
                            // Only add checkbox if it doesn't exist
                            if (!row.querySelector('td.checkbox-column')) {
                                const checkboxCell = document.createElement('td');
                                checkboxCell.className = 'checkbox-column';
                                
                                const checkbox = document.createElement('input');
                                checkbox.type = 'checkbox';
                                checkbox.name = 'question_checkbox';
                                checkbox.value = questionId;
                                
                                checkboxCell.appendChild(checkbox);
                                row.insertBefore(checkboxCell, row.firstChild);
                            }
                        }
                    });
                });
            }
            
            // Initialize checkboxes for questions
            addCheckboxesToQuestions();
            
            // Add a select all checkbox in each category
            document.querySelectorAll('.category-header').forEach(header => {
                const categorySection = header.closest('.category-section');
                if (categorySection) {
                    const selectAllContainer = document.createElement('span');
                    selectAllContainer.style.marginLeft = '10px';
                    
                    const selectAllCheckbox = document.createElement('input');
                    selectAllCheckbox.type = 'checkbox';
                    selectAllCheckbox.className = 'select-all-checkbox';
                    
                    const selectAllLabel = document.createElement('label');
                    selectAllLabel.style.fontSize = '14px';
                    selectAllLabel.style.fontWeight = 'normal';
                    selectAllLabel.textContent = ' Select All';
                    
                    selectAllContainer.appendChild(selectAllCheckbox);
                    selectAllContainer.appendChild(selectAllLabel);
                    header.appendChild(selectAllContainer);
                    
                    // Add select all functionality
                    selectAllCheckbox.addEventListener('change', function() {
                        const checkboxes = categorySection.querySelectorAll('input[name="question_checkbox"]');
                        checkboxes.forEach(checkbox => {
                            checkbox.checked = this.checked;
                        });
                        
                        // Show/hide group button based on selection
                        const groupSelectedBtn = document.getElementById('groupSelectedBtn');
                        if (groupSelectedBtn) {
                            const anyChecked = document.querySelector('input[name="question_checkbox"]:checked');
                            groupSelectedBtn.style.display = anyChecked ? 'inline-block' : 'none';
                        }
                    });
                }
            });
            
            // Check URL parameters to see if we should show the ungrouped modal
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('show_ungrouped_modal') === 'True') {
                // Show ungrouped questions modal when page loads
                setTimeout(() => {
                    openModal('ungroupedQuestionsModal');
                    loadUngroupedQuestionsForModal('all');
                }, 300);
            }
            
            // Ungrouped questions modal functionality
            const ungroupedCategoryFilter = document.getElementById('ungrouped-category-filter');
            if (ungroupedCategoryFilter) {
                ungroupedCategoryFilter.addEventListener('change', function() {
                    loadUngroupedQuestionsForModal(this.value);
                });
            }
            
            // Handle action radio buttons in ungrouped questions modal
            const actionRadios = document.querySelectorAll('input[name="group-action"]');
            actionRadios.forEach(radio => {
                radio.addEventListener('change', function() {
                    const existingGroupSection = document.getElementById('existing-group-section');
                    const newGroupSection = document.getElementById('new-group-section');
                    
                    if (this.value === 'add') {
                        existingGroupSection.style.display = 'block';
                        newGroupSection.style.display = 'none';
                    } else {
                        existingGroupSection.style.display = 'none';
                        newGroupSection.style.display = 'block';
                    }
                });
            });
            
            // Load ungrouped questions for the modal
            function loadUngroupedQuestionsForModal(category, preSelectedQuestionIds = []) {
                const container = document.querySelector('.ungrouped-questions-container');
                if (!container) return;
                
                container.innerHTML = '<div class="loading-spinner">Loading questions...</div>';
                
                fetch(`/questions/api/ungrouped?category=${category}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Failed to fetch questions: ' + response.status);
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.success && data.questions && data.questions.length > 0) {
                            // Create table for questions
                            const table = document.createElement('table');
                            table.className = 'ungrouped-questions-table';
                            
                            // Create table header
                            const thead = document.createElement('thead');
                            const headerRow = document.createElement('tr');
                            
                            const checkboxHeader = document.createElement('th');
                            checkboxHeader.style.width = '30px';
                            
                            const selectAllCheckbox = document.createElement('input');
                            selectAllCheckbox.type = 'checkbox';
                            selectAllCheckbox.id = 'select-all-ungrouped';
                            
                            // Add select all functionality
                            selectAllCheckbox.addEventListener('change', function() {
                                const checkboxes = table.querySelectorAll('input[type="checkbox"]');
                                checkboxes.forEach(checkbox => {
                                    checkbox.checked = this.checked;
                                });
                                updateSelectedCount();
                                updateGroupButtonState();
                            });
                            
                            checkboxHeader.appendChild(selectAllCheckbox);
                            headerRow.appendChild(checkboxHeader);
                            
                            headerRow.innerHTML += `
                                <th>ID</th>
                                <th>Category</th>
                                <th>Type</th>
                                <th>Question</th>
                            `;
                            
                            thead.appendChild(headerRow);
                            table.appendChild(thead);
                            
                            // Create table body
                            const tbody = document.createElement('tbody');
                            
                            // Check if we should pre-select all questions
                            const shouldSelectAll = preSelectedQuestionIds.length > 0 && 
                                preSelectedQuestionIds.length === data.questions.length;
                            
                            if (shouldSelectAll) {
                                selectAllCheckbox.checked = true;
                            }
                            
                            data.questions.forEach(question => {
                                const row = document.createElement('tr');
                                
                                // Checkbox cell
                                const checkboxCell = document.createElement('td');
                                const checkbox = document.createElement('input');
                                checkbox.type = 'checkbox';
                                checkbox.name = 'ungrouped_question_checkbox';
                                checkbox.value = question.id;
                                
                                // Pre-select checkbox if it's in the preSelectedQuestionIds array
                                if (preSelectedQuestionIds.includes(question.id.toString())) {
                                    checkbox.checked = true;
                                }
                                
                                checkbox.addEventListener('change', function() {
                                    updateSelectedCount();
                                    updateGroupButtonState();
                                });
                                checkboxCell.appendChild(checkbox);
                                row.appendChild(checkboxCell);
                                
                                // ID cell
                                const idCell = document.createElement('td');
                                idCell.textContent = question.id;
                                row.appendChild(idCell);
                                
                                // Category cell
                                const categoryCell = document.createElement('td');
                                const categoryBadge = document.createElement('span');
                                categoryBadge.className = 'category-badge category-' + question.category;
                                categoryBadge.textContent = question.category.charAt(0).toUpperCase() + question.category.slice(1);
                                categoryCell.appendChild(categoryBadge);
                                row.appendChild(categoryCell);
                                
                                const typeCell = document.createElement('td');
                                typeCell.textContent = question.type;
                                row.appendChild(typeCell);
                                
                                const questionCell = document.createElement('td');
                                questionCell.className = 'question-text';
                                questionCell.textContent = question.question;
                                row.appendChild(questionCell);
                                
                                tbody.appendChild(row);
                            });
                            
                            table.appendChild(tbody);
                            container.innerHTML = '';
                            container.appendChild(table);
                            
                        } else {
                            container.innerHTML = '<div class="no-questions">No ungrouped questions found in this category.</div>';
                        }
                        
                        // Initialize counter
                        updateSelectedCount();
                        updateGroupButtonState();
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        container.innerHTML = '<div class="no-questions">Error loading questions. Please try again.</div>';
                    });
            }
            
            // Update the selected questions count
            function updateSelectedCount() {
                const selectedCount = document.querySelectorAll('input[name="ungrouped_question_checkbox"]:checked').length;
                const countSpan = document.getElementById('selected-count');
                if (countSpan) {
                    countSpan.textContent = selectedCount;
                }
            }
            
            // Enable/disable group button based on selection
            function updateGroupButtonState() {
                const groupBtn = document.getElementById('group-selected-btn');
                if (groupBtn) {
                    const selectedCount = document.querySelectorAll('input[name="ungrouped_question_checkbox"]:checked').length;
                    groupBtn.disabled = selectedCount === 0;
                }
            }
            
            // Handle form submission for grouping ungrouped questions
            const groupUngroupedForm = document.getElementById('groupUngroupedForm');
            if (groupUngroupedForm) {
                groupUngroupedForm.addEventListener('submit', function(e) {
                    e.preventDefault();
                    
                    // Get all checked questions
                    const selectedQuestions = Array.from(document.querySelectorAll('input[name="ungrouped_question_checkbox"]:checked'))
                        .map(checkbox => checkbox.value);
                    
                    if (selectedQuestions.length === 0) {
                        alert('Please select at least one question');
                        return;
                    }
                    
                    const action = document.querySelector('input[name="group-action"]:checked').value;
                    
                    // Create FormData for the request
                    const formData = new FormData();
                    formData.append('action', action);
                    formData.append('question_ids', JSON.stringify(selectedQuestions));
                    
                    if (action === 'add') {
                        const groupId = document.getElementById('existing-group-select').value;
                        if (!groupId) {
                            alert('Please select a group');
                            return;
                        }
                        
                        formData.append('group_id', groupId);
                    } else {
                        const name = document.getElementById('new-group-name').value.trim();
                        const description = document.getElementById('new-group-description').value.trim();
                        
                        if (!name) {
                            alert('Group name is required');
                            return;
                        }
                        
                        formData.append('group_name', name);
                        formData.append('group_description', description);
                    }
                    
                    // Submit via AJAX
                    fetch('/admin/questions/group_questions', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert(data.message);
                            // Reload the page to show the updated groups
                            window.location.reload();
                        } else {
                            alert('Error: ' + (data.error || 'Failed to group questions'));
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('An error occurred while grouping questions');
                    });
                });
            }
            
            // Update the "View & Group Ungrouped Questions" button to open the modal
            const viewUngroupedBtn = document.querySelector('a.btn-primary.mb-3');
            if (viewUngroupedBtn) {
                viewUngroupedBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    openModal('ungroupedQuestionsModal');
                    loadUngroupedQuestionsForModal('all');
                });
            }
            
            // Load the ungrouped questions in the main view (not in modal)
            const mainUngroupedCategoryFilter = document.getElementById('main-ungrouped-category-filter');
            if (mainUngroupedCategoryFilter) {
                mainUngroupedCategoryFilter.addEventListener('change', function() {
                    loadUngroupedQuestionsForMainView(this.value);
                });
                
                // Initial load of ungrouped questions
                loadUngroupedQuestionsForMainView('all');
            }
            
            // Function to load ungrouped questions for the main view
            function loadUngroupedQuestionsForMainView(category) {
                const container = document.getElementById('main-ungrouped-container');
                if (!container) return;
                
                container.innerHTML = '<div class="loading-spinner">Loading questions...</div>';
                
                fetch(`/questions/api/ungrouped?category=${category}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('Failed to fetch questions: ' + response.status);
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.success && data.questions && data.questions.length > 0) {
                            // Group questions by category
                            const categorizedQuestions = {};
                            
                            data.questions.forEach(question => {
                                if (!categorizedQuestions[question.category]) {
                                    categorizedQuestions[question.category] = [];
                                }
                                categorizedQuestions[question.category].push(question);
                            });
                            
                            // Create HTML for each category
                            container.innerHTML = '';
                            
                            Object.keys(categorizedQuestions).forEach(category => {
                                const questions = categorizedQuestions[category];
                                const categorySection = document.createElement('div');
                                categorySection.className = 'category-section';
                                
                                // Create header with category name and count
                                const header = document.createElement('h3');
                                header.className = 'category-header';
                                header.textContent = `${category.charAt(0).toUpperCase() + category.slice(1)} Questions (${questions.length})`;
                                
                                // Add "Select All" checkbox for this category
                                const selectAllContainer = document.createElement('span');
                                selectAllContainer.style.marginLeft = '10px';
                                
                                const selectAllCheckbox = document.createElement('input');
                                selectAllCheckbox.type = 'checkbox';
                                selectAllCheckbox.className = 'select-all-checkbox';
                                
                                const selectAllLabel = document.createElement('label');
                                selectAllLabel.style.fontSize = '14px';
                                selectAllLabel.style.fontWeight = 'normal';
                                selectAllLabel.textContent = ' Select All';
                                
                                selectAllContainer.appendChild(selectAllCheckbox);
                                selectAllContainer.appendChild(selectAllLabel);
                                header.appendChild(selectAllContainer);
                                
                                // Add select all functionality
                                selectAllCheckbox.addEventListener('change', function() {
                                    const checkboxes = categorySection.querySelectorAll('input[name="main_question_checkbox"]');
                                    checkboxes.forEach(checkbox => {
                                        checkbox.checked = this.checked;
                                    });
                                    
                                    // Show/hide group button based on selection
                                    updateMainGroupButtonVisibility();
                                });
                                
                                categorySection.appendChild(header);
                                
                                // Create table
                                const table = document.createElement('table');
                                const thead = document.createElement('thead');
                                const headerRow = document.createElement('tr');
                                
                                // Add checkbox column
                                const checkboxHeader = document.createElement('th');
                                checkboxHeader.style.width = '30px';
                                headerRow.appendChild(checkboxHeader);
                                
                                headerRow.innerHTML += `
                                    <th>Number</th>
                                    <th>Question</th>
                                    <th>Type</th>
                                    <th>Answer</th>
                                    <th>Actions</th>
                                `;
                                
                                thead.appendChild(headerRow);
                                table.appendChild(thead);
                                
                                const tbody = document.createElement('tbody');
                                
                                questions.forEach(question => {
                                    const row = document.createElement('tr');
                                    
                                    // Checkbox cell
                                    const checkboxCell = document.createElement('td');
                                    const checkbox = document.createElement('input');
                                    checkbox.type = 'checkbox';
                                    checkbox.name = 'main_question_checkbox';
                                    checkbox.value = question.id;
                                    checkbox.addEventListener('change', updateMainGroupButtonVisibility);
                                    checkboxCell.appendChild(checkbox);
                                    row.appendChild(checkboxCell);
                                    
                                    // Number cell
                                    const numberCell = document.createElement('td');
                                    // For display purposes, use question ID if no number is provided
                                    numberCell.textContent = question.numb || question.id;
                                    row.appendChild(numberCell);
                                    
                                    // Question cell
                                    const questionCell = document.createElement('td');
                                    questionCell.className = 'question-text';
                                    questionCell.textContent = question.question;
                                    row.appendChild(questionCell);
                                    
                                    // Type cell
                                    const typeCell = document.createElement('td');
                                    typeCell.textContent = question.type;
                                    row.appendChild(typeCell);
                                    
                                    // Answer cell (we don't have this data in the API response, so show placeholder)
                                    const answerCell = document.createElement('td');
                                    answerCell.textContent = '...';
                                    row.appendChild(answerCell);
                                    
                                    // Action buttons
                                    const actionCell = document.createElement('td');
                                    actionCell.innerHTML = `
                                        <button onclick="editQuestion(${question.id})" class="btn" title="Edit question">
                                            <i class='bx bxs-edit'></i>
                                        </button>
                                        <button onclick="deleteQuestion(${question.id})" class="btn btn-danger" title="Delete question">
                                            <i class='bx bxs-trash'></i>
                                        </button>
                                    `;
                                    row.appendChild(actionCell);
                                    
                                    tbody.appendChild(row);
                                });
                                
                                table.appendChild(tbody);
                                categorySection.appendChild(table);
                                container.appendChild(categorySection);
                            });
                        } else {
                            container.innerHTML = '<div class="empty-state"><i class="bx bx-question-mark empty-icon"></i><p>No ungrouped questions found in this category.</p></div>';
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        container.innerHTML = '<div class="empty-state"><i class="bx bx-error-circle empty-icon"></i><p>Error loading questions. Please try again.</p></div>';
                    });
            }
            
            // Function to update main group button visibility
            function updateMainGroupButtonVisibility() {
                const groupSelectedBtn = document.getElementById('groupSelectedBtn');
                if (groupSelectedBtn) {
                    const checkedBoxes = document.querySelectorAll('input[name="main_question_checkbox"]:checked');
                    groupSelectedBtn.style.display = checkedBoxes.length > 0 ? 'inline-block' : 'none';
                }
            }
            
            // Handle the main group selected button click
            const mainGroupSelectedBtn = document.getElementById('groupSelectedBtn');
            if (mainGroupSelectedBtn) {
                mainGroupSelectedBtn.addEventListener('click', function() {
                    // Get all checked questions from main view
                    const selectedQuestions = Array.from(document.querySelectorAll('input[name="main_question_checkbox"]:checked'))
                        .map(checkbox => checkbox.value);
                    
                    if (selectedQuestions.length === 0) {
                        alert('Please select at least one question');
                        return;
                    }
                    
                    // Open ungrouped questions modal and pre-select these questions
                    openModal('ungroupedQuestionsModal');
                    loadUngroupedQuestionsForModal('all', selectedQuestions);
                });
            }
        });

        // Function to view question group details
        function viewQuestionGroup(groupId, groupName, groupDescription) {
            // Create or update a modal to display group details
            let detailsModal = document.getElementById('viewGroupDetailsModal');
            
            if (!detailsModal) {
                // Create the modal if it doesn't exist
                detailsModal = document.createElement('div');
                detailsModal.id = 'viewGroupDetailsModal';
                detailsModal.className = 'modal';
                
                detailsModal.innerHTML = `
                    <div class="modal-content" style="max-width: 900px;">
                        <div class="modal-header">
                            <h3 id="view-group-name">Group Details</h3>
                            <span class="close-modal" onclick="closeModal('viewGroupDetailsModal')">&times;</span>
                        </div>
                        <div class="modal-body">
                            <div class="group-info">
                                <h4>Basic Information</h4>
                                <p id="view-group-description" style="margin-bottom: 20px; color: #ccc;"></p>
                                
                                <div style="display: flex; margin-bottom: 20px;">
                                    <div style="background-color: rgba(255,255,255,0.1); border-radius: 8px; padding: 15px; margin-right: 10px; flex: 1; text-align: center;">
                                        <h3 id="total-questions">0</h3>
                                        <p>Total Questions</p>
                                    </div>
                                    <div style="background-color: rgba(255,255,255,0.1); border-radius: 8px; padding: 15px; margin-right: 10px; flex: 1; text-align: center;">
                                        <h3 id="question-types">0</h3>
                                        <p>Question Types</p>
                                    </div>
                                </div>
                            </div>
                            
                            <h4>Questions in this Group</h4>
                            <div class="table-container" style="max-height: 400px; overflow-y: auto;">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>ID</th>
                                            <th>Question</th>
                                            <th>Type</th>
                                            <th>Category</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody id="group-questions-table">
                                        <tr>
                                            <td colspan="5" class="text-center">Loading questions...</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn" onclick="editQuestionGroup(${groupId}, '${encodeURIComponent(groupName)}', '${encodeURIComponent(groupDescription)}')">Edit Group</button>
                            <button type="button" class="btn btn-secondary" onclick="closeModal('viewGroupDetailsModal')">Close</button>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(detailsModal);
            } else {
                // Update the modal's edit button
                const editButton = detailsModal.querySelector('.modal-footer .btn');
                editButton.setAttribute('onclick', `editQuestionGroup(${groupId}, '${encodeURIComponent(groupName)}', '${encodeURIComponent(groupDescription)}')`);
            }
            
            // Update modal content
            document.getElementById('view-group-name').textContent = groupName;
            document.getElementById('view-group-description').textContent = groupDescription || 'No description provided';
            
            // Fetch detailed group information
            fetch(`/admin/groups/${groupId}`)
                .then(response => response.json())
                .then(group => {
                    // Update question stats
                    document.getElementById('total-questions').textContent = group.questions ? group.questions.length : 0;
                    
                    // Count unique question types
                    if (group.questions && group.questions.length > 0) {
                        const types = new Set(group.questions.map(q => 
                            q.explanation && q.explanation.includes('[TYPE:') 
                                ? q.explanation.match(/\[TYPE:(.*?)\]/)[1] 
                                : 'multiple_choice'
                        ));
                        document.getElementById('question-types').textContent = types.size;
                        
                        // Populate questions table
                        const questionsTable = document.getElementById('group-questions-table');
                        questionsTable.innerHTML = '';
                        
                        group.questions.forEach(question => {
                            const row = document.createElement('tr');
                            
                            // Determine question type
                            let questionType = 'Multiple Choice';
                            if (question.explanation) {
                                if (question.explanation.includes('[TYPE:fill_blank]')) {
                                    questionType = 'Fill in Blank';
                                } else if (question.explanation.includes('[TYPE:short_answer]')) {
                                    questionType = 'Short Answer';
                                } else if (question.explanation.includes('[TYPE:matching]')) {
                                    questionType = 'Matching';
                                } else if (question.explanation.includes('[TYPE:essay]')) {
                                    questionType = 'Essay';
                                }
                            }
                            
                            row.innerHTML = `
                                <td>${question.id}</td>
                                <td class="question-text">${question.content ? question.content.replace(/"/g, '&quot;') : question.question.replace(/"/g, '&quot;')}</td>
                                <td>${questionType}</td>
                                <td><span class="category-badge category-${question.category}">${question.category.charAt(0).toUpperCase() + question.category.slice(1)}</span></td>
                                <td>
                                    <button onclick="editQuestion(${question.id})" class="btn" title="Edit question"><i class='bx bxs-edit'></i></button>
                                    <button onclick="removeFromGroup(${question.id}, ${groupId})" class="btn btn-danger" title="Remove from group"><i class='bx bxs-minus-circle'></i></button>
                                </td>
                            `;
                            
                            questionsTable.appendChild(row);
                        });
                    } else {
                        document.getElementById('question-types').textContent = '0';
                        document.getElementById('group-questions-table').innerHTML = '<tr><td colspan="5" class="text-center">No questions in this group</td></tr>';
                    }
                })
                .catch(error => {
                    console.error('Error fetching group details:', error);
                    document.getElementById('group-questions-table').innerHTML = 
                        '<tr><td colspan="5" class="text-center text-danger">Error loading questions</td></tr>';
                });
            
            // Show the modal
            openModal('viewGroupDetailsModal');
        }

        // Function to edit question group details
        function editQuestionGroup(groupId, groupName, groupDescription) {
            // Decode URI components if they were encoded
            groupName = decodeURIComponent(groupName);
            groupDescription = decodeURIComponent(groupDescription);
            
            // Create or update a modal to edit group details
            let editModal = document.getElementById('editGroupDetailsModal');
            
            if (!editModal) {
                // Create the modal if it doesn't exist
                editModal = document.createElement('div');
                editModal.id = 'editGroupDetailsModal';
                editModal.className = 'modal';
                
                editModal.innerHTML = `
                    <div class="modal-content">
                        <div class="modal-header">
                            <h3>Edit Group</h3>
                            <span class="close-modal" onclick="closeModal('editGroupDetailsModal')">&times;</span>
                        </div>
                        <div class="modal-body">
                            <form id="editGroupForm">
                                <input type="hidden" id="edit-group-id" value="">
                                <div class="form-group">
                                    <label for="edit-group-name">Group Name</label>
                                    <input type="text" id="edit-group-name" required>
                                </div>
                                <div class="form-group">
                                    <label for="edit-group-description">Description</label>
                                    <textarea id="edit-group-description" rows="3"></textarea>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-danger" id="deleteGroupBtn">Delete Group</button>
                            <button type="button" class="btn btn-secondary" onclick="closeModal('editGroupDetailsModal')">Cancel</button>
                            <button type="button" class="btn" id="saveGroupChangesBtn">Save Changes</button>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(editModal);
                
                // Setup event listeners for the buttons
                document.getElementById('saveGroupChangesBtn').addEventListener('click', function() {
                    saveGroupChanges();
                });
                
                document.getElementById('deleteGroupBtn').addEventListener('click', function() {
                    const groupId = document.getElementById('edit-group-id').value;
                    const groupName = document.getElementById('edit-group-name').value;
                    closeModal('editGroupDetailsModal');
                    deleteQuestionGroup(groupId, groupName);
                });
            }
            
            // Update form fields with current values
            document.getElementById('edit-group-id').value = groupId;
            document.getElementById('edit-group-name').value = groupName;
            document.getElementById('edit-group-description').value = groupDescription;
            
            // Show the modal
            openModal('editGroupDetailsModal');
        }

        // Function to save group changes
        function saveGroupChanges() {
            const groupId = document.getElementById('edit-group-id').value;
            const groupName = document.getElementById('edit-group-name').value.trim();
            const groupDescription = document.getElementById('edit-group-description').value.trim();
            
            // Validate inputs
            if (!groupName) {
                alert('Group name cannot be empty!');
                return;
            }
            
            // Show loading state
            const saveBtn = document.getElementById('saveGroupChangesBtn');
            const originalBtnText = saveBtn.textContent;
            saveBtn.textContent = 'Saving...';
            saveBtn.disabled = true;
            
            // Send the update request
            fetch(`/admin/groups/edit/${groupId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    name: groupName, 
                    description: groupDescription 
                }),
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Failed to update group');
            })
            .then(data => {
                // Close modal
                closeModal('editGroupDetailsModal');
                
                alert('Group updated successfully!');
                
                // Refresh page to show changes
                location.reload();
            })
            .catch(error => {
                console.error('Error saving group:', error);
                alert('An error occurred while saving the group. Please try again.');
                
                // Reset button state
                saveBtn.textContent = originalBtnText;
                saveBtn.disabled = false;
            });
        }

        // Function to delete question group
        function deleteQuestionGroup(groupId, groupName) {
            if (confirm(`Are you sure you want to delete the group "${groupName}"? This action cannot be undone.`)) {
                // Show loading state in case we need it
                const deleteBtn = document.getElementById('deleteGroupBtn');
                if (deleteBtn) {
                    deleteBtn.textContent = 'Deleting...';
                    deleteBtn.disabled = true;
                }
                
                // Send the delete request
                fetch(`/groups/delete/${groupId}`, {
                    method: 'POST'
                })
                .then(response => {
                    if (response.ok) {
                        alert(`Group "${groupName}" deleted successfully!`);
                        // Refresh the page to update the groups list
                        location.reload();
                        return;
                    }
                    throw new Error('Failed to delete group');
                })
                .catch(error => {
                    console.error('Error deleting group:', error);
                    alert('An error occurred while deleting the group. Please try again.');
                    
                    // Reset button state
                    if (deleteBtn) {
                        deleteBtn.textContent = 'Delete Group';
                        deleteBtn.disabled = false;
                    }
                });
            }
        }

        // Function to remove a question from a group without deleting the question
        function removeFromGroup(questionId, groupId) {
            if (confirm('Are you sure you want to remove this question from the group?')) {
                fetch(`/admin/groups/${groupId}/remove_question/${questionId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => {
                    if (response.ok) {
                        return response.json();
                    } else {
                        throw new Error('Failed to remove question from group');
                    }
                })
                .then(data => {
                    alert('Question removed from group successfully!');
                    
                    // If view modal is open, refresh it
                    if (document.getElementById('viewGroupDetailsModal') && 
                        document.getElementById('viewGroupDetailsModal').classList.contains('active')) {
                        // Get the current group data to refresh the view
                        const groupName = document.getElementById('view-group-name').textContent;
                        const groupDescription = document.getElementById('view-group-description').textContent;
                        
                        closeModal('viewGroupDetailsModal');
                        setTimeout(() => {
                            viewQuestionGroup(groupId, groupName, groupDescription);
                        }, 300);
                    } else {
                        // Just refresh the page
                        location.reload();
                    }
                })
                .catch(error => {
                    console.error('Error removing question from group:', error);
                    alert('An error occurred while removing the question from the group. Please try again.');
                });
            }
        }

        // Function to edit a specific question
        function editQuestion(questionId) {
            // Load the question data
            fetch(`/admin/questions/get/${questionId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Use existing question edit functionality if available
                        loadQuestionData(questionId);
                    } else {
                        alert('Error loading question: ' + (data.message || 'Unknown error'));
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while loading the question.');
                });
        }

        // Function to view question group details in the modal
        function viewQuestionGroup(groupId, groupName, groupDescription) {
            // Update modal title and description
            document.getElementById('group-view-title').textContent = groupName;
            document.getElementById('group-view-description').textContent = groupDescription || 'No description provided';
            
            // Set up buttons with correct group ID
            document.getElementById('edit-group-btn').onclick = () => editQuestionGroup(groupId, groupName, groupDescription);
            document.getElementById('delete-group-btn').onclick = () => deleteQuestionGroup(groupId, groupName);
            document.getElementById('add-questions-btn').onclick = () => openAddQuestionsModal(groupId, groupName);
            
            // Fetch and display group questions
            fetchGroupQuestions(groupId);
            
            // Open the modal
            openModal('viewQuestionGroupModal');
        }

        // Function to fetch questions for a specific group
        function fetchGroupQuestions(groupId, category = 'all') {
            const tableBody = document.getElementById('group-questions-tbody');
            tableBody.innerHTML = '<tr><td colspan="5" class="text-center">Loading questions...</td></tr>';
            
            fetch(`/admin/questions/group/${groupId}/questions?category=${category}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.questions) {
                        // Update question count
                        document.getElementById('group-question-count').textContent = data.questions.length;
                        
                        if (data.questions.length > 0) {
                            tableBody.innerHTML = '';
                            
                            // Add questions to the table
                            data.questions.forEach(question => {
                                const row = document.createElement('tr');
                                
                                // Get question type from explanation or default to Multiple Choice
                                let questionType = 'Multiple Choice';
                                if (question.explanation) {
                                    const typeMatch = question.explanation.match(/\[TYPE:(.*?)\]/);
                                    if (typeMatch) {
                                        const type = typeMatch[1].trim();
                                        questionType = type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
                                    }
                                }
                                
                                row.innerHTML = `
                                    <td>${question.numb}</td>
                                    <td class="question-text">${question.question}</td>
                                    <td>${questionType}</td>
                                    <td><span class="category-badge category-${question.category}">${question.category.charAt(0).toUpperCase() + question.category.slice(1)}</span></td>
                                    <td>
                                        <button onclick="editQuestion(${question.id})" class="btn" title="Edit question"><i class='bx bx-edit'></i></button>
                                        <button onclick="removeFromGroup(${question.id}, ${groupId})" class="btn btn-danger" title="Remove from group"><i class='bx bx-minus-circle'></i></button>
                                    </td>
                                `;
                                
                                tableBody.appendChild(row);
                            });
                        } else {
                            tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No questions in this group</td></tr>';
                        }
                    } else {
                        tableBody.innerHTML = '<tr><td colspan="5" class="text-center">Failed to load questions</td></tr>';
                    }
                })
                .catch(error => {
                    console.error('Error fetching group questions:', error);
                    tableBody.innerHTML = '<tr><td colspan="5" class="text-center">Error loading questions</td></tr>';
                });
        }

        // Function to open add questions to group modal
        function openAddQuestionsModal(groupId, groupName) {
            // Set group name and ID in the modal
            document.getElementById('add-questions-group-name').textContent = groupName;
            document.getElementById('add-questions-group-id').value = groupId;
            
            // Load available questions (questions not in this group)
            loadAvailableQuestions(groupId, 'all');
            
            // Open modal
            openModal('addQuestionsToGroupModal');
            
            // Setup category filter
            const categoryFilter = document.getElementById('add-questions-category-filter');
            categoryFilter.value = 'all';
            categoryFilter.onchange = () => loadAvailableQuestions(groupId, categoryFilter.value);
        }
        
        // Function to load available questions for adding to group
        function loadAvailableQuestions(groupId, category) {
            const container = document.querySelector('.available-questions-container');
            container.innerHTML = '<div class="loading-spinner">Loading available questions...</div>';
            
            fetch(`/admin/questions/api/available-for-group/${groupId}?category=${category}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success && data.questions && data.questions.length > 0) {
                        // Create container for questions
                        const questionsContainer = document.createElement('div');
                        questionsContainer.className = 'available-questions';
                        
                        data.questions.forEach(question => {
                            const questionItem = document.createElement('div');
                            questionItem.className = 'question-item';
                            
                            const checkbox = document.createElement('input');
                            checkbox.type = 'checkbox';
                            checkbox.name = 'available_question_ids';
                            checkbox.value = question.id;
                            checkbox.id = `available_q_${question.id}`;
                            checkbox.addEventListener('change', updateSelectedQuestionsCount);
                            
                            const label = document.createElement('label');
                            label.htmlFor = `available_q_${question.id}`;
                            
                            // Create a category badge
                            const badge = document.createElement('span');
                            badge.className = `category-badge category-${question.category}`;
                            badge.textContent = question.category.charAt(0).toUpperCase() + question.category.slice(1);
                            
                            // Add badge and question text
                            label.appendChild(badge);
                            label.appendChild(document.createTextNode(` ${question.question}`));
                            
                            questionItem.appendChild(checkbox);
                            questionItem.appendChild(label);
                            questionsContainer.appendChild(questionItem);
                        });
                        
                        container.innerHTML = '';
                        container.appendChild(questionsContainer);
                        
                        // Set up form submission
                        const form = document.getElementById('addQuestionsToGroupForm');
                        form.onsubmit = function(e) {
                            e.preventDefault();
                            addQuestionsToGroup(groupId);
                        };
                    } else {
                        container.innerHTML = '<div class="no-questions">No available questions found for this category.</div>';
                    }
                    
                    // Update the initial count
                    updateSelectedQuestionsCount();
                })
                .catch(error => {
                    console.error('Error loading available questions:', error);
                    container.innerHTML = '<div class="no-questions">Error loading questions. Please try again.</div>';
                });
        }
        
        // Function to update the count of selected questions
        function updateSelectedQuestionsCount() {
            const selectedCount = document.querySelectorAll('input[name="available_question_ids"]:checked').length;
            document.getElementById('add-questions-selected-count').textContent = selectedCount;
            
            // Enable/disable submit button based on selection
            const submitBtn = document.getElementById('add-selected-questions-btn');
            submitBtn.disabled = selectedCount === 0;
        }
        
        // Function to add selected questions to a group
        function addQuestionsToGroup(groupId) {
            // Get all selected question IDs
            const selectedQuestions = Array.from(
                document.querySelectorAll('input[name="available_question_ids"]:checked')
            ).map(checkbox => checkbox.value);
            
            if (selectedQuestions.length === 0) {
                alert('Please select at least one question');
                return;
            }
            
            // Disable button and show loading state
            const submitBtn = document.getElementById('add-selected-questions-btn');
            const originalBtnText = submitBtn.textContent;
            submitBtn.textContent = 'Adding...';
            submitBtn.disabled = true;
            
            // Send request to add questions to group
            fetch('/admin/questions/group/add-questions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    group_id: groupId,
                    question_ids: selectedQuestions
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message || 'Questions added successfully!');
                    
                    // Close the add questions modal
                    closeModal('addQuestionsToGroupModal');
                    
                    // Refresh the questions in the view modal
                    fetchGroupQuestions(groupId);
                } else {
                    alert('Error: ' + (data.error || 'Failed to add questions to group'));
                }
            })
            .catch(error => {
                console.error('Error adding questions to group:', error);
                alert('An error occurred while adding questions to the group');
            })
            .finally(() => {
                // Reset button state
                submitBtn.textContent = originalBtnText;
                submitBtn.disabled = false;
            });
        }
        
        // Function to remove a question from a group
        function removeFromGroup(questionId, groupId) {
            if (confirm('Are you sure you want to remove this question from the group?')) {
                fetch(`/admin/questions/group/remove-question`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        group_id: groupId,
                        question_id: questionId
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Refresh the questions list
                        fetchGroupQuestions(groupId);
                    } else {
                        alert('Error: ' + (data.error || 'Failed to remove question from group'));
                    }
                })
                .catch(error => {
                    console.error('Error removing question from group:', error);
                    alert('An error occurred while removing the question from the group');
                });
            }
        }

        // Function to delete a question
        function deleteQuestion(questionId) {
            if (confirm('Are you sure you want to delete this question? It will be removed from the RiddleNet game.')) {
                fetch(`/admin/questions/delete/${questionId}`, {
                    method: 'POST'
                })
                .then(response => {
                    if (response.ok) {
                        alert('Question deleted successfully!');
                        location.reload();
                    } else {
                        alert('Failed to delete question. Please try again.');
                    }
                })
                .catch(error => {
                    console.error('Error deleting question:', error);
                    alert('An error occurred while deleting the question. Please try again.');
                });
            }
        }
 