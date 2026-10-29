const rosterEl = document.getElementById("roster");
const statusEl = document.getElementById("status");
const emptyEl = document.getElementById("empty");
const errorEl = document.getElementById("error");
const searchEl = document.getElementById("search");

let students = [];

function render() {
  const query = searchEl.value.trim().toLowerCase();
  const visible = students.filter((student) =>
    student.name.toLowerCase().includes(query)
  );

  rosterEl.replaceChildren();
  emptyEl.classList.toggle("hidden", visible.length > 0 || students.length === 0);
  errorEl.classList.add("hidden");

  visible.forEach((student) => {
    const item = document.createElement("li");

    const name = document.createElement("span");
    name.className = "student-name";
    name.textContent = student.name;

    const year = document.createElement("span");
    year.className = "school-year";
    year.textContent = student.school_year;

    item.append(name, year);
    rosterEl.append(item);
  });

  if (!students.length) {
    statusEl.textContent = "No students found in the database.";
    return;
  }

  if (query) {
    statusEl.textContent = `Showing ${visible.length} of ${students.length} students`;
  } else {
    statusEl.textContent = `${students.length} students`;
  }
}

async function loadStudents() {
  try {
    const response = await fetch("/api/students");
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Could not load the roster.");
    }
    students = data.students || [];
    render();
  } catch (error) {
    rosterEl.replaceChildren();
    emptyEl.classList.add("hidden");
    errorEl.classList.remove("hidden");
    errorEl.textContent =
      error.message || "Something went wrong while loading names.";
    statusEl.textContent = "Roster unavailable";
  }
}

searchEl.addEventListener("input", render);
loadStudents();
