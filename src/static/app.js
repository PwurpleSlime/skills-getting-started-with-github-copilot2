 document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Helper to escape HTML in participant emails
  function escapeHtml(str) {
    return str
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        // Create activity card
        const card = document.createElement("div");
        card.className = "activity-card";

        const title = document.createElement("h4");
        title.textContent = name;
        card.appendChild(title);

        const desc = document.createElement("p");
        desc.textContent = details.description;
        card.appendChild(desc);

        const schedule = document.createElement("p");
        schedule.innerHTML = `<strong>Schedule:</strong> ${escapeHtml(details.schedule)}`;
        card.appendChild(schedule);

        const spots = document.createElement("p");
        const taken = details.participants ? details.participants.length : 0;
        spots.innerHTML = `<strong>Spots:</strong> ${taken} / ${details.max_participants}`;
        card.appendChild(spots);

        // Participants section (styled)
        const participantsWrap = document.createElement("div");
        participantsWrap.className = "participants";

        const participantsTitle = document.createElement("h5");
        participantsTitle.textContent = "Participants";
        participantsWrap.appendChild(participantsTitle);

        if (details.participants && details.participants.length > 0) {
          const ul = document.createElement("ul");
          ul.className = "participants-list";
          details.participants.forEach((p) => {
            const li = document.createElement("li");
            li.innerHTML = `<span class="participant">${escapeHtml(p)}</span>`;
            ul.appendChild(li);
          });
          participantsWrap.appendChild(ul);
        } else {
          const none = document.createElement("p");
          none.className = "info small";
          none.textContent = "No participants yet";
          participantsWrap.appendChild(none);
        }

        card.appendChild(participantsWrap);

        activitiesList.appendChild(card);

        // Add option to select for signup (mark as dynamic so we can refresh)
        const opt = document.createElement("option");
        opt.value = name;
        opt.textContent = name;
        opt.className = "dynamic";
        activitySelect.appendChild(opt);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
