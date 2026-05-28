const loginForm = document.getElementById("login-form");
const loginMessage = document.getElementById("login-message");

function setLoginMessage(text, isError = false) {
  loginMessage.textContent = text;
  loginMessage.style.color = isError ? "#b91c1c" : "#047857";
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setLoginMessage("");

  const formData = new FormData(loginForm);
  const payload = {
    email: formData.get("email"),
    password: formData.get("password"),
  };

  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (!response.ok) {
      setLoginMessage(result.error || "Login failed", true);
      return;
    }

    sessionStorage.setItem("userId", String(result.user.id));
    sessionStorage.setItem("userRole", result.user.role);
    sessionStorage.setItem("userEmail", result.user.email);

    if (result.user.role === "student") {
      setLoginMessage("Login successful. Redirecting to student home...");
      setTimeout(() => {
        window.location.href = "/student/home";
      }, 700);
      return;
    }

    setLoginMessage("Login successful. Redirecting to recruiter home...");
    setTimeout(() => {
      window.location.href = "/recruiter/home";
    }, 700);
  } catch {
    setLoginMessage("Login failed", true);
  }
});
