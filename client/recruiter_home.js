const jobForm = document.getElementById("job-form");
const jobMessage = document.getElementById("job-message");
const recruiterJobsList = document.getElementById("recruiter-jobs-list");
const refreshJobsBtn = document.getElementById("refresh-jobs-btn");
const recruiterIdentity = document.getElementById("recruiter-identity");
const jobFormTitle = document.getElementById("job-form-title");
const jobSubmitBtn = document.getElementById("job-submit-btn");
const cancelEditBtn = document.getElementById("cancel-edit-btn");

const recruiterId = sessionStorage.getItem("userId");
const recruiterRole = sessionStorage.getItem("userRole");
const recruiterEmail = sessionStorage.getItem("userEmail");
let editingJobId = null;
let recruiterJobsCache = [];

if (!recruiterId || recruiterRole !== "recruiter") {
  window.location.href = "/login";
}

if (recruiterIdentity && recruiterEmail) {
  recruiterIdentity.textContent = `Logged in as ${recruiterEmail}`;
}

function setJobMessage(text, isError = false) {
  jobMessage.textContent = text;
  jobMessage.style.color = isError ? "#b91c1c" : "#047857";
}

function setFormMode(isEditMode) {
  if (isEditMode) {
    jobFormTitle.textContent = "Edit Job";
    jobSubmitBtn.textContent = "Update Job";
    cancelEditBtn.style.display = "inline-block";
    return;
  }

  jobFormTitle.textContent = "Post a Job";
  jobSubmitBtn.textContent = "Publish Job";
  cancelEditBtn.style.display = "none";
}

function populateForm(job) {
  jobForm.elements.title.value = job.title || "";
  jobForm.elements.company.value = job.company || "";
  jobForm.elements.location.value = job.location || "";
  jobForm.elements.job_type.value = job.job_type || "full-time";
  jobForm.elements.work_mode.value = job.work_mode || "on-site";
  jobForm.elements.salary.value = job.salary || "";
  jobForm.elements.description.value = job.description || "";
}

function renderRecruiterJobs(jobs) {
  recruiterJobsList.innerHTML = "";

  if (!jobs.length) {
    recruiterJobsList.innerHTML = '<p class="empty-state">No jobs posted yet.</p>';
    return;
  }

  jobs.forEach((job) => {
    const card = document.createElement("article");
    card.className = "job-item";
    card.innerHTML = `
      <div class="job-item-head">
        <h3>${job.title}</h3>
        <span class="salary-pill">${job.salary}</span>
      </div>
      <p class="job-company">${job.company}</p>
      <div class="job-meta">
        <span>${job.location}</span>
        <span>${job.job_type}</span>
        <span>${job.work_mode}</span>
      </div>
      <p class="job-description">${job.description}</p>
      <div class="job-actions">
        <button class="secondary-btn edit-job-btn" type="button" data-id="${job.id}">
          Edit
        </button>
        <button class="delete-btn delete-job-btn" type="button" data-id="${job.id}">
          Delete
        </button>
      </div>
    `;
    recruiterJobsList.appendChild(card);
  });
}

async function loadJobs() {
  try {
    const response = await fetch(`/api/recruiter/jobs?recruiter_id=${recruiterId}`);
    const jobs = await response.json();
    if (!response.ok) {
      setJobMessage("Failed to load jobs", true);
      return;
    }
    recruiterJobsCache = jobs;
    renderRecruiterJobs(jobs);
  } catch {
    setJobMessage("Failed to load jobs", true);
  }
}

jobForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setJobMessage("");

  const formData = new FormData(jobForm);
  const payload = {
    recruiter_id: Number(recruiterId),
    title: formData.get("title"),
    company: formData.get("company"),
    location: formData.get("location"),
    job_type: formData.get("job_type"),
    work_mode: formData.get("work_mode"),
    salary: formData.get("salary"),
    description: formData.get("description"),
  };

  try {
    const isEditMode = editingJobId !== null;
    const response = await fetch(
      isEditMode ? `/api/jobs/${editingJobId}` : "/api/jobs",
      {
        method: isEditMode ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }
    );
    const result = await response.json();

    if (!response.ok) {
      setJobMessage(result.error || "Failed to save job", true);
      return;
    }

    editingJobId = null;
    setFormMode(false);
    jobForm.reset();
    setJobMessage(isEditMode ? "Job updated successfully" : "Job posted successfully");
    await loadJobs();
  } catch {
    setJobMessage("Failed to save job", true);
  }
});

cancelEditBtn.addEventListener("click", () => {
  editingJobId = null;
  setFormMode(false);
  jobForm.reset();
  setJobMessage("");
});

recruiterJobsList.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }

  const jobId = target.getAttribute("data-id");
  if (!jobId) {
    return;
  }

  if (target.classList.contains("edit-job-btn")) {
    const selectedJob = recruiterJobsCache.find(
      (job) => String(job.id) === String(jobId)
    );
    if (!selectedJob) {
      setJobMessage("Job not found", true);
      return;
    }

    editingJobId = Number(jobId);
    populateForm(selectedJob);
    setFormMode(true);
    setJobMessage("Editing selected job");
    window.scrollTo({ top: 0, behavior: "smooth" });
    return;
  }

  if (target.classList.contains("delete-job-btn")) {
    const confirmed = window.confirm("Delete this job post?");
    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(`/api/jobs/${jobId}?recruiter_id=${recruiterId}`, {
        method: "DELETE",
      });
      const result = await response.json();
      if (!response.ok) {
        setJobMessage(result.error || "Failed to delete job", true);
        return;
      }

      setJobMessage("Job deleted successfully");
      if (editingJobId === Number(jobId)) {
        editingJobId = null;
        setFormMode(false);
        jobForm.reset();
      }
      await loadJobs();
    } catch {
      setJobMessage("Failed to delete job", true);
    }
  }
});

refreshJobsBtn.addEventListener("click", loadJobs);

setFormMode(false);
loadJobs();
