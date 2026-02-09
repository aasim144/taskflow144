
function toggleTheme() {
  document.body.classList.toggle("dark");

  const icon = document.getElementById("themeIcon");

  if (document.body.classList.contains("dark")) {
    icon.src = "/static/img/sun.png";
    localStorage.setItem("theme", "dark");
  } else {
    icon.src = "/static/img/night-mode.png";
    localStorage.setItem("theme", "light");
  }
}

/* load saved theme */
window.onload = () => {
  const savedTheme = localStorage.getItem("theme");
  const icon = document.getElementById("themeIcon");

  if (savedTheme === "dark") {
    document.body.classList.add("dark");
    icon.src = "/static/img/sun.png";
  }
  loadTasks();
};