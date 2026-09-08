function startPlatform() {
    alert("Welcome to PlaceMate AI!");
}
// =====================================
// PLACEMATE AI - FINAL UI ANIMATIONS
// =====================================

document.addEventListener("DOMContentLoaded", function () {

    // Smooth page load
    document.body.style.opacity = "0";

    setTimeout(() => {
        document.body.style.transition = "opacity 0.5s ease";
        document.body.style.opacity = "1";
    }, 100);

});