// Small progressive enhancements. Everything works without JavaScript.
document.addEventListener("click", function (event) {
  var target = event.target.closest("[data-print]");
  if (target) {
    event.preventDefault();
    window.print();
  }
});

document.addEventListener("submit", function (event) {
  var message = event.target.getAttribute("data-confirm");
  if (message && !window.confirm(message)) {
    event.preventDefault();
  }
});

// Show "details" inputs only when the related checkbox is ticked.
document.addEventListener("DOMContentLoaded", function () {
  [["id_special_info", "id_special_info_details"]].forEach(function (pair) {
    var box = document.getElementById(pair[0]);
    var detail = document.getElementById(pair[1]);
    if (!box || !detail) return;
    var wrap = detail.closest(".field");
    var sync = function () { wrap.hidden = !box.checked && !detail.value; };
    box.addEventListener("change", sync);
    sync();
  });
});
