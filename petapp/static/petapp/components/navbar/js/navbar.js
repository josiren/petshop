// Modal windows alarm
let button = document.querySelector(".alarm");
let modal_window = document.querySelector(".modal__window");

button.onclick = function () {
  modal_window.classList.toggle("open");
  button.classList.toggle("active-color-swap");
};
