$(document).ready(function () {
  $(".menu-icon").click(function () {
    $(".menu-icon").toggleClass("active");
    $(".sa-menu").toggleClass("active");
  });
    $(".sa-menu ul li").click(function () {
    $(".menu-icon").toggleClass("active");
    $(".sa-menu").toggleClass("active");
  });
});