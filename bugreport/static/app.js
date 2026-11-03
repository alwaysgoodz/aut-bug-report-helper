"use strict";

const summary = document.getElementById("form-errors");
if (summary) summary.focus();

document.querySelectorAll("form[method='post']").forEach((form) => {
  form.addEventListener("submit", () => {
    form.querySelectorAll("button[type='submit']").forEach((button) => {
      button.disabled = true;
      button.setAttribute("aria-busy", "true");
    });
  });
});

window.addEventListener("pageshow", () => {
  document.querySelectorAll("button[aria-busy='true']").forEach((button) => {
    button.disabled = false;
    button.removeAttribute("aria-busy");
  });
});
