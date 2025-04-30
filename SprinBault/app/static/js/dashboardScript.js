async function logout() {
    await fetch("/logout", { method: "POST" });

    document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "is_admin=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
    document.cookie = "email=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";

    localStorage.removeItem("email");
    sessionStorage.removeItem("email");

    window.location.href = "/";
}

// Token refresh
setInterval(() => {
    fetch('/refresh-token', { method: 'POST' });
}, 60000);