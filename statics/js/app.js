(() => {
    function ensureToastRoot() {
        let root = document.getElementById("toast-root");
        if (!root) {
            root = document.createElement("div");
            root.id = "toast-root";
            root.className = "toast-root";
            document.body.appendChild(root);
        }
        return root;
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#39;");
    }

    async function parseResponse(response) {
        const contentType = response.headers.get("content-type") || "";
        if (contentType.includes("application/json")) {
            return response.json();
        }

        const text = await response.text();
        return text ? { detail: text } : null;
    }

    async function request(url, options = {}) {
        const headers = new Headers(options.headers || {});
        const config = {
            credentials: "same-origin",
            ...options,
            headers,
        };

        if (config.body && !(config.body instanceof FormData) && !headers.has("Content-Type")) {
            headers.set("Content-Type", "application/json");
        }

        const response = await fetch(url, config);
        const payload = await parseResponse(response);

        if (!response.ok) {
            const detail =
                payload?.detail ||
                payload?.message ||
                `Request failed with status ${response.status}`;

            if (response.status === 401 && window.location.pathname !== "/app/login") {
                window.location.assign("/app/login");
            }

            throw new Error(detail);
        }

        return payload;
    }

    function toast(message, type = "success") {
        const root = ensureToastRoot();
        const item = document.createElement("div");
        item.className = `toast toast--${type}`;
        item.textContent = message;
        root.appendChild(item);

        requestAnimationFrame(() => {
            item.classList.add("is-visible");
        });

        window.setTimeout(() => {
            item.classList.remove("is-visible");
            window.setTimeout(() => item.remove(), 220);
        }, 2600);
    }

    function setSidebarState(isOpen) {
        document.body.classList.toggle("sidebar-open", isOpen);
        const toggle = document.querySelector("[data-sidebar-toggle]");
        if (toggle) {
            toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
        }
    }

    function initSidebar() {
        const sidebar = document.getElementById("sidebar");
        if (!sidebar) {
            return;
        }

        const toggle = document.querySelector("[data-sidebar-toggle]");
        const overlay = document.querySelector("[data-sidebar-overlay]");

        toggle?.addEventListener("click", () => {
            setSidebarState(!document.body.classList.contains("sidebar-open"));
        });

        overlay?.addEventListener("click", () => {
            setSidebarState(false);
        });

        window.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                setSidebarState(false);
            }
        });
    }

    function initLogout() {
        const button = document.querySelector("[data-logout-button]");
        if (!button) {
            return;
        }

        button.addEventListener("click", async () => {
            button.disabled = true;
            try {
                await request("/api/auth/logout", { method: "POST" });
            } catch (error) {
                console.error(error);
            } finally {
                window.location.assign("/app/login");
            }
        });
    }

    function initLogin() {
        const form = document.getElementById("loginForm");
        if (!form) {
            return;
        }

        const usernameInput = document.getElementById("username");
        const passwordInput = document.getElementById("password");
        const message = document.getElementById("loginMessage");
        const submitButton = form.querySelector('button[type="submit"]');

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            submitButton.disabled = true;
            submitButton.textContent = "Signing in...";
            message.textContent = "";
            message.dataset.state = "";

            try {
                const payload = await request("/api/auth/login", {
                    method: "POST",
                    body: JSON.stringify({
                        username: usernameInput.value.trim(),
                        password: passwordInput.value,
                    }),
                });

                message.textContent = `Welcome back, ${payload.full_name}. Redirecting...`;
                message.dataset.state = "success";
                toast("Signed in successfully.");

                const nextUrl =
                    new URLSearchParams(window.location.search).get("next") ||
                    "/app/dashboard/";
                window.setTimeout(() => {
                    window.location.assign(nextUrl);
                }, 250);
            } catch (error) {
                message.textContent = error.message;
                message.dataset.state = "error";
                toast(error.message, "error");
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = "Sign in";
            }
        });
    }

    window.rms = {
        escapeHtml,
        request,
        toast,
    };

    document.addEventListener("DOMContentLoaded", () => {
        initSidebar();
        initLogout();
        initLogin();
    });
})();
