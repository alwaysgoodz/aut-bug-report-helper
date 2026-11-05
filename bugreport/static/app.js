"use strict";

const summary = document.getElementById("form-errors");
if (summary) summary.focus();

const motionPreference = window.matchMedia("(prefers-reduced-motion: reduce)");
const feedbackAnimations = new Map();
const animateFeedback = (element) => {
  feedbackAnimations.get(element)?.cancel();
  if (motionPreference.matches || !element.animate) return;
  const animation = element.animate([
    { opacity: .55, transform: "translateY(3px)" },
    { opacity: 1, transform: "none" },
  ], { duration: 220, easing: "cubic-bezier(.2,.7,.2,1)" });
  feedbackAnimations.set(element, animation);
  animation.finished.then(() => {
    if (feedbackAnimations.get(element) === animation) feedbackAnimations.delete(element);
  }, () => {}); // Cancellation is expected when typing or preferences change.
};
motionPreference.addEventListener("change", () => {
  feedbackAnimations.forEach((animation) => animation.cancel());
  feedbackAnimations.clear();
});

const busyButtons = new Map();
document.querySelectorAll("form").forEach((form) => {
  form.querySelectorAll("button[type='submit']").forEach((button) => {
    const label = document.createElement("span");
    label.className = "button-label";
    label.append(...button.childNodes);
    button.append(label);
  });
  form.addEventListener("submit", (event) => {
    if (event.defaultPrevented) return;
    form.setAttribute("aria-busy", "true");
    form.querySelectorAll("button[type='submit']").forEach((button) => {
      if (busyButtons.has(button)) return;
      const label = button.querySelector(".button-label");
      busyButtons.set(button, { nodes: Array.from(label.childNodes), minWidth: button.style.minWidth });
      button.style.minWidth = `${button.getBoundingClientRect().width}px`;
      label.textContent = button.dataset.busyLabel || (form.method === "get" ? "Applying…" : "Submitting…");
      button.disabled = true;
      button.setAttribute("aria-busy", "true");
    });
  });
});

window.addEventListener("pageshow", () => {
  busyButtons.forEach((original, button) => {
    button.querySelector(".button-label").replaceChildren(...original.nodes);
    button.style.minWidth = original.minWidth;
    button.disabled = false;
    button.removeAttribute("aria-busy");
  });
  busyButtons.clear();
  document.querySelectorAll("form[aria-busy='true']").forEach((form) => form.removeAttribute("aria-busy"));
});

const progress = document.getElementById("completeness-progress");
let progressFill;
if (progress) {
  progressFill = document.createElement("span");
  progressFill.className = "completion-fill";
  progressFill.setAttribute("aria-hidden", "true");
  progressFill.style.transform = `scaleX(${progress.value / 100})`;
  progress.parentElement.append(progressFill);
  progress.parentElement.classList.add("is-enhanced");
}

const reportForm = document.querySelector("form[data-completeness]");
if (reportForm) {
  const fields = Array.from(reportForm.querySelectorAll("[data-report-field]"));
  const blankPoints = new Set(reportForm.dataset.blankCodepoints.split(" ").map(Number));
  const hasText = (value) => Array.from(value).some((char) => !blankPoints.has(char.codePointAt(0)));
  const items = new Map(fields.map((field) => [field.name, document.querySelector(`#missing-fields [data-field='${field.name}']`)]));
  const score = document.getElementById("completeness-score");
  const count = document.getElementById("completeness-count");
  const completeMessage = document.getElementById("guidance-complete");
  let previousPercent;
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
    if (previousPercent !== undefined && percent !== previousPercent) animateFeedback(score);
    previousPercent = percent;
    count.textContent = `${completed} of ${fields.length} fields`;
    progress.value = percent;
    progressFill.style.transform = `scaleX(${percent / 100})`;
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
  const help = document.getElementById("status-help");
  const refresh = () => {
    const current = statusForm.elements.expected_status.value;
    const unchanged = statusSelect.value === current;
    button.disabled = unchanged;
    help.textContent = unchanged ? "Choose a new status before updating."
      : `Ready to change from ${current} to ${statusSelect.value}. Save to confirm.`;
  };
  statusSelect.addEventListener("change", refresh);
  window.addEventListener("pageshow", refresh);
  refresh();
}
