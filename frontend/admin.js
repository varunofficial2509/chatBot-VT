(() => {
  const loginSection = document.getElementById("login-section");
  const uploadSection = document.getElementById("upload-section");
  const passwordInput = document.getElementById("password");
  const loginButton = document.getElementById("login-button");
  const loginStatus = document.getElementById("login-status");
  const resumeFile = document.getElementById("resume-file");
  const profileFile = document.getElementById("profile-file");
  const ingestButton = document.getElementById("ingest-button");
  const ingestStatus = document.getElementById("ingest-status");

  let adminToken = null;

  async function login() {
    const password = passwordInput.value;
    if (!password) return;

    loginButton.disabled = true;
    loginStatus.textContent = "Checking...";
    loginStatus.className = "status-line";

    try {
      const response = await fetch("/api/admin/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });

      if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail || "Login failed");
      }

      const data = await response.json();
      adminToken = data.token;
      loginSection.classList.add("hidden");
      uploadSection.classList.remove("hidden");
    } catch (err) {
      loginStatus.textContent = err.message || "Login failed";
    } finally {
      loginButton.disabled = false;
    }
  }

  async function ingest() {
    if (!adminToken) return;
    if (!resumeFile.files[0] && !profileFile.files[0]) {
      ingestStatus.textContent = "Please choose a resume, a profile JSON, or both.";
      ingestStatus.className = "status-line";
      return;
    }

    ingestButton.disabled = true;
    ingestStatus.textContent = "Uploading and indexing...";
    ingestStatus.className = "status-line";

    const formData = new FormData();
    if (resumeFile.files[0]) formData.append("resume", resumeFile.files[0]);
    if (profileFile.files[0]) formData.append("profile_json", profileFile.files[0]);

    try {
      const response = await fetch("/api/admin/ingest", {
        method: "POST",
        headers: { Authorization: `Bearer ${adminToken}` },
        body: formData,
      });

      const body = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(body.detail || "Ingestion failed");
      }

      const parts = [];
      if (body.chunks_indexed !== undefined) parts.push(`${body.chunks_indexed} chunks indexed`);
      if (body.profile_name) parts.push(`profile: ${body.profile_name}`);
      ingestStatus.textContent = `✓ Knowledge base updated${parts.length ? ` (${parts.join(", ")})` : ""}`;
      ingestStatus.className = "status-line ok";
    } catch (err) {
      ingestStatus.textContent = err.message || "Ingestion failed";
      ingestStatus.className = "status-line";
    } finally {
      ingestButton.disabled = false;
    }
  }

  loginButton.addEventListener("click", login);
  passwordInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") login();
  });
  ingestButton.addEventListener("click", ingest);
})();
