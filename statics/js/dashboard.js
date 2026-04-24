document.addEventListener("DOMContentLoaded", () => {
    if (!document.body.classList.contains("app-body")) {
        return;
    }

    window.requestAnimationFrame(() => {
        document.body.classList.add("app-ready");
    });
});
