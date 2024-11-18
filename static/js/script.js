document.addEventListener('DOMContentLoaded', function() {
    let questionCount = 0;  
    let questionNumb = 1;
    let userScore = 0;

    //Profile Button const
    const profileLink = document.querySelector('.profile-link');
    const profileExitBtn = document.querySelector('.profile-exit-btn');

    //Leaderboard Button const
    const leaderboardLink = document.querySelector('.leaderboard-link');
    const leaderboardExitBtn = document.querySelector('.leaderboard-exit-btn');
    const aboutusSection = document.querySelector('.about-us');

    //Scores Button const
    const viewMyScoresBtn = document.querySelector(".view-my-scores-btn");
    const scoresPopup = document.getElementById("scoresPopup");
    const closeScoresPopup = document.querySelector(".close-scores-popup");

    //Start RiddleNet Button const
    const startBtn = document.querySelector('.start-btn');
    const popupInfo = document.querySelector('.popup-info');
    const exitBtn = document.querySelector('.exit-btn');
    const main = document.querySelector('.main');
    
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
    const userInfo = document.querySelector('.user-info');


// Show Profile Section
profileLink.onclick = () => {
    profile.classList.add('active');
    main.classList.add('active'); // Blur the main content
    aboutusSection.classList.add('active'); 
};
  
  // Hide Profile Section
  profileExitBtn.onclick = () => {
    profile.classList.remove('active');
    main.classList.remove('active'); // Remove blur from main content
    aboutusSection.classList.remove('active'); 

};
  
  // Show Leaderboard Section
  leaderboardLink.onclick = () => {
    leaderboard.classList.add('active');
    main.classList.add('active'); // Blur the main content
    aboutusSection.classList.add('active'); 
};
  
  // Hide Leaderboard Section
  leaderboardExitBtn.onclick = () => {
    leaderboard.classList.remove('active');
    main.classList.remove('active'); // Remove blur from main content
    aboutusSection.classList.remove('active'); 
};

viewMyScoresBtn.addEventListener("click", function() {
    scoresPopup.classList.add("active");
  });

  closeScoresPopup.addEventListener("click", function() {
    scoresPopup.classList.remove("active");
  });

  
    startBtn.onclick = () => {
        popupInfo.classList.add('active');
        main.classList.add('active');
console.log('Start')
    };

    exitBtn.onclick = () => {
        popupInfo.classList.remove('active');
        main.classList.remove('active');
        userInfo.classList.remove('active');  
    };

    continueBtn.onclick = () => {
        quizSection.classList.add('active');
        popupInfo.classList.remove('active');
        main.classList.remove('active');
        quizBox.classList.add('active');
        console.log('Continue')
        showQuestions(0);
        questionCounter(1);
        headerScore();
        document.body.style.overflow = 'hidden'; 
    };

    tryAgainBtn.onclick = () => {
        quizBox.classList.add('active');
        resultBox.classList.remove('active');
        nextBtn.classList.remove('active');

        questionCount = 0;  
        questionNumb = 1;
        userScore = 0;
        showQuestions(questionCount);
        questionCounter(questionNumb);

        headerScore();
    };

    goHomeQuizBtn.onclick = () => {
        quizSection.classList.remove('active');
        quizBox.classList.remove('active');
        nextBtn.classList.remove('active');
        homeSection.classList.add('active');
        setTimeout(() => {
            location.reload();  
        }, 200);
        questionCount = 0;  
        questionNumb = 1;
        userScore = 0;
        showQuestions(questionCount);
        questionCounter(questionNumb);
        headerScore();
    };

    goHomeResultBtn.onclick = () => {
        quizSection.classList.remove('active');
        resultBox.classList.remove('active');
        nextBtn.classList.remove('active');
        homeSection.classList.add('active');
        setTimeout(() => {
            location.reload();  
        }, 200);
        questionCount = 0;  
        questionNumb = 1;
        userScore = 0;
        showQuestions(questionCount);
        questionCounter(questionNumb);
        headerScore();
    };
    
    nextBtn.onclick = () => {
        if (questionCount < questions.length - 1){
            questionCount++;
            showQuestions(questionCount);
            questionNumb++;
            questionCounter(questionNumb);

            nextBtn.classList.remove('active');
        } else {
            showResultBox();
        }
    };   
    
    function showQuestions(index) {
        const questionText = document.querySelector('.question-text');
        questionText.textContent = `${questions[index].numb}. ${questions[index].question}`;

        let optionTag = `<div class="option"><span>${questions[index].options[0]}</span></div>
                        <div class="option"><span>${questions[index].options[1]}</span></div>
                        <div class="option"><span>${questions[index].options[2]}</span></div>
                        <div class="option"><span>${questions[index].options[3]}</span></div>`;

        optionList.innerHTML = optionTag;

        const option = document.querySelectorAll('.option');
        option.forEach(item => {
            item.addEventListener('click', function() {
                optionSelected(this);
            });
        });
    }

    function questionCounter(index) {
        const questionTotal = document.querySelector('.question-total');
        questionTotal.textContent = `${index} of ${questions.length} Questions`;
    }

    function optionSelected(answer) {
        let userAnswer = answer.textContent;
        let correctAnswer = questions[questionCount].answer;
        let allOptions = optionList.children.length;

        if (userAnswer == correctAnswer) {
            answer.classList.add('correct');
            userScore += 1;
            headerScore();
        } else {
            answer.classList.add('incorrect');
            for (let i = 0; i < allOptions; i++) {
                if (optionList.children[i].textContent == correctAnswer) {
                    optionList.children[i].setAttribute('class', 'option correct');
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
        quizBox.classList.remove('active');
        resultBox.classList.add('active');
    
        const scoreText = document.querySelector('.score-text');
        scoreText.textContent = `Your Score ${userScore} out of ${questions.length}`;
        
        const circularProgress = document.querySelector('.circular-progress');
        const progressValue = document.querySelector('.progress-value');
        let progressStartValue = -1;
        let progressEndValue = (userScore / questions.length) * 100;
        let speed = 20;
    
        let progress = setInterval(() => {
            progressStartValue++;
            progressValue.textContent = `${progressStartValue}%`;
            circularProgress.style.background = `conic-gradient(#00C3B5 ${progressStartValue * 3.6}deg, rgba(255,255,255, .1) 0deg)`;
    
            if (progressStartValue == progressEndValue) {
                clearInterval(progress)
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
                alert('Score saved successfully');            
            } else {
                alert('Error saving score:', data.message);
            }
        })
        .catch(error => console.error('Error:', error));  // Catch network or server errors
    }        
    
    
      
      
});


