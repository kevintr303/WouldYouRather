document.addEventListener("DOMContentLoaded", () => {
    const optionBoxes = document.querySelectorAll(".option-box");
    let voteSubmitted = false;
    const questionContent = document.getElementById("question-content");
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    optionBoxes.forEach(box => box.addEventListener("click", handleVoteOrNext));

    async function handleVoteOrNext(event) {
        event.preventDefault();
        if (voteSubmitted) {
            loadNextQuestion();
            return;
        }
        const optionBox = event.currentTarget;
        const questionId = optionBox.dataset.questionId;
        const option = optionBox.dataset.option;

        try {
            const response = await fetch(`/vote/${questionId}/${option}`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken
                },
                credentials: "same-origin"
            });
            const data = await response.json();

            if (response.ok) {
                animateVoteResults(data.votes_a, data.votes_b);
                voteSubmitted = true;
            } else {
                console.warn(data.error || "Error voting");
            }
        } catch (error) {
            console.error("Vote error:", error);
        }
    }

    function animateVoteResults(votesA, votesB) {
        const votesAElement = document.getElementById("option-a-votes");
        const votesBElement = document.getElementById("option-b-votes");
        const barA = document.getElementById("bar-a");
        const barB = document.getElementById("bar-b");

        if (!votesAElement || !votesBElement) return;

        const totalVotes = votesA + votesB;
        const percentA = totalVotes > 0 ? Math.round((votesA / totalVotes) * 100) : 0;
        const percentB = totalVotes > 0 ? Math.round((votesB / totalVotes) * 100) : 0;

        votesAElement.classList.remove("is-hidden");
        votesBElement.classList.remove("is-hidden");
        animatePercentage(0, percentA, votesAElement);
        animatePercentage(0, percentB, votesBElement);

        barA.classList.remove("hidden");
        barB.classList.remove("hidden");
        barA.style.width = `${percentA}%`;
        barB.style.width = `${percentB}%`;
    }

    function animatePercentage(start, end, element) {
        let current = start;
        const step = Math.max(Math.floor(end / 20), 1);
        const interval = setInterval(() => {
            current += step;
            if (current >= end) {
                current = end;
                clearInterval(interval);
            }
            element.textContent = `${current}%`;
        }, 30);
    }

    async function loadNextQuestion() {
        if (!questionContent) return;
        questionContent.classList.add("slide-out-left");

        setTimeout(async () => {
            try {
                const response = await fetch('/api/random_question');
                const data = await response.json();
                let newContent = "";

                if (data.message) {
                    newContent = `<div class="flex flex-1 items-center justify-center">
                                    <h1 class="text-2xl font-light text-slate-300">No approved questions yet.</h1>
                                  </div>`;
                } else {
                    newContent = `
                      <div class="flex flex-col md:flex-row flex-1 gap-4">
                        <div class="flex-1 flex flex-col items-center justify-center text-center p-6 md:w-1/2 w-full rounded-lg shadow-lg bg-slate-700 text-white cursor-pointer relative option-box" data-option="a" data-question-id="${data.id}">
                          <h1 class="text-3xl font-light p-6" id="option-a-text">${data.option_a}</h1>
                          <p class="text-2xl font-semibold mb-6 is-hidden" id="option-a-votes"></p>
                          <div id="bar-a" class="result-bar hidden"></div>
                        </div>
                        <div class="flex-1 flex flex-col items-center justify-center text-center p-6 md:w-1/2 w-full rounded-lg shadow-lg bg-slate-700 text-white cursor-pointer relative option-box" data-option="b" data-question-id="${data.id}">
                          <h1 class="text-3xl font-light p-6" id="option-b-text">${data.option_b}</h1>
                          <p class="text-2xl font-semibold mb-6 is-hidden" id="option-b-votes"></p>
                          <div id="bar-b" class="result-bar hidden"></div>
                        </div>
                      </div>
                    `;
                }

                questionContent.innerHTML = newContent;
                voteSubmitted = false;

                questionContent.classList.remove("slide-out-left");
                questionContent.classList.add("slide-in-right");
                setTimeout(() => questionContent.classList.remove("slide-in-right"), 500);

                const newOptionBoxes = document.querySelectorAll(".option-box");
                newOptionBoxes.forEach(box => box.addEventListener("click", handleVoteOrNext));
            } catch (error) {
                console.error("Error loading next question:", error);
            }
        }, 400);
    }

    const questionForm = document.getElementById("question-form");
    const formStatus = document.getElementById("form-status");
    const submitButton = document.getElementById("submit-btn");

    questionForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const optionAInput = document.getElementById("option_a");
        const optionBInput = document.getElementById("option_b");
        const optionA = optionAInput.value;
        const optionB = optionBInput.value;

        if (!optionA || !optionB) {
            showFormStatus("Please fill in both options", "error");
            return;
        }

        submitButton.disabled = true;
        submitButton.textContent = "Submitting...";

        try {
            const formData = new FormData(questionForm);
            const response = await fetch("/ask", {
                method: "POST",
                body: formData,
                credentials: "same-origin"
            });
            if (response.ok) {
                showFormStatus("Your question has been submitted for approval!", "success");
                questionForm.reset();
                setTimeout(() => {
                    const askModal = document.getElementById('ask-modal');
                    const modalContent = askModal.querySelector('.modal-content');
                    modalContent.classList.remove('modal-fade-in');
                    modalContent.classList.add('modal-fade-out');
                    setTimeout(() => {
                        askModal.classList.add('hidden');
                        modalContent.classList.remove('modal-fade-out');
                        formStatus.classList.add("hidden");
                    }, 300);
                }, 2000);
            } else if (response.status === 429) {
                showFormStatus("Too Many Requests (rate limit exceeded)", "error");
            } else {
                showFormStatus("Error submitting your question. Please try again.", "error");
            }
        } catch (error) {
            console.error("Form submission error:", error);
            showFormStatus("An error occurred. Please try again.", "error");
        }

        submitButton.disabled = false;
        submitButton.textContent = "Submit Question";
    });

    function showFormStatus(message, type) {
        formStatus.textContent = message;
        formStatus.classList.remove("hidden");
        if (type === "success") {
            formStatus.className = "mb-4 text-sm text-green-400";
        } else {
            formStatus.className = "mb-4 text-sm text-red-400";
        }
    }
});
