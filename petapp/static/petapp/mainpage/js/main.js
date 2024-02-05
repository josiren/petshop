// NavBar active page
document.addEventListener("DOMContentLoaded", function() {
  let main = document.getElementById("main");
  let catalog = document.getElementById("catalog");
  let contact = document.getElementById("contact");
  let whyme = document.getElementById("why-me");

  let currentLocation = window.location.href;

  if (currentLocation.endsWith("/")) {
    main.classList.add("active-under");
  } else if (currentLocation.endsWith("/catalog")) {
    catalog.classList.add("active-under");
  } else if (currentLocation.endsWith("/contact")) {
    contact.classList.add("active-under");
  } else if (currentLocation.endsWith("/why-me")) {
    whyme.classList.add("active-under");
  }
});

console.log(main);
