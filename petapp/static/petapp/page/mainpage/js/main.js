const swiper = new Swiper('.swiper', {
  direction: 'horizontal',
  loop: true,
  slidesPerView: 3,
  allowTouchMove: true,
  breakpoints: {
    1280:{
      spaceBetween: 135
    },
    375: {
      spaceBetween: 45,
      speed: 200,
    },
  }
});