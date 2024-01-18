// Add a new text box for legal questions
function addTextBox() {
    var newTextBoxDiv = document.createElement('div');

    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'legalQuestion';
    newTextBoxDiv.appendChild(input);

    var removeBtn = document.createElement('button');
    removeBtn.textContent = 'x';
    removeBtn.className = 'btn btn-remove';
    removeBtn.onclick = function () { removeTextBox(removeBtn); };
    newTextBoxDiv.appendChild(removeBtn);

    document.getElementById('legalQuestionsDiv').appendChild(newTextBoxDiv);
}


// Remove a text box for legal questions
function removeTextBox(btn) {
    btn.parentNode.remove();
}


// Summarize button action
document.getElementById('summarizeBtn').addEventListener('click', function () {
    var legalSituation = document.getElementById('legalSituation').value;

    fetch('/getSummary', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(
            {
                "legal_situation": legalSituation,
                "language": "German",
                "user_id": 123456
            }
        )
    })
        .then(function (response) {
            if (response.ok) {
                return response.json(); // Parse the JSON response
            } else {
                throw new Error('Network response was not ok');
            }
        })
        .then(function (data) {
            var summary = data.summary_enum[0].content;
            document.getElementById('summaryResult').innerText = summary;
        })
        .catch(function (error) {
            console.error('Error:', error);
            document.getElementById('summaryResult').innerText = error;
        });
});


// Articles button action
document.getElementById('getArticlesBtn').addEventListener('click', function () {
    var legalSituation = document.getElementById('legalSituation').value;
    var legalQuestionElements = document.getElementsByClassName('legalQuestion');

    // Create an array of legal questions in the expected format
    var legalQuestions = [];
    for (var i = 0; i < legalQuestionElements.length; i++) {
        var questionText = legalQuestionElements[i].value;
        var questionObject = {
            "number": i + 1, // Property names enclosed in double quotes
            "question": questionText // Property names enclosed in double quotes
        };
        legalQuestions.push(questionObject);
    }

    // Validate input on the frontend
    if (!legalSituation || legalQuestions.length === 0) {
        alert('Please fill in all required fields.');
        return;
    }

    var userRequest = {
        "user_id": 123456, // Property names enclosed in double quotes
        "request_id": 1234349, // Property names enclosed in double quotes
        "language": "German", // Property names enclosed in double quotes
        "legal_situation": legalSituation, // Property names enclosed in double quotes
        "legal_questions": legalQuestions // Property names enclosed in double quotes
    };

    fetch('/getArticles', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userRequest)
    })
        .then(response => {
            if (response.ok) {
                return response.json(); // Parse the response as JSON
            } else {
                throw new Error('Network response was not ok');
            }
        })
        .then(data => {
            const container = document.getElementById('dropdownContainer');
            container.innerHTML = ''; // Clear previous results

            data.legal_questions.forEach(question => {
                question.articles.forEach(article => {
                    article.paragraphs.forEach(paragraph => {
                        // Create dropdown menu for each paragraph
                        const menuItem = document.createElement('div');
                        
                        const menuTitle = `[${question.question_ref}] ${paragraph.bookName} Art. ${paragraph.articleNum}${paragraph.articleNumMinor ? paragraph.articleNumMinor : ''} Abs. ${paragraph.paragraphNum}${paragraph.paragraphNumMinor ? paragraph.paragraphNumMinor : ''}`;
                        
                        menuItem.innerHTML = `<button class="dropdown-btn">${menuTitle}</button><div class="dropdown-content">${paragraph.paragraphText}</div>`;

                        container.appendChild(menuItem);
                    });
                });
            });
        })
        .catch(error => {
            console.error('Error:', error);
            // Handle errors here
        });
});


// Get Paragraphs action
document.getElementById("getParagraphForm").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent the default form submission behavior

    // Get form input values
    var bookName = document.getElementById("bookName").value.trim();
    var articleNum = parseInt(document.getElementById("articleNum").value);
    var articleNumMinor = document.getElementById("articleNumMinor").value;
    var paragraphNum = parseInt(document.getElementById("paragraphNum").value);

    // Prepare the data to send in the GET request
    var requestData = {
        bookName: bookName,
        articleNum: articleNum,
        articleNumMinor: articleNumMinor.trim() === "" ? null : articleNumMinor.trim(),
        paragraphNum: isNaN(paragraphNum) ? null : paragraphNum
    };

    // Create a POST request to the "/getParagraphs" endpoint
    fetch("/getParagraphs", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json' // Set the content type if sending JSON data
        },
        body: JSON.stringify(requestData) // Convert the data to JSON format
    })
        .then(function (response) {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error("Request failed with status: " + response.status);
            }
        })
        .then(function (data) {
            var paragraphResult = document.getElementById("paragraphResult");
            paragraphResult.innerHTML = JSON.stringify(data, null, 2); // Use null and 2 for pretty-printing

        })
        .catch(function (error) {
            var paragraphResult = document.getElementById("paragraphResult");
            paragraphResult.innerHTML = "ERROR: Unable to fetch data. Please try again later.";
        });
});


// DROP DOWN MENU 

document.addEventListener('click', function (e) {
    // Check if the clicked element is a dropdown button
    if (e.target.classList.contains('dropdown-btn')) {
        // Close any already open dropdown content
        document.querySelectorAll('.dropdown-content').forEach(function (content) {
            if (content !== e.target.nextElementSibling) {
                content.style.display = 'none';
            }
        });

        // Toggle the display of the clicked dropdown content
        var content = e.target.nextElementSibling;
        content.style.display = content.style.display === 'block' ? 'none' : 'block';
    } else {
        // If the clicked element is not a dropdown button, close all dropdowns
        document.querySelectorAll('.dropdown-content').forEach(function (content) {
            content.style.display = 'none';
        });
    }
});

// document.addEventListener('click', function (e) {
//     if (e.target.classList.contains('dropdown-btn')) {
//         // Close all dropdowns
//         document.querySelectorAll('.dropdown-content').forEach(function (content) {
//             content.style.display = 'none';
//             content.previousElementSibling.classList.remove('toggle');
//         });

//         // Toggle the clicked dropdown content
//         var content = e.target.nextElementSibling;
//         if (content.style.display === 'none') {
//             content.style.display = 'block';
//             e.target.classList.add('toggle');
//         } else {
//             content.style.display = 'none';
//             e.target.classList.remove('toggle');
//         }
//     } else {
//         // Clicking outside of a dropdown closes all dropdowns
//         document.querySelectorAll('.dropdown-content').forEach(function (content) {
//             content.style.display = 'none';
//             content.previousElementSibling.classList.remove('toggle');
//         });
//     }
// });
