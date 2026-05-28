const searchInput = document.getElementById("search-input");
const searchBtn = document.getElementById("search-btn");
const locationFilter = document.getElementById("location-filter");
const jobTypeFilter = document.getElementById("job-type-filter");
const workModeFilter = document.getElementById("work-mode-filter");
const clearFiltersBtn = document.getElementById("clear-filters-btn");
const jobsList = document.getElementById("jobs-list");
const jobsMessage = document.getElementById("jobs-message");
const resultsCount = document.getElementById("results-count");

function setJobsMessage(text, isError = false) {
  jobsMessage.textContent = text;
  jobsMessage.style.color = isError ? "#b91c1c" : "#6b7280";
}

function createOption(value, label) {
  const option = document.createElement("option");
  option.value = value;
  option.textContent = label;
  return option;
}

async function loadFilters() {
  try {
    const response = await fetch("/api/jobs/filters");
    const data = await response.json();
    if (!response.ok) {
      setJobsMessage("Failed to load filters", true);
      return;
    }

    data.locations.forEach((location) => {
      locationFilter.appendChild(createOption(location, location));
    });
    data.job_types.forEach((jobType) => {
      jobTypeFilter.appendChild(createOption(jobType, jobType));
    });
    data.work_modes.forEach((workMode) => {
      workModeFilter.appendChild(createOption(workMode, workMode));
    });
  } catch {
    setJobsMessage("Failed to load filters", true);
  }
}

function renderJobs(jobs) {
  jobsList.innerHTML = "";
  resultsCount.textContent = `${jobs.length} result(s)`;

  if (!jobs.length) {
    jobsList.innerHTML = '<p class="empty-state">No job posts found.</p>';
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
    `;
    jobsList.appendChild(card);
  });
}

async function loadJobs() {
  setJobsMessage("Loading job posts...");

  const query = new URLSearchParams();
  if (searchInput.value.trim()) {
    query.set("search", searchInput.value.trim());
  }
  if (locationFilter.value) {
    query.set("location", locationFilter.value);
  }
  if (jobTypeFilter.value) {
    query.set("job_type", jobTypeFilter.value);
  }
  if (workModeFilter.value) {
    query.set("work_mode", workModeFilter.value);
  }

  try {
    const response = await fetch(`/api/jobs?${query.toString()}`);
    const jobs = await response.json();
    if (!response.ok) {
      setJobsMessage("Failed to load job posts", true);
      return;
    }

    setJobsMessage("");
    renderJobs(jobs);
  } catch {
    setJobsMessage("Failed to load job posts", true);
  }
}

searchBtn.addEventListener("click", loadJobs);
searchInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    loadJobs();
  }
});

locationFilter.addEventListener("change", loadJobs);
jobTypeFilter.addEventListener("change", loadJobs);
workModeFilter.addEventListener("change", loadJobs);

clearFiltersBtn.addEventListener("click", () => {
  searchInput.value = "";
  locationFilter.value = "";
  jobTypeFilter.value = "";
  workModeFilter.value = "";
  loadJobs();
});

loadFilters().then(loadJobs);
