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

// Ignore a second click on Save while the first is still being sent, so a double click can't
// create the same record twice. The button isn't disabled: that would drop its name (e.g. "next")
// from the submitted form.
var leaving = false;
document.addEventListener("submit", function (event) {
  var form = event.target;
  if (event.defaultPrevented) return;
  if (form.dataset.submitting) {
    event.preventDefault();
    return;
  }
  form.dataset.submitting = "1";
  form.setAttribute("aria-busy", "true");
  leaving = true;
  // Safety net for a response that doesn't leave the page (e.g. a file download).
  setTimeout(function () { unlock(form); }, 8000);
});

function unlock(form) {
  delete form.dataset.submitting;
  form.removeAttribute("aria-busy");
  leaving = false;
}

// Coming back with the Back button restores the page from cache: make its forms usable again.
window.addEventListener("pageshow", function (event) {
  if (event.persisted) document.querySelectorAll("form[data-submitting]").forEach(unlock);
});

// Warn before leaving a form with unsaved changes.
var dirty = new Set();
function track(event) {
  var form = event.target.form;
  if (form && form.method === "post" && !form.hasAttribute("data-no-unsaved-warning")) dirty.add(form);
}
document.addEventListener("input", track);
document.addEventListener("change", track);
window.addEventListener("beforeunload", function (event) {
  if (dirty.size && !leaving) {
    event.preventDefault();
    event.returnValue = "";
  }
});

// Mobile menu: keyboard support and Escape to close. The checkbox keeps it working without JS.
document.addEventListener("DOMContentLoaded", function () {
  var toggle = document.getElementById("nav-toggle");
  var button = document.querySelector(".nav-button");
  if (!toggle || !button) return;
  var sync = function () {
    button.setAttribute("aria-expanded", toggle.checked ? "true" : "false");
    document.documentElement.classList.toggle("nav-open", toggle.checked);
  };
  toggle.addEventListener("change", sync);
  button.addEventListener("keydown", function (event) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      toggle.checked = !toggle.checked;
      sync();
      if (toggle.checked) {
        var first = document.querySelector("#sidebar .nav-link");
        if (first) first.focus();
      }
    }
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && toggle.checked) {
      toggle.checked = false;
      sync();
      button.focus();
    }
  });
  sync();
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
