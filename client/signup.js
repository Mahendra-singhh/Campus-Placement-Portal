const signupForm = document.getElementById("signup-form");
const signupMessage = document.getElementById("signup-message");

function setSignupMessage(text, isError = false) {
  signupMessage.textContent = text;
  signupMessage.style.color = isError ? "#b91c1c" : "#047857";
}

signupForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setSignupMessage("");

  const formData = new FormData(signupForm);
  const payload = {
    role: formData.get("role"),
    email: formData.get("email"),
    password: formData.get("password"),
  };

  try {
    const response = await fetch("/api/auth/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (!response.ok) {
      setSignupMessage(result.error || "Sign up failed", true);
      return;
    }

    signupForm.reset();
    setSignupMessage("Sign up successful. Redirecting to login...");
    setTimeout(() => {
      window.location.href = "/login";
    }, 900);
  } catch {
    setSignupMessage("Sign up failed", true);
  }
});
