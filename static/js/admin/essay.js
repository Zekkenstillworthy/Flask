      document.addEventListener('DOMContentLoaded', function() {
    // Get the modal
    const modal = document.getElementById("essayModal");
    const editModal = document.getElementById("editEssayModal");
    
    // Check if modals exist
    if (!editModal) {
        console.error("Edit modal not found in the DOM!");
    }

        // Get all buttons that open the modal
        const viewButtons = document.querySelectorAll(".view-essay-btn");
        const editButtons = document.querySelectorAll(".edit-essay-btn");
        const tableRows = document.querySelectorAll("tbody tr[data-id]");
        
        // Log the number of buttons found
        console.log(`Found ${editButtons.length} edit buttons`);

        // Get the <span> element that closes the modal
        const closeBtn = document.querySelector(".close");
        const closeEditBtn = document.getElementById("edit-close");
        const closeModalBtn = document.getElementById("close-modal-btn");
        const editCancelBtn = document.getElementById("edit-cancel-btn");        // Disable automatic row clicks that open the modal

        // When the user clicks on a view button, open the modal
        viewButtons.forEach(button => {
            button.addEventListener("click", function (e) {
                e.stopPropagation(); // Prevent row click event
                const essayId = this.getAttribute("data-id");
                const username = this.getAttribute("data-username");
                const question = this.getAttribute("data-question");
                const answer = this.getAttribute("data-answer");
                const category = this.getAttribute("data-category");
                const date = this.getAttribute("data-date");
                const status = this.getAttribute("data-status");
                const score = this.getAttribute("data-score");

                // Highlight the row
                document.querySelectorAll("tbody tr").forEach(tr => {
                    tr.classList.remove("highlight-row");
                });
                const parentRow = this.closest("tr");
                if (parentRow) {
                    parentRow.classList.add("highlight-row");
                }

                // Populate modal content
                document.getElementById("essay-id").textContent = essayId;
                document.getElementById("essay-username").textContent = username;
                document.getElementById("essay-question").textContent = question;
                document.getElementById("essay-answer").textContent = answer;
                document.getElementById("essay-category").textContent = category;
                document.getElementById("essay-date").textContent = date;
                document.getElementById("essay-status").textContent = status;
                document.getElementById("essay-score").textContent = score || "Not graded";
                document.getElementById("grade-input").value = score;

                // Show modal with animation
                modal.style.display = "block";
            });
        });        // Edit button functionality
        editButtons.forEach(button => {
            button.addEventListener("click", function (e) {
                e.stopPropagation(); // Prevent row click event
                const essayId = this.getAttribute("data-id");
                console.log("Edit button clicked for essay ID:", essayId);
                
                // Get the parent row to extract data directly from the table
                const row = this.closest("tr");
                const questionExcerpt = row.querySelector(".essay-excerpt").getAttribute("title");
                const category = row.querySelector("td:nth-child(3)").textContent;
                
                // Try to fetch from API first, but use table data as fallback
                fetch(`/api/essays/${essayId}`)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error("API response was not ok");
                        }
                        return response.json();
                    })
                    .then(data => {
                        document.getElementById("edit-essay-id").value = data.id;
                        document.getElementById("edit-question").value = data.question;
                        document.getElementById("edit-answer").value = data.answer;
                        document.getElementById("edit-category").value = data.category;

                        // Show modal
                        editModal.style.display = "block";
                    })
                    .catch(error => {
                        console.error("Error fetching essay details:", error);
                        
                        // Fallback: use data from the table and open modal
                        document.getElementById("edit-essay-id").value = essayId;
                        document.getElementById("edit-question").value = questionExcerpt || "";
                        
                        // Since we can't get the full answer from the table, leave it blank
                        // The user will need to enter it again
                        document.getElementById("edit-answer").value = "";
                        document.getElementById("edit-category").value = category.trim();

                        // Show modal even if fetch fails
                        editModal.style.display = "block";
                        
                    });
            });
        });

        // Delete confirmation
        document.querySelectorAll(".delete-essay-btn").forEach(button => {
            button.addEventListener("click", function (e) {
                e.stopPropagation(); // Prevent row click event
                e.preventDefault();

                if (confirm("Are you sure you want to delete this essay response? This action cannot be undone.")) {
                    this.closest("form").submit();
                }
            });
        });

        // Form submission for edit
        const editForm = document.getElementById("edit-essay-form");
        if (editForm) {
            editForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const essayId = document.getElementById("edit-essay-id").value;
            const question = document.getElementById("edit-question").value;
            const answer = document.getElementById("edit-answer").value;
            const category = document.getElementById("edit-category").value;

            if (!question.trim() || !answer.trim() || !category.trim()) {
                alert("Please fill in all required fields.");
                return;
            }

            fetch(`/api/essays/${essayId}/edit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    question: question,
                    answer: answer,
                    category: category
                })
            })
                .then(response => {
                    if (response.ok) {
                        alert("Essay updated successfully!");
                        location.reload();
                    } else {
                        throw new Error("Failed to update essay");
                    }
                })                .catch(error => {
                    console.error("Error updating essay:", error);
                    alert("Failed to update essay. Please try again.");
                });
            });
        }

        // Close modal functionality
        closeBtn.onclick = function () { modal.style.display = "none"; }
        closeModalBtn.onclick = function () { modal.style.display = "none"; }
        closeEditBtn.onclick = function () { editModal.style.display = "none"; }
        editCancelBtn.onclick = function () { editModal.style.display = "none"; }

        // When the user clicks anywhere outside of the modal, close it
        window.onclick = function (event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
            if (event.target == editModal) {
                editModal.style.display = "none";
            }
        }

        // Handle saving the grade
        document.getElementById("save-grade-btn").addEventListener("click", function () {
            const essayId = document.getElementById("essay-id").textContent;
            const score = document.getElementById("grade-input").value;

            if (score === "" || isNaN(score) || score < 0 || score > 100) {
                alert("Please enter a valid score between 0 and 100");
                return;
            }

            // Send grade to server
            fetch(`/api/essays/${essayId}/grade`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ score: score })
            })
                .then(response => {
                    if (response.ok) {
                        alert("Grade saved successfully!");
                        // Update the UI to reflect the new grade
                        document.getElementById("essay-status").textContent = "Reviewed";
                        document.getElementById("essay-score").textContent = score;

                        // Update the table row
                        const tableRow = document.querySelector(`button[data-id="${essayId}"]`).closest("tr");
                        if (tableRow) {
                            tableRow.querySelector("td:nth-child(6)").textContent = score;
                            const statusElement = tableRow.querySelector(".status");
                            statusElement.textContent = "Reviewed";
                            statusElement.classList.remove("pending");
                            statusElement.classList.add("reviewed");
                        }
                    } else {
                        throw new Error("Failed to save grade");
                    }
                })
                .catch(error => {
                    console.error("Error saving grade:", error);
                    alert("Failed to save grade. Please try again.");
                });
        });        // Sidebar toggle for mobile
        const sidebarToggle = document.getElementById("sidebar-toggle");
        const sidebar = document.getElementById("sidebar");

        if (sidebarToggle) {
            sidebarToggle.addEventListener("click", function () {
                sidebar.classList.toggle("active");
            });
        }        
        // Add direct way to open the modal for debugging
});  

   