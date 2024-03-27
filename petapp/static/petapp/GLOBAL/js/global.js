document.addEventListener("DOMContentLoaded", function() {
  const currenturl = window.location.pathname;
  let pages = ["home-page", "catalog-page", "contact-page", "about-page", "auth-page", "basket-page", "reg-page"];

  for (let page of pages) {
    let element = document.querySelector("." + page);
    if (page === "home-page" && currenturl === "/") {
      element.classList.add("active-under");
    } else if (currenturl === `/${page.split("-")[0]}/`) {
      if (page === "basket-page" || page === "auth-page" || page === "reg-page") {
        element.classList.add("active-color-swap");
      } else {
        element.classList.add("active-under");
      }
    }
  }
});