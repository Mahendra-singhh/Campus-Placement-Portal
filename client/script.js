const API_BASE_URL = "/api";

const form = document.getElementById("user-form");
const messageEl = document.getElementById("form-message");
const userListEl = document.getElementById("user-list");
const refreshBtn = document.getElementById("refresh-btn");

function showMessage(text, isError = false) {
  messageEl.textContent = text;
  messageEl.style.color = isError ? "#b91c1c" : "#047857";
}

function renderUsers(users) {
  userListEl.innerHTML = "";

  if (!users.length) {
    userListEl.innerHTML = "<li>No users yet.</li>";
    return;
  }

  users.forEach((user) => {
    const listItem = document.createElement("li");
    listItem.className = "user-item";
    listItem.innerHTML = `
      <div class="user-meta">
        <strong>${user.name}</strong><br />
        <span>${user.email} (${user.role})</span>
      </div>
      <button class="delete-btn" data-id="${user.id}" type="button">Delete</button>
    `;
    userListEl.appendChild(listItem);
  });
}

async function loadUsers() {
  try {
    const response = await fetch(`${API_BASE_URL}/users`);
    const users = await response.json();
    renderUsers(users);
  } catch {
    showMessage("Failed to load users", true);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  showMessage("");

  const formData = new FormData(form);
  const payload = {
    name: formData.get("name"),
    email: formData.get("email"),
    role: formData.get("role"),
  };

  try {
    const response = await fetch(`${API_BASE_URL}/users`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const result = await response.json();
    if (!response.ok) {
      showMessage(result.error || "Failed to create user", true);
      return;
    }

    form.reset();
    showMessage("User created successfully");
    await loadUsers();
  } catch {
    showMessage("Failed to create user", true);
  }
});

refreshBtn.addEventListener("click", loadUsers);

userListEl.addEventListener("click", async (event) => {
  const target = event.target;
  if (!target.classList.contains("delete-btn")) {
    return;
  }

  const userId = target.getAttribute("data-id");
  if (!userId) {
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: "DELETE",
    });
    if (!response.ok) {
      showMessage("Failed to delete user", true);
      return;
    }

    showMessage("User deleted");
    await loadUsers();
  } catch {
    showMessage("Failed to delete user", true);
  }
});

loadUsers();
