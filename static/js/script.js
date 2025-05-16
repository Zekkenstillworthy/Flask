document.addEventListener('DOMContentLoaded', function() {
    let questionCount = 0;  
    let questionNumb = 1;
    let userScore = 0;
    let questions = []; // Will be populated from API

    //Profile Button const
    const profileLink = document.querySelector('.profile-link');
    const profileExitBtn = document.querySelector('.profile-exit-btn');

    //Leaderboard Button const
    const header = document.querySelector('.header');

    //Start RiddleNet Button const
    const startBtn = document.querySelector('.start-btn');
    const popupInfo = document.querySelector('.popup-info');
    const exitBtn = document.querySelector('.exit-btn');
    const main = document.querySelector('#dashboard');
    
    //Topology riddle Button
    const continueBtn = document.querySelector('.continue-btn');
    const quizSection = document.querySelector('.quiz-section');
    const quizBox = document.querySelector('.quiz-box');
    const nextBtn = document.querySelector('.next-btn');   
    const optionList = document.querySelector('.option-list');
    const resultBox = document.querySelector('.result-box');
    const tryAgainBtn = document.querySelector('.tryAgain-btn')
    const goHomeQuizBtn = document.querySelector('.goHome-quiz-btn'); 
    const goHomeResultBtn = document.querySelector('.goHome-result-btn'); 
    const topologySound = document.getElementById('bgSound');
    const profile = document.querySelector('#profile');
    const homeSection = document.querySelector('.home');  // Changed from '.home_box' to '.home'

    const sections = document.querySelectorAll('section');
    const navlinks = document.querySelectorAll('header nav a');

    // Intersection Observer to highlight nav links on scroll
    const options = {
        root: null,
        rootMargin: '0px',
        threshold: 0.5 // Adjust this value to determine when a section is considered "visible"
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.id || 'dashboard';
                navlinks.forEach(link => {
                    link.classList.remove('active');
                    const href = link.getAttribute('href').replace('#', '');
                    if ((href === '' && id === 'dashboard') || href === id) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }, options);

    sections.forEach(section => {
        observer.observe(section);
    });

    // Add click handlers for smooth scrolling
    document.querySelectorAll('.navbar a').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = link.getAttribute('href');
            
            // Skip for external page navigation links (starting with '/')
            if (href === '/logout' || (href.startsWith('/') && href !== '#')) {
                return; // Don't prevent default for page navigation links
            }

            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            } else {
                // Only try to find elements for anchor links (starting with #)
                const targetSection = document.querySelector(targetId);
                if (targetSection) {
                    targetSection.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }

            // Only update active state for anchor links (not page navigation)
            document.querySelectorAll('.navbar a').forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Show Profile Section
    profileLink.onclick = () => {
        profile.classList.add('active');
        sections.forEach(section => {
            if (section !== profile) {
                section.classList.add('blur'); 
                header.classList.add('blur'); 
            }
        });
        document.body.style.overflow = 'hidden'; // Disable page scrolling
    };

    // Hide Profile Section
    profileExitBtn.onclick = () => {
        profile.classList.remove('active');
        sections.forEach(section => {
            section.classList.remove('blur'); // Remove blur from all sections
        });
        header.classList.remove('blur'); 
        document.body.style.overflow = ''; // Enable page scrolling
    };

    startBtn.onclick = () => {
        // Reset state variables
        questionCount = 0;  
        questionNumb = 1;
        userScore = 0;
        popupInfo.classList.add('active');
        sections.forEach(section => {
            if (section !== profile) {
                section.classList.add('blur'); 
                header.classList.add('blur'); 
            }
        });
        document.body.style.overflow = 'hidden'; // Disable page scrolling
    };

    exitBtn.onclick = () => {
        
        popupInfo.classList.remove('active');
        sections.forEach(section => {
            section.classList.remove('blur'); // Remove blur from all sections
        });
        header.classList.remove('blur'); 
        document.body.style.overflow = ''; // Enable page scrolling 
    };

    // Fetch questions from API
    async function fetchQuestions(category = 'riddle') {
        try {
            console.log(`Attempting to fetch ${category} questions from database...`);
            
            // Try the main API endpoint first
            let response = await fetch(`/api/questions?category=${category}`);
            
            // If that fails, try the direct QuizController endpoint
            if (!response.ok) {
                console.warn(`Main API endpoint failed with ${response.status}, trying alternate endpoint...`);
                response = await fetch(`/questions?category=${category}`);
                
                if (!response.ok) {
                    throw new Error(`Failed to fetch questions from all endpoints: ${response.status} ${response.statusText}`);
                }
            }
            
            const data = await response.json();
            questions = data;
            
            console.log(`Successfully loaded ${questions.length} questions from database`);
            console.log('First question:', questions.length > 0 ? questions[0] : 'No questions found');
            
            return questions.length > 0;
        } catch (error) {
            console.error('Error fetching questions from database:', error);
            alert('Failed to load questions. Please contact an administrator or check browser console for details.');
            return false;
        }
    }

    continueBtn.onclick = async () => {
        // Reset state variables
        questionCount = 0;  
        questionNumb = 1;
        userScore = 0;
        
        // Show loading indicator
        const loadingIndicator = document.createElement('div');
        loadingIndicator.textContent = "Loading questions...";
        loadingIndicator.style.color = "#fff";
        loadingIndicator.style.textAlign = "center";
        loadingIndicator.style.marginTop = "20px";
        popupInfo.appendChild(loadingIndicator);
        
        // Fetch questions from the database before starting the quiz
        const questionsLoaded = await fetchQuestions('riddle');
        
        // Remove loading indicator
        popupInfo.removeChild(loadingIndicator);
        
        if (!questionsLoaded) {
            alert('No questions available in the database. Please try again later or contact an administrator to add questions.');
            return;
        }
        
        quizSection.classList.add('active');
        popupInfo.classList.remove('active');
        main.classList.remove('active');
        quizBox.classList.add('active');

        popupInfo.classList.remove('active');
        sections.forEach(section => {
            section.classList.remove('blur');
        });
        header.classList.remove('blur'); 
        document.body.style.overflow = 'none';
        showQuestions(0);
        questionCounter(1);
        headerScore();
    };

    tryAgainBtn.onclick = () => {
        // First make sure both are visible before changing their state
        resultBox.style.display = 'none';
        quizBox.style.display = 'block';

        // Now add/remove active classes
        quizBox.classList.add('active');
        resultBox.classList.remove('active');
        nextBtn.classList.remove('active');

        // Reset quiz state
        questionCount = 0;  
        questionNumb = 1;
        userScore = 0;
        
        // Load the first question and update displays
        showQuestions(questionCount);
        questionCounter(questionNumb);
        headerScore();
        
        console.log("Try Again button clicked: quizBox display =", quizBox.style.display, "resultBox display =", resultBox.style.display);
    };

    goHomeQuizBtn.onclick = () => {
        // Reset quiz state
        questionCount = 0;  
        questionNumb = 1;
        userScore = 0;

        setTimeout(() => {
            location.reload();
        }, 100);
                // Pause background sound first
        topologySound.pause();
        topologySound.currentTime = 0;
        topologySound.loop = false;

        document.body.style.overflow = '';
        quizSection.classList.remove('active');
        quizBox.classList.remove('active');
        nextBtn.classList.remove('active');
        homeSection.classList.add('active');
        
        
        
    };

    goHomeResultBtn.onclick = () => {
        topologySound.pause();
        topologySound.currentTime = 0;
        topologySound.loop = false;

        setTimeout(() => {
            location.reload();
        }, 100);
        document.body.style.overflow = '';
        resultBox.classList.remove('active');
        quizSection.classList.remove('active');
        quizBox.classList.remove('active');
        nextBtn.classList.remove('active');
        homeSection.classList.add('active');
        // Reset quiz state
        questionCount = 0;
        questionNumb = 1;
        userScore = 0;
        
        // Update display
        headerScore();
        
        // Reset the next button
        nextBtn.classList.remove('active');
    };
    
    nextBtn.onclick = () => {
        if (questionCount < questions.length - 1){
            questionCount++;
            showQuestions(questionCount);
            questionNumb++;
            questionCounter(questionNumb);

            nextBtn.classList.remove('active');
        } else {
            console.log("All questions answered, showing result box");
            showResultBox();
        }
    };   
    
    function showQuestions(index) {
        if (!questions || questions.length === 0) {
            console.error('No questions loaded from database');
            return;
        }
    
        const questionText = document.querySelector('.question-text');
        questionText.textContent = `${questions[index].numb}. ${questions[index].question}`;
    
        // Get question type from explanation field
        const questionExplanation = questions[index].explanation || '';
        const isBlankQuestion = questionExplanation.includes('[TYPE:fill_blank]');
        const isShortAnswerQuestion = questionExplanation.includes('[TYPE:short_answer]');
        const isMatchingQuestion = questionExplanation.includes('[TYPE:matching]');
        const isEssayQuestion = questionExplanation.includes('[TYPE:essay]');
        // Always use drag-drop style for matching questions
        const useDragDrop = true;
        
        // Update the quiz header to display the question type
        const quizHeaderSpan = document.querySelector('.quiz-header span:first-child');
        let questionType = 'Multiple Choice';
        
        if (isBlankQuestion) {
            questionType = 'Fill in the Blank';
        } else if (isShortAnswerQuestion) {
            questionType = 'Short Answer';
        } else if (isMatchingQuestion) {
            questionType = 'Drag & Drop Matching';
        } else if (isEssayQuestion) {
            questionType = 'Essay Question';
        } else if (questions[index].options && questions[index].options.length === 2 && 
                  (questions[index].options[0].includes('True') || questions[index].options[0].includes('False'))) {
            questionType = 'True/False';
        }
        
        // Update the header with the question type and category
        const category = window.location.pathname.includes('topology') ? 'Topology' : 
                        window.location.pathname.includes('troubleshoot') ? 'Troubleshooting' : 
                        window.location.pathname.includes('crimp') ? 'Cable Crimping' : 'Riddle';
        
        quizHeaderSpan.textContent = `${questionType} ${category}`;
        
        // Clear previous content
        optionList.innerHTML = '';
        
        // Hide all special question containers
        document.querySelector('.matching-container').style.display = 'none';
        document.querySelector('.essay-container').style.display = 'none';
        
        if (isBlankQuestion) {
            // Create input field for fill-in-the-blank question
            const inputField = document.createElement('div');
            inputField.className = 'blank-input-container';
            inputField.innerHTML = `
                <input type="text" class="blank-input" placeholder="Type your answer here...">
                <button class="submit-blank-btn">Submit</button>
            `;
            optionList.appendChild(inputField);
            
            // Add event listener for the submit button
            const submitBtn = document.querySelector('.submit-blank-btn');
            submitBtn.addEventListener('click', function() {
                const userInput = document.querySelector('.blank-input').value;
                checkBlankAnswer(userInput);
            });
            
            // Also allow pressing Enter to submit
            const blankInput = document.querySelector('.blank-input');
            blankInput.addEventListener('keypress', function(event) {
                if (event.key === 'Enter') {
                    event.preventDefault();
                    const userInput = document.querySelector('.blank-input').value;
                    checkBlankAnswer(userInput);
                }
            });
        } else if (isShortAnswerQuestion) {
            // Create text area for short answer question
            const inputField = document.createElement('div');
            inputField.className = 'short-answer-container';
            inputField.innerHTML = `
                <textarea class="short-answer-input" placeholder="Enter your answer here..." rows="4"></textarea>
                <p class="character-count">0 characters</p>
                <button class="submit-short-answer-btn">Submit</button>
            `;
            optionList.appendChild(inputField);
            
            // Add character count functionality
            const textArea = document.querySelector('.short-answer-input');
            const charCount = document.querySelector('.character-count');
            textArea.addEventListener('input', function() {
                const count = this.value.length;
                charCount.textContent = `${count} character${count !== 1 ? 's' : ''}`;
            });
            
            // Add event listener for the submit button
            const submitBtn = document.querySelector('.submit-short-answer-btn');
            submitBtn.addEventListener('click', function() {
                const userInput = document.querySelector('.short-answer-input').value;
                checkShortAnswer(userInput);
            });
            
            // Also allow pressing Ctrl+Enter to submit
            textArea.addEventListener('keydown', function(event) {
                if (event.key === 'Enter' && event.ctrlKey) {
                    event.preventDefault();
                    const userInput = textArea.value;
                    checkShortAnswer(userInput);
                }
            });
        } else if (isMatchingQuestion) {
            // Always use drag-drop interface for matching questions
            createDragDropMatchingInterface(questions[index]);
        } else if (isEssayQuestion) {
            // Display essay question interface
            const essayContainer = document.querySelector('.essay-container');
            essayContainer.style.display = 'block';
            
            // Reset essay input
            const essayInput = document.querySelector('.essay-input');
            essayInput.value = '';
            
            // Reset character count
            const charCount = document.querySelector('.character-count');
            charCount.textContent = '0 characters';
            
            // Reset feedback area
            const feedbackArea = document.querySelector('.essay-feedback');
            feedbackArea.innerHTML = '';
            
            // Add character count functionality
            essayInput.addEventListener('input', function() {
                const count = this.value.length;
                charCount.textContent = `${count} character${count !== 1 ? 's' : ''}`;
            });
            
            // Add event listener for the submit button
            const submitBtn = document.querySelector('.submit-essay-btn');
            submitBtn.addEventListener('click', function() {
                const userInput = document.querySelector('.essay-input').value;
                handleEssaySubmission(userInput);
            });
            
            // Also allow pressing Ctrl+Enter to submit
            essayInput.addEventListener('keydown', function(event) {
                if (event.key === 'Enter' && event.ctrlKey) {
                    event.preventDefault();
                    const userInput = this.value;
                    handleEssaySubmission(userInput);
                }
            });
            
            // Show a model answer or rubric if available
            if (questions[index].model_answer || questions[index].rubric) {
                const modelAnswerBtn = document.createElement('button');
                modelAnswerBtn.className = 'show-model-answer-btn';
                modelAnswerBtn.textContent = 'Show Guidance';
                modelAnswerBtn.addEventListener('click', function() {
                    showEssayGuidance(questions[index]);
                });
                
                const controlsDiv = document.querySelector('.essay-controls');
                controlsDiv.appendChild(modelAnswerBtn);
            }
        } else {
            // Create option elements for regular multiple choice questions
            let optionTag = '';
            if (questions[index].options && Array.isArray(questions[index].options)) {
                questions[index].options.forEach(option => {
                    optionTag += `<div class="option"><span>${option}</span></div>`;
                });
            } else {
                console.error('Invalid options format for question', questions[index]);
                optionTag = '<div class="option"><span>Error loading options</span></div>';
            }
            
            optionList.innerHTML = optionTag;
            
            // Add event listeners for multiple choice options
            const options = document.querySelectorAll('.option');
            options.forEach(item => {
                item.addEventListener('click', function() {
                    optionSelected(this);
                });
            });
        }
    
        if (topologySound) {
            topologySound.currentTime = 0;
            topologySound.play();
            topologySound.loop = true;
        }
    }

    // New function to handle fill-in-the-blank answer validation
    function checkBlankAnswer(userInput) {
        if (!userInput) {
            alert('Please enter an answer');
            return;
        }
        
        const correctAnswer = questions[questionCount].answer;
        let isCorrect = false;
        
        // Convert to lowercase and trim for case-insensitive comparison
        const normalizedInput = userInput.trim().toLowerCase();
        
        // Check if answer is an array of possible answers
        if (Array.isArray(correctAnswer)) {
            isCorrect = correctAnswer.some(answer => {
                const normalizedAnswer = answer.trim().toLowerCase();
                return normalizedAnswer === normalizedInput;
            });
        } else {
            // Single answer as a string
            const normalizedAnswer = correctAnswer.trim().toLowerCase();
            isCorrect = normalizedAnswer === normalizedInput;
        }
        
        // Display feedback
        const inputContainer = document.querySelector('.blank-input-container');
        const blankInput = document.querySelector('.blank-input');
        const submitBtn = document.querySelector('.submit-blank-btn');
        
        if (isCorrect) {
            blankInput.classList.add('correct-input');
            userScore += 1;
            headerScore();
            playCorrectSound();
        } else {
            blankInput.classList.add('incorrect-input');
            playIncorrectSound();
            
            // Show correct answer
            const feedbackDiv = document.createElement('div');
            feedbackDiv.className = 'blank-feedback';
            feedbackDiv.innerHTML = `<p>Correct answer: <strong>${Array.isArray(correctAnswer) ? correctAnswer[0] : correctAnswer}</strong></p>`;
            inputContainer.appendChild(feedbackDiv);
        }
        
        // Disable input and button
        blankInput.disabled = true;
        submitBtn.disabled = true;
        
        // Show next button
        nextBtn.classList.add('active');
    }

    // Short answer question validation
    function checkShortAnswer(userInput) {
        if (!userInput || userInput.trim() === '') {
            alert('Please enter an answer');
            return;
        }
        
        const correctAnswers = questions[questionCount].answer;
        const answerList = Array.isArray(correctAnswers) ? correctAnswers : [correctAnswers];
        let isCorrect = false;
        let bestSimilarity = 0;
        let closestAnswer = '';
        
        // Convert to lowercase and trim for case-insensitive comparison
        const normalizedInput = userInput.trim().toLowerCase();
        
        // Check exact matches first
        for (const answer of answerList) {
            const normalizedAnswer = answer.trim().toLowerCase();
            if (normalizedAnswer === normalizedInput) {
                isCorrect = true;
                closestAnswer = answer;
                bestSimilarity = 1;
                break;
            }
        }
        
        // If no exact match, check if the answer contains key phrases
        if (!isCorrect) {
            for (const answer of answerList) {
                const normalizedAnswer = answer.trim().toLowerCase();
                
                // Check if the user's answer contains the key phrase
                if (normalizedInput.includes(normalizedAnswer)) {
                    isCorrect = true;
                    closestAnswer = answer;
                    bestSimilarity = 1;
                    break;
                }
                
                // Check if any key phrase contains the user's answer
                if (normalizedAnswer.includes(normalizedInput) && normalizedInput.length > 3) {
                    isCorrect = true;
                    closestAnswer = answer;
                    bestSimilarity = 1;
                    break;
                }
                
                // Calculate similarity score for partial matches
                const similarity = calculateStringSimilarity(normalizedInput, normalizedAnswer);
                if (similarity > bestSimilarity) {
                    bestSimilarity = similarity;
                    closestAnswer = answer;
                }
            }
        }
        
        // Consider it correct if similarity is above threshold (80%)
        if (!isCorrect && bestSimilarity >= 0.8) {
            isCorrect = true;
        }
        
        // Display feedback
        const inputContainer = document.querySelector('.short-answer-container');
        const textArea = document.querySelector('.short-answer-input');
        const submitBtn = document.querySelector('.submit-short-answer-btn');
        
        if (isCorrect) {
            textArea.classList.add('correct-input');
            userScore += 1;
            headerScore();
            playCorrectSound();
        } else {
            textArea.classList.add('incorrect-input');
            playIncorrectSound();
            
            // Show correct answer
            const feedbackDiv = document.createElement('div');
            feedbackDiv.className = 'short-answer-feedback';
            
            if (bestSimilarity >= 0.6) {
                // Close but not quite right
                feedbackDiv.innerHTML = `<p>Your answer was close! Correct answer: <strong>${closestAnswer}</strong></p>`;
            } else {
                feedbackDiv.innerHTML = `<p>Correct answer: <strong>${closestAnswer || answerList[0]}</strong></p>`;
            }
            
            inputContainer.appendChild(feedbackDiv);
        }
        
        // Disable input and button
        textArea.disabled = true;
        submitBtn.disabled = true;
        
        // Show next button
        nextBtn.classList.add('active');
    }
    
    // Calculate similarity between two strings (0.0 to 1.0)
    function calculateStringSimilarity(str1, str2) {
        // If strings are identical, return 1.0
        if (str1 === str2) return 1.0;
        
        // If either string is empty, return 0.0
        if (str1.length === 0 || str2.length === 0) return 0.0;
        
        // Calculate Levenshtein distance
        const matrix = [];
        
        // Initialize matrix
        for (let i = 0; i <= str1.length; i++) {
            matrix[i] = [i];
        }
        
        for (let j = 0; j <= str2.length; j++) {
            matrix[0][j] = j;
        }
        
        // Fill matrix
        for (let i = 1; i <= str1.length; i++) {
            for (let j = 1; j <= str2.length; j++) {
                if (str1.charAt(i - 1) === str2.charAt(j - 1)) {
                    matrix[i][j] = matrix[i - 1][j - 1];
                } else {
                    matrix[i][j] = Math.min(
                        matrix[i - 1][j - 1] + 1, // substitution
                        Math.min(
                            matrix[i][j - 1] + 1, // insertion
                            matrix[i - 1][j] + 1 // deletion
                        )
                    );
                }
            }
        }
        
        // The Levenshtein distance is the bottom-right element
        const distance = matrix[str1.length][str2.length];
        
        // Calculate similarity as a value between 0 and 1
        const maxLength = Math.max(str1.length, str2.length);
        return (maxLength - distance) / maxLength;
    }

    // Function to create matching question interface
    function createMatchingInterface(question) {
        try {
            // Check if the answer is valid JSON and contains matching pairs
            let correctPairs;
            try {
                correctPairs = JSON.parse(question.answer);
                
                // Validate that parsed data is an array of objects with prompt and match properties
                if (!Array.isArray(correctPairs) || 
                    !correctPairs.every(pair => pair.item && pair.match)) {
                    throw new Error('Invalid matching question format');
                }
            } catch (parseError) {
                console.error('Error parsing matching question data:', parseError);
                
                // Fall back to multiple choice display if the answer isn't proper JSON for matching
                console.log('Falling back to multiple choice display');
                let optionTag = '<div class="option"><span>Error loading matching question</span></div>';
                optionList.innerHTML = optionTag;
                return;
            }
            
            // Create arrays of prompts and answers
            const prompts = correctPairs.map(pair => pair.item);
            const answers = correctPairs.map(pair => pair.match);
            
            // Create a mapping to track correct answers
            const correctAnswerMap = {};
            correctPairs.forEach(pair => {
                correctAnswerMap[pair.item] = pair.match;
            });
            
            // Shuffle the answers for display
            const shuffledAnswers = [...answers].sort(() => Math.random() - 0.5);
            
            // Create the matching container
            const matchingContainer = document.createElement('div');
            matchingContainer.className = 'matching-container';
            
            // Create instructions
            const instructions = document.createElement('div');
            instructions.className = 'matching-instructions';
            instructions.innerHTML = '<p>Match each item on the left with its corresponding answer on the right by selecting from the dropdown menu.</p>';
            
            // Create the table for matching
            const matchingTable = document.createElement('div');
            matchingTable.className = 'matching-table';
            
            // Add prompts and dropdown selectors
            prompts.forEach((prompt, index) => {
                const matchingRow = document.createElement('div');
                matchingRow.className = 'matching-row';
                
                const promptDiv = document.createElement('div');
                promptDiv.className = 'matching-prompt';
                promptDiv.textContent = `${index + 1}. ${prompt}`;
                
                const dropdownDiv = document.createElement('div');
                dropdownDiv.className = 'matching-dropdown';
                
                const select = document.createElement('select');
                select.className = 'matching-select';
                select.dataset.promptIndex = index;
                select.dataset.prompt = prompt;
                
                // Add empty default option
                const defaultOption = document.createElement('option');
                defaultOption.value = '';
                defaultOption.textContent = '-- Select a match --';
                select.appendChild(defaultOption);
                
                // Add all possible answers to dropdown
                shuffledAnswers.forEach((answer, i) => {
                    const option = document.createElement('option');
                    option.value = answer;
                    option.textContent = `${String.fromCharCode(65 + i)}. ${answer}`;
                    select.appendChild(option);
                });
                
                dropdownDiv.appendChild(select);
                
                // Add feedback icon space (will be populated after checking answers)
                const feedbackIcon = document.createElement('span');
                feedbackIcon.className = 'matching-feedback-icon';
                dropdownDiv.appendChild(feedbackIcon);
                
                matchingRow.appendChild(promptDiv);
                matchingRow.appendChild(dropdownDiv);
                matchingTable.appendChild(matchingRow);
            });
            
            // Create the submit button
            const submitButton = document.createElement('button');
            submitButton.className = 'matching-submit-btn';
            submitButton.textContent = 'Check Matches';
            
            // Add all elements to the container
            matchingContainer.appendChild(instructions);
            matchingContainer.appendChild(matchingTable);
            matchingContainer.appendChild(submitButton);
            
            // Add styling
            const styleElement = document.createElement('style');
            styleElement.textContent = `
                .matching-container {
                    width: 100%;
                    margin-bottom: 20px;
                }
                
                .matching-instructions {
                    margin-bottom: 15px;
                    color: #ddd;
                    font-style: italic;
                }
                
                .matching-table {
                    width: 100%;
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }
                
                .matching-row {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: 20px;
                }
                
                .matching-prompt {
                    flex: 1;
                    font-weight: bold;
                    color: #fff;
                }
                
                .matching-dropdown {
                    flex: 1;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .matching-select {
                    width: 100%;
                    padding: 8px;
                    border-radius: 4px;
                    background: rgba(255,255,255,0.1);
                    color: white;
                    border: 1px solid #444;
                }
                
                .matching-select.correct-match {
                    background-color: rgba(0,255,0,0.2);
                    border-color: #4CAF50;
                }
                
                .matching-select.incorrect-match {
                    background-color: rgba(255,0,0,0.2);
                    border-color: #F44336;
                }
                
                .matching-select.error-select {
                    border-color: #FFC107;
                    box-shadow: 0 0 0 2px rgba(255, 193, 7, 0.5);
                }
                
                .matching-submit-btn {
                    margin-top: 15px;
                    padding: 10px 15px;
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    align-self: center;
                    display: block;
                    width: fit-content;
                    font-weight: bold;
                }
                
                .matching-submit-btn:hover {
                    background-color: #0b7dda;
                }
                
                .matching-submit-btn:disabled {
                    background-color: #cccccc;
                    cursor: not-allowed;
                }
                
                .matching-feedback-icon {
                    width: 20px;
                    height: 20px;
                    display: inline-block;
                }
                
                .matching-feedback-icon.correct:after {
                    content: '✓';
                    color: #4CAF50;
                    font-weight: bold;
                }
                
                .matching-feedback-icon.incorrect:after {
                    content: '✗';
                    color: #F44336;
                    font-weight: bold;
                }
                
                .matching-result {
                    margin-top: 15px;
                    padding: 10px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                
                .matching-result.good {
                    background-color: rgba(76, 175, 80, 0.3);
                    color: white;
                }
                
                .matching-result.bad {
                    background-color: rgba(244, 67, 54, 0.3);
                    color: white;
                }
                
                .matching-correct-answers {
                    margin-top: 15px;
                    padding: 10px;
                    border-radius: 4px;
                    background-color: rgba(0, 0, 0, 0.2);
                }
                
                .matching-correct-answers h4 {
                    margin-top: 0;
                    margin-bottom: 10px;
                    color: #FFC107;
                }
                
                .matching-correct-answers ul {
                    margin: 0;
                    padding-left: 20px;
                }
                
                .matching-correct-answers li {
                    margin-bottom: 5px;
                }
            `;
            
            // Add the container and styles to the option list
            optionList.innerHTML = '';
            optionList.appendChild(styleElement);
            optionList.appendChild(matchingContainer);
            
            // Add event listener to the submit button
            submitButton.addEventListener('click', function() {
                handleMatchingSubmission(correctAnswerMap, shuffledAnswers);
            });
            
        } catch (error) {
            console.error('Error creating matching interface:', error);
            // Fall back to error message
            optionList.innerHTML = '<div class="option"><span>Error loading matching question</span></div>';
        }
    }

    // Function to handle submission of matching question answers
    function handleMatchingSubmission(correctAnswerMap, shuffledAnswers) {
        const selectElements = document.querySelectorAll('.matching-select');
        let isComplete = true;
        let userSelections = [];
        
        // Check if all items have selections
        selectElements.forEach(select => {
            if (!select.value) {
                select.classList.add('error-select');
                isComplete = false;
            } else {
                select.classList.remove('error-select');
                userSelections.push({
                    prompt: select.dataset.prompt,
                    selectedAnswer: select.value
                });
            }
        });
        
        // If not all selections made, show error and don't proceed
        if (!isComplete) {
            alert('Please select a match for each item.');
            return;
        }
        
        // Calculate score and provide feedback
        let correctCount = 0;
        userSelections.forEach((selection, index) => {
            const select = document.querySelector(`.matching-select[data-prompt="${selection.prompt}"]`);
            const feedbackIcon = select.parentElement.querySelector('.matching-feedback-icon');
            
            // Check if the answer is correct
            const isCorrect = correctAnswerMap[selection.prompt] === selection.selectedAnswer;
            
            if (isCorrect) {
                select.classList.add('correct-match');
                feedbackIcon.classList.add('correct');
                correctCount++;
            } else {
                select.classList.add('incorrect-match');
                feedbackIcon.classList.add('incorrect');
            }
            
            // Disable the select
            select.disabled = true;
        });
        
        // Calculate percentage score
        const totalQuestions = Object.keys(correctAnswerMap).length;
        const scorePercentage = Math.round((correctCount / totalQuestions) * 100);
        
        // Create result feedback
        const resultDiv = document.createElement('div');
        resultDiv.className = `matching-result ${scorePercentage >= 70 ? 'good' : 'bad'}`;
        resultDiv.innerHTML = `
            <p>You got ${correctCount} out of ${totalQuestions} matches correct (${scorePercentage}%).</p>
        `;
        
        // Create correct answers section
        const correctAnswersDiv = document.createElement('div');
        correctAnswersDiv.className = 'matching-correct-answers';
        correctAnswersDiv.innerHTML = `
            <h4>Correct Matches:</h4>
            <ul>
                ${Object.entries(correctAnswerMap).map(([prompt, match]) => 
                    `<li>${prompt} → ${match}</li>`
                ).join('')}
            </ul>
        `;
        
        // Add results to the container
        const matchingContainer = document.querySelector('.matching-container');
        matchingContainer.appendChild(resultDiv);
        matchingContainer.appendChild(correctAnswersDiv);
        
        // Disable submit button
        const submitBtn = document.querySelector('.matching-submit-btn');
        submitBtn.disabled = true;
        
        // Update user score based on percentage correct
        // This adds a proportional score for matching questions
        const scoreValue = correctCount / totalQuestions;
        userScore += scoreValue;
        headerScore(); // Update displayed score
        
        // Play sound based on score
        if (scorePercentage >= 70) {
            playCorrectSound();
        } else {
            playIncorrectSound();
        }
        
        // Show next button
        nextBtn.classList.add('active');
    }

    // Function to create draggable matching question interface
    function createDragDropMatchingInterface(question) {
        try {
            // Check if the answer is valid JSON and contains matching pairs
            let correctPairs;
            try {
                correctPairs = JSON.parse(question.answer);
                
                // Validate that parsed data is an array of objects with item and match properties
                if (!Array.isArray(correctPairs) || 
                    !correctPairs.every(pair => pair.item && pair.match)) {
                    throw new Error('Invalid matching question format');
                }
            } catch (parseError) {
                console.error('Error parsing matching question data:', parseError);
                optionList.innerHTML = '<div class="option"><span>Error loading matching question</span></div>';
                return;
            }
            
            // Create arrays of items and answers
            const leftItems = correctPairs.map(pair => pair.item);
            const rightItems = correctPairs.map(pair => pair.match);
            
            // Create a mapping to track correct answers
            const correctAnswerMap = {};
            correctPairs.forEach(pair => {
                correctAnswerMap[pair.item] = pair.match;
            });
            
            // Shuffle the answers for display
            const shuffledRightItems = [...rightItems].sort(() => Math.random() - 0.5);
            
            // Create the matching container
            const matchingContainer = document.createElement('div');
            matchingContainer.className = 'cisco-matching-container';
            
            // Create instructions
            const instructions = document.createElement('div');
            instructions.className = 'cisco-instructions';
            instructions.innerHTML = '<p>Drag the answers from the right column to match with the corresponding questions on the left.</p>';
            
            // Create the main matching area with two columns
            const matchingArea = document.createElement('div');
            matchingArea.className = 'cisco-matching-area';
            
            // Left column - questions with drop zones
            const leftColumn = document.createElement('div');
            leftColumn.className = 'cisco-column cisco-questions';
            
            // Add column headers
            const leftHeader = document.createElement('div');
            leftHeader.className = 'cisco-header';
            leftHeader.textContent = 'Questions';
            leftColumn.appendChild(leftHeader);
            
            // Right column - draggable answers
            const rightColumn = document.createElement('div');
            rightColumn.className = 'cisco-column cisco-answers';
            
            // Add column headers
            const rightHeader = document.createElement('div');
            rightHeader.className = 'cisco-header';
            rightHeader.textContent = 'Answers';
            rightColumn.appendChild(rightHeader);
            
            // Create drop zones and labels for left column
            leftItems.forEach((item, index) => {
                const questionCard = document.createElement('div');
                questionCard.className = 'cisco-question';
                
                const questionText = document.createElement('div');
                questionText.className = 'question-text';
                questionText.innerHTML = `<span class="question-number">${index + 1}.</span> ${item}`;
                questionCard.appendChild(questionText);
                
                const dropZone = document.createElement('div');
                dropZone.className = 'cisco-dropzone';
                dropZone.dataset.question = item;
                dropZone.innerHTML = '<span class="dropzone-placeholder">Drop answer here</span>';
                
                // Add event listeners for drop events
                dropZone.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    dropZone.classList.add('dragover');
                });
                
                dropZone.addEventListener('dragleave', () => {
                    dropZone.classList.remove('dragover');
                });
                
                dropZone.addEventListener('drop', (e) => {
                    e.preventDefault();
                    dropZone.classList.remove('dragover');
                    
                    // Get the dragged item id
                    const draggedId = e.dataTransfer.getData('text/plain');
                    const draggedElement = document.getElementById(draggedId);
                    
                    if (draggedElement) {
                        // Check if this drop zone already has an answer
                        const existingAnswer = dropZone.querySelector('.cisco-answer');
                        
                        // If there's already a match, move it back to right column
                        if (existingAnswer) {
                            rightColumn.appendChild(existingAnswer);
                            existingAnswer.classList.remove('matched');
                        }
                        
                        // Move the dragged element to the drop zone
                        dropZone.innerHTML = ''; // Clear placeholder
                        dropZone.appendChild(draggedElement);
                        draggedElement.classList.add('matched');
                        
                        // Update data attributes to track the match
                        dropZone.dataset.matchedItem = draggedElement.textContent;
                        draggedElement.dataset.matchedTo = item;
                    }
                });
                
                questionCard.appendChild(dropZone);
                leftColumn.appendChild(questionCard);
            });
            
            // Create draggable items for right column
            shuffledRightItems.forEach((item, index) => {
                const answerCard = document.createElement('div');
                answerCard.className = 'cisco-answer';
                answerCard.id = `cisco-answer-${index}`;
                answerCard.draggable = true;
                answerCard.textContent = item;
                
                // Add event listeners for drag events
                answerCard.addEventListener('dragstart', (e) => {
                    e.dataTransfer.setData('text/plain', answerCard.id);
                    setTimeout(() => {
                        answerCard.classList.add('dragging');
                    }, 0);
                });
                
                answerCard.addEventListener('dragend', () => {
                    answerCard.classList.remove('dragging');
                });
                
                // Touch device support
                answerCard.addEventListener('touchstart', (e) => {
                    const touch = e.targetTouches[0];
                    const offsetX = touch.clientX - answerCard.getBoundingClientRect().left;
                    const offsetY = touch.clientY - answerCard.getBoundingClientRect().top;
                    
                    answerCard.dataset.touchOffsetX = offsetX;
                    answerCard.dataset.touchOffsetY = offsetY;
                    
                    // Add a class to indicate it's being touched
                    answerCard.classList.add('touch-dragging');
                });
                
                answerCard.addEventListener('touchmove', (e) => {
                    if (!answerCard.classList.contains('touch-dragging')) return;
                    
                    e.preventDefault();
                    const touch = e.targetTouches[0];
                    const offsetX = parseInt(answerCard.dataset.touchOffsetX) || 0;
                    const offsetY = parseInt(answerCard.dataset.touchOffsetY) || 0;
                    
                    // Position the element
                    answerCard.style.position = 'absolute';
                    answerCard.style.left = `${touch.clientX - offsetX}px`;
                    answerCard.style.top = `${touch.clientY - offsetY}px`;
                    
                    // Find if we're over a drop zone
                    const dropZones = document.querySelectorAll('.cisco-dropzone');
                    let targetDropZone = null;
                    
                    dropZones.forEach(zone => {
                        const rect = zone.getBoundingClientRect();
                        if (
                            touch.clientX >= rect.left && 
                            touch.clientX <= rect.right && 
                            touch.clientY >= rect.top && 
                            touch.clientY <= rect.bottom
                        ) {
                            targetDropZone = zone;
                            zone.classList.add('dragover');
                        } else {
                            zone.classList.remove('dragover');
                        }
                    });
                    
                    answerCard.dataset.targetDropZone = targetDropZone ? targetDropZone.dataset.question : '';
                });
                
                answerCard.addEventListener('touchend', (e) => {
                    if (!answerCard.classList.contains('touch-dragging')) return;
                    
                    answerCard.classList.remove('touch-dragging');
                    answerCard.style.position = '';
                    answerCard.style.left = '';
                    answerCard.style.top = '';
                    
                    // If we have a target drop zone, move to it
                    const targetQuestion = answerCard.dataset.targetDropZone;
                    if (targetQuestion !== '') {
                        const targetDropZone = document.querySelector(`.cisco-dropzone[data-question="${targetQuestion}"]`);
                        if (targetDropZone) {
                            // Check if this drop zone already has an answer
                            const existingAnswer = targetDropZone.querySelector('.cisco-answer');
                            
                            // If there's already a match, move it back to right column
                            if (existingAnswer) {
                                rightColumn.appendChild(existingAnswer);
                                existingAnswer.classList.remove('matched');
                            }
                            
                            // Move to the drop zone
                            targetDropZone.innerHTML = ''; // Clear placeholder
                            targetDropZone.appendChild(answerCard);
                            answerCard.classList.add('matched');
                            
                            // Update data attributes
                            targetDropZone.dataset.matchedItem = answerCard.textContent;
                            answerCard.dataset.matchedTo = targetQuestion;
                        }
                    }
                    
                    // Clear all drag-over states
                    document.querySelectorAll('.cisco-dropzone').forEach(zone => {
                        zone.classList.remove('dragover');
                    });
                });
                
                rightColumn.appendChild(answerCard);
            });
            
            // Add buttons container
            const buttonsContainer = document.createElement('div');
            buttonsContainer.className = 'cisco-buttons';
            
            // Add submit button
            const submitButton = document.createElement('button');
            submitButton.className = 'cisco-submit-btn';
            submitButton.textContent = 'Submit';
            submitButton.addEventListener('click', () => {
                validateCiscoMatches(correctAnswerMap);
            });
            
            // Add reset button
            const resetButton = document.createElement('button');
            resetButton.className = 'cisco-reset-btn';
            resetButton.textContent = 'Reset';
            resetButton.addEventListener('click', () => {
                // Move all draggables back to right column
                document.querySelectorAll('.cisco-answer').forEach(answer => {
                    rightColumn.appendChild(answer);
                    answer.classList.remove('matched');
                    answer.classList.remove('correct');
                    answer.classList.remove('incorrect');
                    answer.dataset.matchedTo = '';
                    answer.draggable = true;
                });
                
                // Reset all drop zones
                document.querySelectorAll('.cisco-dropzone').forEach(dropZone => {
                    dropZone.innerHTML = '<span class="dropzone-placeholder">Drop answer here</span>';
                    dropZone.dataset.matchedItem = '';
                    dropZone.classList.remove('correct');
                    dropZone.classList.remove('incorrect');
                });
                
                // Remove any result displays
                const resultElement = matchingContainer.querySelector('.cisco-result');
                if (resultElement) resultElement.remove();
                
                // Re-enable submit button
                submitButton.disabled = false;
                submitButton.classList.remove('disabled');
            });
            
            // Add all elements to container
            matchingArea.appendChild(leftColumn);
            matchingArea.appendChild(rightColumn);
            matchingContainer.appendChild(instructions);
            matchingContainer.appendChild(matchingArea);
            
            buttonsContainer.appendChild(resetButton);
            buttonsContainer.appendChild(submitButton);
            matchingContainer.appendChild(buttonsContainer);
            
            // Clear existing content and add new elements
            optionList.innerHTML = '';
            optionList.appendChild(matchingContainer);
            
        } catch (error) {
            console.error('Error creating drag-and-drop matching interface:', error);
            optionList.innerHTML = '<div class="option"><span>Error loading matching question</span></div>';
        }
    }

    // Function to validate the cisco matches
    function validateCiscoMatches(correctAnswerMap) {
        // Get all drop zones with matches
        const dropZones = document.querySelectorAll('.cisco-dropzone');
        
        // Check if all items have been matched
        let allMatched = true;
        dropZones.forEach(dropZone => {
            if (!dropZone.querySelector('.cisco-answer')) {
                allMatched = false;
            }
        });
        
        // If not all items are matched, show alert and return
        if (!allMatched) {
            alert('Please match all items before submitting.');
            return;
        }
        
        // Prepare result object
        let correctCount = 0;
        const totalQuestions = dropZones.length;
        
        // Check each match
        dropZones.forEach(dropZone => {
            const questionText = dropZone.dataset.question;
            const correctMatch = correctAnswerMap[questionText];
            const selectedElement = dropZone.querySelector('.cisco-answer');
            const selectedMatch = selectedElement ? selectedElement.textContent : null;
            
            // Determine if the match is correct
            const isCorrect = correctMatch === selectedMatch;
            
            // Update visual feedback
            if (isCorrect) {
                correctCount++;
                dropZone.classList.add('correct');
                selectedElement.classList.add('correct');
            } else {
                dropZone.classList.add('incorrect');
                selectedElement.classList.add('incorrect');
            }
            
            // Disable dragging after checking
            selectedElement.draggable = false;
        });
        
        // Calculate score percentage
        const scorePercentage = Math.round((correctCount / totalQuestions) * 100);
        
        // Create result feedback
        const resultDiv = document.createElement('div');
        resultDiv.className = `cisco-result ${scorePercentage >= 70 ? 'success' : 'error'}`;
        resultDiv.innerHTML = `
            <p><strong>Score: ${scorePercentage}%</strong> - You got ${correctCount} out of ${totalQuestions} correct</p>
        `;
        
        // Add results to container
        const matchingContainer = document.querySelector('.cisco-matching-container');
        matchingContainer.appendChild(resultDiv);
        
        // Disable submit button
        const submitButton = document.querySelector('.cisco-submit-btn');
        submitButton.disabled = true;
        submitButton.classList.add('disabled');
        
        // Add to user score based on percentage correct
        const scoreValue = correctCount / totalQuestions;
        userScore += scoreValue;
        headerScore(); // Update displayed score
        
        // Show next button
        nextBtn.classList.add('active');
    }

    function questionCounter(index) {
        const questionTotal = document.querySelector('.question-total');
        questionTotal.textContent = `${index} of ${questions.length} Questions`;
    }

    function optionSelected(answer) {
        let userAnswer = answer.textContent;
        let correctAnswer = questions[questionCount].answer;
        let allOptions = optionList.children.length;

        // Check if this is a true/false question (only 2 options and they are True/False)
        let isTrueFalseQuestion = allOptions === 2 && 
            (optionList.children[0].textContent.trim() === "True" || optionList.children[0].textContent.trim() === "False") && 
            (optionList.children[1].textContent.trim() === "True" || optionList.children[1].textContent.trim() === "False");
        
        // Special handling for true/false questions
        if (isTrueFalseQuestion) {
            // Normalize both answers to lowercase for comparison
            let normalizedUserAnswer = userAnswer.trim().toLowerCase();
            let normalizedCorrectAnswer = Array.isArray(correctAnswer) ? 
                correctAnswer[0].trim().toLowerCase() : correctAnswer.trim().toLowerCase();
            
            if (normalizedUserAnswer === normalizedCorrectAnswer || 
                (normalizedCorrectAnswer.includes(normalizedUserAnswer))) {
                answer.classList.add('correct');
                userScore += 1;
                headerScore();
                playCorrectSound();
            } else {
                answer.classList.add('incorrect');
                playIncorrectSound();
                for (let i = 0; i < allOptions; i++) {
                    let optionText = optionList.children[i].textContent.trim().toLowerCase();
                    if (optionText === normalizedCorrectAnswer || normalizedCorrectAnswer.includes(optionText)) {
                        optionList.children[i].setAttribute('class', 'option correct');
                    }
                }
            }
        } else {
            // Original logic for other question types
            if (userAnswer == correctAnswer) {
                answer.classList.add('correct');
                userScore += 1;
                headerScore();
                playCorrectSound();
            } else {
                answer.classList.add('incorrect');
                playIncorrectSound();
                for (let i = 0; i < allOptions; i++) {
                    if (optionList.children[i].textContent == correctAnswer) {
                        optionList.children[i].setAttribute('class', 'option correct');
                    }
                }
            }
        }

        for (let i = 0; i < allOptions; i++) {
            optionList.children[i].classList.add('disabled');
        }

        nextBtn.classList.add('active');
    }

    function headerScore() {
        const headerScoreText = document.querySelector('.header-score');
        headerScoreText.textContent = `Score: ${userScore} / ${questions.length}`;
    }

    function showResultBox() {
        console.log("showResultBox function called");
        
        // First hide the quiz box completely
        quizBox.classList.remove('active');
        quizBox.style.display = 'none';
        
        // Then show the result box with higher z-index
        resultBox.style.display = 'block';
        resultBox.classList.add('active');
        resultBox.style.zIndex = '999';
        
        console.log("Display states: quizBox:", quizBox.style.display, "resultBox:", resultBox.style.display);
    
        const scoreText = document.querySelector('.score-text');
        scoreText.textContent = `Your Score ${userScore} out of ${questions.length}`;
        
        const circularProgress = document.querySelector('.circular-progress');
        const progressValue = document.querySelector('.progress-value');
        let progressStartValue = 0;
        // Ensure progressEndValue never exceeds 100%
        let progressEndValue = Math.min(Math.round((userScore / questions.length) * 100), 100);
        let speed = 20;
    
        // Reset existing animation if any
        clearInterval(window.progressAnimation);
    
        window.progressAnimation = setInterval(() => {
            progressStartValue++;
            progressValue.textContent = `${progressStartValue}%`;
            circularProgress.style.background = `conic-gradient(#FFF ${progressStartValue * 3.6}deg, rgba(255,255,255, .1) 0deg)`;
    
            if (progressStartValue >= progressEndValue) {
                clearInterval(window.progressAnimation);
            }
        }, speed);
    
        // Send score to backend to save
        fetch('/save_score', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ score: userScore })  // Send the score
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log('Score saved successfully');            
            } else {
                console.error('Error saving score:', data.message);
            }
        })
        .catch(error => console.error('Error:', error));  // Catch network or server errors
    }

    // Function to handle essay submissions
    function handleEssaySubmission(userInput) {
        if (!userInput || userInput.trim() === '') {
            alert('Please write your answer before submitting.');
            return;
        }
        
        // Get the current category from the URL
        const currentPath = window.location.pathname;
        let category = 'riddle';
        if (currentPath.includes('topology')) {
            category = 'topology';
        } else if (currentPath.includes('troubleshoot')) {
            category = 'troubleshoot';
        } else if (currentPath.includes('crimp')) {
            category = 'crimping';
        }

        // Store the essay response in an object to send to server
        const essayResponse = {
            question: questions[questionCount].question,
            answer: userInput.trim(),
            questionId: questions[questionCount].id || questionCount,
            category: category,
            timestamp: new Date().toISOString()
        };
        
        // Send the essay to the server through the API endpoint
        console.log("Attempting to submit essay to /save_essay (direct endpoint)...");
        // Try the direct endpoint first since we know QuizController is properly registered
        fetch('/save_essay', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(essayResponse)
        })
        .then(response => {
            if (!response.ok) {
                console.warn(`Direct endpoint failed with ${response.status}, trying API endpoint...`);
                // Try the API endpoint as a fallback
                console.log("Falling back to /api/save_essay...");
                return fetch('/api/save_essay', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(essayResponse)
                });
            }
            return response;
        })
        .then(response => {
            if (!response.ok) {
                console.error(`HTTP error! Status: ${response.status}`);
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                console.log('Essay submitted successfully');
            } else {
                console.error('Error submitting essay:', data.message);
            }
        })
        .catch(error => {
            console.error('Network error when submitting essay:', error);
        });
        
        // Provide feedback to user
        const feedbackArea = document.querySelector('.essay-feedback');
        feedbackArea.innerHTML = `
            <div class="essay-submission-feedback">
                <p>Your essay has been submitted for review. Essays cannot be automatically graded.</p>
                <p>You may proceed to the next question.</p>
            </div>
        `;
        
        // Add some styling to the feedback
        const styleElement = document.createElement('style');
        styleElement.textContent = `
            .essay-submission-feedback {
                margin-top: 15px;
                padding: 10px;
                background-color: rgba(76, 175, 80, 0.2);
                border-radius: 4px;
                color: white;
            }
        `;
        feedbackArea.appendChild(styleElement);
        
        // Disable the text area and submit button to prevent multiple submissions
        document.querySelector('.essay-input').disabled = true;
        document.querySelector('.submit-essay-btn').disabled = true;
        
        // Enable the next button
        nextBtn.classList.add('active');
        
        // For scoring purposes, we'll give a nominal score for essay completion
        // This would be updated later when the essay is actually graded
        userScore += 0.5;  // Give half a point for submitting
        headerScore();
        
        // Play a sound for submission
        playCorrectSound();
    }

    // Function to show essay guidance (model answer or rubric)
    function showEssayGuidance(question) {
        const feedbackArea = document.querySelector('.essay-feedback');
        let guidanceContent = '';
        
        if (question.rubric) {
            guidanceContent += `
                <div class="essay-guidance-section">
                    <h4>Grading Rubric:</h4>
                    <p>${question.rubric}</p>
                </div>
            `;
        }
        
        if (question.model_answer) {
            guidanceContent += `
                <div class="essay-guidance-section">
                    <h4>Example Answer:</h4>
                    <p>${question.model_answer}</p>
                </div>
            `;
        }
        
        if (guidanceContent) {
            feedbackArea.innerHTML = `
                <div class="essay-guidance">
                    ${guidanceContent}
                    <p class="guidance-note">Note: These are provided as reference only. Your answer may differ.</p>
                </div>
            `;
            
            // Add some styling to the guidance
            const styleElement = document.createElement('style');
            styleElement.textContent = `
                .essay-guidance {
                    margin-top: 15px;
                    padding: 10px;
                    background-color: rgba(33, 150, 243, 0.2);
                    border-radius: 4px;
                    color: white;
                }
                
                .essay-guidance-section {
                    margin-bottom: 10px;
                }
                
                .essay-guidance-section h4 {
                    margin-bottom: 5px;
                    color: #FFC107;
                }
                
                .guidance-note {
                    font-style: italic;
                    margin-top: 10px;
                    font-size: 0.9em;
                    color: #aaa;
                }
            `;
            feedbackArea.appendChild(styleElement);
        }
    }

    // Fix the audio handling to prevent AbortError
    function playSound(sound) {
        if (!sound) return;
        
        // Create a tracking variable for the current sound's play state
        if (!window.audioPlayPromises) {
            window.audioPlayPromises = new Map();
        }
        
        // If this sound is already playing and has a pending promise, wait for it
        const existingPromise = window.audioPlayPromises.get(sound);
        if (existingPromise) {
            existingPromise.then(() => {
                // Reset sound and play
                sound.currentTime = 0;
                startNewPlay(sound);
            }).catch(error => {
                // If previous promise was rejected (e.g. autoplay blocked), try again
                console.log("Previous play was interrupted:", error);
                startNewPlay(sound);
            });
        } else {
            // No existing promise, start new play
            startNewPlay(sound);
        }
        
        function startNewPlay(audio) {
            // Store the promise of the play operation
            const playPromise = audio.play();
            
            if (playPromise !== undefined) {
                window.audioPlayPromises.set(audio, playPromise);
                
                // When play is finished, remove from tracking
                playPromise.then(() => {
                    window.audioPlayPromises.delete(audio);
                }).catch(error => {
                    // Handle autoplay restrictions or other errors
                    window.audioPlayPromises.delete(audio);
                    console.log("Audio playback error or prevented by browser:", error);
                });
            }
        }
    }

    // Update the existing playCorrectSound and playIncorrectSound functions
    function playCorrectSound() {
        const sound = document.getElementById('correctSound');
        if (sound) playSound(sound);
    }

    function playIncorrectSound() {
        const sound = document.getElementById('incorrectSound');
        if (sound) playSound(sound);
    }
    
    // Also fix the background music handling to prevent AbortError
    function handleBackgroundMusic(action) {
        const bgMusic = document.getElementById('bgSound');
        if (!bgMusic) return;
        
        if (action === 'play') {
            playSound(bgMusic);
            if (bgMusic) bgMusic.loop = true;
        } else if (action === 'pause') {
            // Check if there's a pending play promise
            const existingPromise = window.audioPlayPromises && window.audioPlayPromises.get(bgMusic);
            if (existingPromise) {
                existingPromise.then(() => {
                    bgMusic.pause();
                    bgMusic.currentTime = 0;
                    window.audioPlayPromises.delete(bgMusic);
                }).catch(error => {
                    // Promise was already rejected, just clean up
                    window.audioPlayPromises.delete(bgMusic);
                });
            } else {
                // No pending promise, safe to pause
                bgMusic.pause();
                bgMusic.currentTime = 0;
            }
        }
    }

    function playCorrectSound() {
        const sound = document.getElementById('correct-sound');
        if (sound) playSound(sound);
    }

    function playIncorrectSound() {
        const sound = document.getElementById('incorrect-sound');
        if (sound) playSound(sound);
    }

    // Function to open the modal and populate it with question details
    function openEditModal(questionId, questionContent, groupName) {
        const modal = new bootstrap.Modal(document.getElementById('viewEditModal'));
        document.getElementById('questionContent').value = questionContent;
        const groupSelect = document.getElementById('questionGroup');
        
        // Clear previous options
        groupSelect.innerHTML = '';
        
        // Fetch all available groups from the backend
        fetch('/api/groups')
            .then(response => response.json())
            .then(groups => {
                // Add groups to dropdown
                groups.forEach(group => {
                    const option = document.createElement('option');
                    option.value = group.id;
                    option.textContent = group.name;
                    if (group.name === groupName) {
                        option.selected = true;
                    }
                    groupSelect.appendChild(option);
                })
                .catch(error => {
                    console.error('Error fetching groups:', error);
                    // Fallback to using the current group if API fails
                    const option = document.createElement('option');
                    option.value = groupName;
                    option.textContent = groupName;
                    option.selected = true;
                    groupSelect.appendChild(option);
                });
            });
        
        // Store question ID for later use
        document.getElementById('viewEditModal').dataset.questionId = questionId;
        
        modal.show();
    }
    
    // Event listener for saving changes
    const saveChangesButton = document.getElementById('saveChanges');
    if (saveChangesButton) {  // Add null check before adding event listener
        saveChangesButton.addEventListener('click', () => {
            const questionId = document.getElementById('viewEditModal').dataset.questionId;
            const updatedContent = document.getElementById('questionContent').value;
            const updatedGroup = document.getElementById('questionGroup').value;
        
            // Send update request to backend
            fetch(`/api/questions/${questionId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content: updatedContent, group: updatedGroup }),
            })
                .then(response => {
                    if (response.ok) {
                        alert('Question updated successfully!');
                        location.reload(); // Reload the page to reflect changes
                    } else {
                        alert('Failed to update question.');
                    }
                })
                .catch(error => {
                    console.error('Error updating question:', error);
                    alert('An error occurred while updating the question.');
                });
        });
    }
    
    // Event listener for deleting a question
    const deleteButton = document.getElementById('deleteQuestion');
    if (deleteButton) {  // Add null check before adding event listener
        deleteButton.addEventListener('click', () => {
            const questionId = document.getElementById('viewEditModal').dataset.questionId;
        
            if (confirm('Are you sure you want to delete this question?')) {
                // Send delete request to backend
                fetch(`/api/questions/${questionId}`, {
                    method: 'DELETE',
                })
                    .then(response => {
                        if (response.ok) {
                            alert('Question deleted successfully!');
                            location.reload(); // Reload the page to reflect changes
                        } else {
                            alert('Failed to delete question.');
                        }
                    })
                    .catch(error => {
                        console.error('Error deleting question:', error);
                        alert('An error occurred while deleting the question.');
                    });
            }
        });
    }

    // Function to open group modal for adding a new group
    function openAddGroupModal() {
        const modal = new bootstrap.Modal(document.getElementById('groupModal'));
        document.getElementById('groupModalLabel').textContent = 'Add New Group';
        
        // Clear all fields
        document.getElementById('groupId').value = '';
        document.getElementById('groupName').value = '';
        document.getElementById('groupDescription').value = '';
        document.getElementById('createdAt').value = 'N/A';
        
        // Hide stats cards for new groups
        document.querySelectorAll('.modal-body .card').forEach(card => {
            card.style.opacity = '0.5';
        });
        
        document.getElementById('totalQuestions').textContent = '0';
        document.getElementById('questionTypes').textContent = '0';
        document.getElementById('groupCreated').textContent = 'N/A';
        
        // Empty the questions table
        document.getElementById('groupQuestionsTable').innerHTML = '<tr><td colspan="4" class="text-center">No questions yet</td></tr>';
        
        // Show only the basic info tab
        document.getElementById('questions-tab').classList.add('disabled');
        document.getElementById('basic-info-tab').click();
        
        // Change button text to reflect creation mode
        document.getElementById('saveGroupChanges').textContent = 'Create Group';
        document.getElementById('deleteGroup').style.display = 'none';
        
        // Store empty group ID to indicate this is a new group
        document.getElementById('groupModal').dataset.groupId = '';
        
        modal.show();
    }

    // Function to open group modal for viewing/editing existing group
    function openGroupModal(groupId, groupName, groupDescription) {
        const modal = new bootstrap.Modal(document.getElementById('groupModal'));
        document.getElementById('groupModalLabel').textContent = 'Group Details';
        
        // Populate basic info
        document.getElementById('groupId').value = groupId;
        document.getElementById('groupName').value = groupName;
        document.getElementById('groupDescription').value = groupDescription;
        
        // Show stats cards for existing groups
        document.querySelectorAll('.modal-body .card').forEach(card => {
            card.style.opacity = '1';
        });
        
        // Enable questions tab
        document.getElementById('questions-tab').classList.remove('disabled');
        
        // Set button text to reflect edit mode
        document.getElementById('saveGroupChanges').textContent = 'Edit Group';
        document.getElementById('deleteGroup').style.display = 'block';
        
        // Store group ID for later use
        document.getElementById('groupModal').dataset.groupId = groupId;
        
        // Fetch detailed group information including questions
        fetch(`/api/groups/${groupId}`)
            .then(response => response.json())
            .then(group => {
                // Update created date if available
                if (group.created_at) {
                    document.getElementById('createdAt').value = group.created_at;
                    document.getElementById('groupCreated').textContent = group.created_at;
                } else {
                    document.getElementById('createdAt').value = 'N/A';
                    document.getElementById('groupCreated').textContent = 'N/A';
                }
                
                // Populate questions table
                const questionsTable = document.getElementById('groupQuestionsTable');
                if (group.questions && group.questions.length > 0) {
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
                            <td>${question.content.length > 50 ? question.content.substring(0, 50) + '...' : question.content}</td>
                            <td>${questionType}</td>
                            <td>
                                <button class="btn btn-sm btn-outline-info" onclick="openEditModal(${question.id}, '${question.content.replace(/'/g, "\\'")}', '${groupName}')">Edit</button>
                                <button class="btn btn-sm btn-outline-danger" onclick="removeFromGroup(${question.id})">Remove</button>
                            </td>
                        `;
                        questionsTable.appendChild(row);
                    });
                } else {
                    questionsTable.innerHTML = '<tr><td colspan="4" class="text-center">No questions in this group</td></tr>';
                }
            })
            .catch(error => {
                console.error('Error fetching group details:', error);
                document.getElementById('createdAt').value = 'Error loading data';
                document.getElementById('groupQuestionsTable').innerHTML = '<tr><td colspan="4" class="text-center text-danger">Error loading questions</td></tr>';
            });
        
        // Fetch group statistics
        fetch(`/api/groups/${groupId}/stats`)
            .then(response => response.json())
            .then(stats => {
                document.getElementById('totalQuestions').textContent = stats.questionCount;
                document.getElementById('questionTypes').textContent = stats.typeCount;
                if (stats.createdDate && stats.createdDate !== 'N/A') {
                    document.getElementById('groupCreated').textContent = stats.createdDate;
                }
            })
            .catch(error => {
                console.error('Error fetching group stats:', error);
                document.getElementById('totalQuestions').textContent = '?';
                document.getElementById('questionTypes').textContent = '?';
            });
        
        // Show the modal
        modal.show();
    }

    // Function to confirm deletion of a group
    function confirmDeleteGroup(groupId, groupName) {
        if (confirm(`Are you sure you want to delete the group "${groupName}" and all its questions? This action cannot be undone.`)) {
            deleteGroup(groupId);
        }
    }

    // Function to delete group and all its questions
    function deleteGroup(groupId) {
        // Show loading state
        const deleteBtn = document.getElementById('deleteGroup');
        const originalText = deleteBtn.textContent;
        deleteBtn.textContent = 'Deleting...';
        deleteBtn.disabled = true;
        
        fetch(`/api/groups/${groupId}`, {
            method: 'DELETE'
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Failed to delete group');
        })
        .then(data => {
            // Close modal if open
            const groupModal = bootstrap.Modal.getInstance(document.getElementById('groupModal'));
            if (groupModal) {
                groupModal.hide();
            }
            
            // Show success message
            alert(`Group deleted successfully! ${data.deletedQuestions} questions were also deleted.`);
            
            // Refresh the page to update the groups list
            location.reload();
        })
        .catch(error => {
            console.error('Error deleting group:', error);
            alert('An error occurred while deleting the group. Please try again.');
            
            // Reset button state
            deleteBtn.textContent = originalText;
            deleteBtn.disabled = false;
        });
    }

    // Function to remove a question from a group without deleting it
    function removeFromGroup(questionId) {
        if (confirm('Are you sure you want to remove this question from the group?')) {
            fetch(`/api/questions/${questionId}/remove-from-group`, {
                method: 'POST'
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                }
                throw new Error('Failed to remove question from group');
            })
            .then(data => {
                // Refresh group modal to show changes
                const groupId = document.getElementById('groupModal').dataset.groupId;
                if (groupId) {
                    // Get current group name and description to pass back to openGroupModal
                    const groupName = document.getElementById('groupName').value;
                    const groupDescription = document.getElementById('groupDescription').value;
                    
                    // Reopen the modal with updated data
                    const groupModal = bootstrap.Modal.getInstance(document.getElementById('groupModal'));
                    if (groupModal) {
                        groupModal.hide();
                        setTimeout(() => {
                            openGroupModal(groupId, groupName, groupDescription);
                        }, 500);
                    }
                }
            })
            .catch(error => {
                console.error('Error removing question from group:', error);
                alert('An error occurred while removing the question from the group. Please try again.');
            });
        }
    }

    // Event listener for saving group changes
    const saveGroupChangesButton = document.getElementById('saveGroupChanges');
    if (saveGroupChangesButton) {
        saveGroupChangesButton.addEventListener('click', () => {
            const groupModal = document.getElementById('groupModal');
            const groupId = groupModal.dataset.groupId;
            const groupName = document.getElementById('groupName').value;
            const groupDescription = document.getElementById('groupDescription').value;
            
            // Validate inputs
            if (!groupName.trim()) {
                alert('Group name cannot be empty!');
                return;
            }
            
            // Show loading state
            const originalText = saveGroupChangesButton.textContent;
            saveGroupChangesButton.textContent = groupId ? 'Saving...' : 'Creating...';
            saveGroupChangesButton.disabled = true;
            
            // Determine if this is an update or create operation
            const isNewGroup = !groupId;
            const url = isNewGroup ? '/api/groups' : `/api/groups/${groupId}`;
            const method = isNewGroup ? 'POST' : 'PUT';
            
            // Send request to backend
            fetch(url, {
                method: method,
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
                throw new Error(isNewGroup ? 'Failed to create group' : 'Failed to update group');
            })
            .then(data => {
                // Close modal
                const groupModal = bootstrap.Modal.getInstance(document.getElementById('groupModal'));
                if (groupModal) {
                    groupModal.hide();
                }
                
                alert(isNewGroup ? 'Group created successfully!' : 'Group updated successfully!');
                
                // Refresh page to show changes
                location.reload();
            })
            .catch(error => {
                console.error('Error saving group:', error);
                alert('An error occurred while saving the group. Please try again.');
                
                // Reset button state
                saveGroupChangesButton.textContent = originalText;
                saveGroupChangesButton.disabled = false;
            });
        });
    }

    // Event listener for deleting group from modal
    const deleteGroupButton = document.getElementById('deleteGroup');
    if (deleteGroupButton) {
        deleteGroupButton.addEventListener('click', () => {
            const groupModal = document.getElementById('groupModal');
            const groupId = groupModal.dataset.groupId;
            const groupName = document.getElementById('groupName').value;
            
            if (!groupId) {
                alert('Cannot delete a group that has not been created yet.');
                return;
            }
            
            confirmDeleteGroup(groupId, groupName);
        });
    }

    // Expose functions to global scope for onclick attributes
    window.openAddGroupModal = openAddGroupModal;
    window.openGroupModal = openGroupModal;
    window.confirmDeleteGroup = confirmDeleteGroup;
    window.removeFromGroup = removeFromGroup;
});