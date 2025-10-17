function loading(url) {
    const loadingScreen = document.getElementById("loading-screen");
    if (loadingScreen) {
        loadingScreen.classList.add("active");
    }
    setTimeout(() => {
        window.location.href = url;
    }, 200);
}
