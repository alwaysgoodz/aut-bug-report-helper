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
  const blankPoints = new Set(reportForm.dataset.blankCodepoints.split(" ").map(Number));
  const hasText = (value) => Array.from(value).some((char) => !blankPoints.has(char.codePointAt(0)));
  const items = new Map(fields.map((field) => [field.name, document.querySelector(`#missing-fields [data-field='${field.name}']`)]));
  const score = document.getElementById("completeness-score");
  const count = document.getElementById("completeness-count");
  const progress = document.getElementById("completeness-progress");
  const completeMessage = document.getElementById("guidance-complete");
  const update = () => {
    let completed = 0;
    fields.forEach((field) => {
      const valid = field.name === "severity"
        ? Array.from(field.options).some((option) => option.value && option.value === field.value)
        : hasText(field.value);
      if (valid) completed++;
      items.get(field.name).hidden = valid;
    });
    const percent = Math.round(100 * completed / fields.length);
    if (score.textContent !== `${percent}%`) score.textContent = `${percent}%`;
    count.textContent = `${completed} of ${fields.length} fields`;
    progress.value = percent;
    completeMessage.hidden = completed !== fields.length;
    document.getElementById("missing-count").textContent = completed === fields.length ? "Complete" : `${fields.length-completed} missing`;
    const title = reportForm.elements.title;
    const titleLength = Array.from(title.value).length;
    const titleLimit = Number(title.dataset.characterLimit);
    const titleCounter = document.getElementById("title-count");
    titleCounter.textContent = `${titleLength} / ${titleLimit}`;
    titleCounter.classList.toggle("over-limit", titleLength > titleLimit);
  };
  reportForm.addEventListener("input", update);
  reportForm.addEventListener("change", update);
  window.addEventListener("pageshow", () => {
    update();
    // History traversal may restore form values after pageshow dispatch.
    setTimeout(update, 0);
  });
  update();
}

const guidance = document.querySelector(".form-page .guidance-details");
if (guidance) {
  const wide = window.matchMedia("(min-width: 1280px) and (min-height: 740px)");
  const adapt = () => { guidance.open = wide.matches; };
  wide.addEventListener("change", adapt);
  adapt();
}

const statusSelect = document.getElementById("status");
if (statusSelect) {
  const statusForm = statusSelect.form;
  const button = statusForm.querySelector("button[type='submit']");
  const refresh = () => { button.disabled = statusSelect.value === statusForm.elements.expected_status.value; };
  statusSelect.addEventListener("change", refresh);
  window.addEventListener("pageshow", refresh);
  refresh();
}
