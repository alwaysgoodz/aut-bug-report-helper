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

const reportForm = document.querySelector("form[data-completeness]");
if (reportForm) {
  const fields = Array.from(reportForm.querySelectorAll("[data-report-field]"));
  const score = document.getElementById("completeness-score");
  const count = document.getElementById("completeness-count");
  const progress = document.getElementById("completeness-progress");
  const completeMessage = document.getElementById("guidance-complete");
  const update = () => {
    let completed = 0;
    fields.forEach((field) => {
      const valid = field.name === "severity"
        ? Array.from(field.options).some((option) => option.value && option.value === field.value)
        : Boolean(field.value.trim());
      if (valid) completed++;
      document.querySelector(`#missing-fields [data-field='${field.name}']`).hidden = valid;
    });
    const percent = Math.round(100 * completed / fields.length);
    if (score.textContent !== `${percent}%`) score.textContent = `${percent}%`;
    count.textContent = `${completed} of ${fields.length} fields`;
    progress.value = percent;
    completeMessage.hidden = completed !== fields.length;
  };
  reportForm.addEventListener("input", update);
  reportForm.addEventListener("change", update);
  update();
}
