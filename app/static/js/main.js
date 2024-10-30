console.log("Welcome to the Flask Project!");

function toggleReplies() {
    const repliesSection = document.querySelector(".replies");
    const toggleButton = document.querySelector(".toggle-replies");

    if (repliesSection.style.display === "none") {
        repliesSection.style.display = "block";
        toggleButton.textContent = "Hide Replies";
    } else {
        repliesSection.style.display = "none";
        toggleButton.textContent = "Show Replies";
    }
}
