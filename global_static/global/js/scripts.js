function loading(url) {
    const loadingScreen = document.getElementById("loading-screen");
    if (loadingScreen) {
        loadingScreen.classList.add("active");
    }

    if (url) {
        setTimeout(() => {
            window.location.href = url;
        }, 200);
    }
}


document.addEventListener("DOMContentLoaded", () => {
    const alerts = document.querySelectorAll(".alert-message");
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = "opacity 0.6s, transform 0.6s";
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-10px)";
            setTimeout(() => alert.remove(), 600);
        }, 4000);
    });
});
