document.getElementById("flashcard-form").addEventListener("submit", async function(event) {
    event.preventDefault(); // Prevents form submission and page reload

    // Get input values
    const topic = document.getElementById("topic").value.trim();
    const amount = document.getElementById("amount").value.trim();

    console.log("Topic:", topic);
    console.log("Number of flashcards:", amount);

    try {
        const response = await fetch("http://127.0.0.1:5000/generate-flashcards", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                topic,
                amount
            })
        });

        const responseData = await response.json();
        const flashcards = JSON.parse(responseData.flashcards); // Fix here ✅

        if (response.ok) {
            console.log("Generated flashcards:", flashcards);
            displayFlashcards(flashcards);
        } else {
            console.error("Error from API:", responseData);
        }
    } catch (error) {
        console.error("Error fetching flashcards:", error);
    }
});



function displayFlashcards(flashcards) {
    const flashcardContainer = document.getElementById("flashcard-container");
    flashcardContainer.innerHTML = "<h3 class='text-primary'>Generated Flashcards:</h3>";

    // Ensure flashcards is an array
    if (!Array.isArray(flashcards)) {
        flashcardContainer.innerHTML += "<p class='text-danger'>Error: Flashcards data is not in the correct format.</p>";
        console.error("Expected an array, but got:", flashcards);
        return;
    }

    const flashcardDeck = document.createElement("div");
    flashcardDeck.classList.add("row", "row-cols-1", "row-cols-md-2", "g-4");

    flashcards.forEach(([question, answer], index) => {
        const card = document.createElement("div");
        card.classList.add("col");

        card.innerHTML = `
            <div class="card shadow-sm">
                <div class="card-body">
                    <h5 class="card-title">Flashcard ${index + 1}</h5>
                    <p class="card-text"><strong>Q:</strong> ${question}</p>
                    <p class="card-text"><strong>A:</strong> ${answer}</p>
                </div>
            </div>
        `;

        flashcardDeck.appendChild(card);
    });

    flashcardContainer.appendChild(flashcardDeck);
}


