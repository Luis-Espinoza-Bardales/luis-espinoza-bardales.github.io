const NEW_WINDOW_DAYS = 90;
const SITE_VERSION = "2026-06-02-04";

const state = {
  papers: [],
  teaching: [],
  site: null,
};

const escapeHtml = (value = "") =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

const isRecent = (dateValue) => {
  if (!dateValue) return false;
  const updated = new Date(`${dateValue}T00:00:00`);
  if (Number.isNaN(updated.valueOf())) return false;
  const age = Date.now() - updated.getTime();
  return age >= 0 && age <= NEW_WINDOW_DAYS * 24 * 60 * 60 * 1000;
};

const loadJson = async (path) => {
  const response = await fetch(`${path}?v=${SITE_VERSION}`, { cache: "no-cache" });
  if (!response.ok) {
    throw new Error(`Unable to load ${path}`);
  }
  return response.json();
};

const paperBadges = (paper) => {
  const badges = [
    `<span class="tag">${escapeHtml(paper.year)}</span>`,
    `<span class="tag">${escapeHtml(paper.category)}</span>`,
  ];
  if (isRecent(paper.updated)) {
    badges.push('<span class="new-badge">new!</span>');
  }
  return badges.join("");
};

const filterIcons = {
  All: '<rect width="7" height="7" x="3" y="3" rx="1"></rect><rect width="7" height="7" x="14" y="3" rx="1"></rect><rect width="7" height="7" x="14" y="14" rx="1"></rect><rect width="7" height="7" x="3" y="14" rx="1"></rect>',
  "Working Papers": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.8-3.8a6 6 0 0 1-8 8L6.6 20.4a2.1 2.1 0 0 1-3-3L10.5 10.5a6 6 0 0 1 8-8l-3.8 3.8z"></path>',
  "Policy Papers": '<line x1="3" x2="21" y1="22" y2="22"></line><line x1="6" x2="6" y1="18" y2="11"></line><line x1="10" x2="10" y1="18" y2="11"></line><line x1="14" x2="14" y1="18" y2="11"></line><line x1="18" x2="18" y1="18" y2="11"></line><polygon points="12 2 20 7 4 7"></polygon>',
  "Book Chapters": '<path d="M12 7v14"></path><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"></path>',
  "Work in Progress": '<path d="M13 7 8.7 2.7a2.4 2.4 0 0 0-3.4 0L2.7 5.3a2.4 2.4 0 0 0 0 3.4L7 13"></path><path d="m8 6 2-2"></path><path d="m18 16 2-2"></path><path d="m17 11 4.3 4.3a2.4 2.4 0 0 1 0 3.4l-2.6 2.6a2.4 2.4 0 0 1-3.4 0L11 17"></path><path d="M21.2 6.8a1 1 0 0 0-4-4L3.8 16.2a2 2 0 0 0-.5.8L2 21.4a.5.5 0 0 0 .6.6L7 20.7a2 2 0 0 0 .8-.5z"></path><path d="m15 5 4 4"></path>',
  default: '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M10 9H8"></path><path d="M16 13H8"></path><path d="M16 17H8"></path>',
};

const filterIcon = (category) => `
  <span class="filter-icon" aria-hidden="true">
    <svg viewBox="0 0 24 24" role="img" focusable="false">
      ${filterIcons[category] || filterIcons.default}
    </svg>
  </span>
`;

const placeholderLabel = (paper) => paper.category === "Work in Progress" ? "WIP" : "PUB";

const paperCard = (paper) => `
  <button class="paper-card" type="button" data-open-paper="${escapeHtml(paper.slug)}">
    <div class="paper-thumb">
      ${paper.image
        ? `<img src="${escapeHtml(paper.image)}" alt="${escapeHtml(paper.title)} thumbnail">`
        : `<span class="node-placeholder" aria-hidden="true">${placeholderLabel(paper)}</span>`}
    </div>
    <div class="paper-meta">${paperBadges(paper)}</div>
    <h3>${escapeHtml(paper.title)}</h3>
    <p>${escapeHtml(paper.short)}</p>
  </button>
`;

const paperNode = (paper) => `
  <button class="paper-node${paper.image ? "" : " no-figure"}" type="button" data-open-paper="${escapeHtml(paper.slug)}" aria-label="${escapeHtml(paper.title)}">
    ${paper.image
      ? `<img src="${escapeHtml(paper.image)}" alt="" aria-hidden="true">`
      : `<span class="node-placeholder" aria-hidden="true">${placeholderLabel(paper)}</span>`}
    ${isRecent(paper.updated) ? '<span class="node-new">new!</span>' : ""}
    <span class="node-label">${escapeHtml(paper.title)}</span>
  </button>
`;

const isExternalLink = (url = "") => /^https?:\/\//i.test(url);

const linkButtons = (links = []) =>
  links
    .map((link) => {
      const isExternal = isExternalLink(link.url);
      const kind = link.primary ? "pdf-action" : isExternal ? "source-action" : "secondary-action";
      const target = isExternal ? ' target="_blank" rel="noopener noreferrer"' : "";
      const sourceTag = isExternal ? '<span class="action-tag">Source</span>' : "";
      return `<a class="paper-action ${kind}" href="${escapeHtml(link.url)}"${target}>${sourceTag}<span class="action-label">${escapeHtml(link.label)}</span></a>`;
    })
    .join("");

const versionContent = (paper, version) => {
  const display = version || paper;
  const links = display.links || paper.links || [];
  return `
    <h2>${escapeHtml(display.title || paper.title)}</h2>
    <p class="authors">${escapeHtml(paper.authors)}</p>
    <p class="citation">${escapeHtml(display.citation || paper.citation || paper.status || "")}</p>
    ${paper.languageNote ? `<p class="language-warning">${escapeHtml(paper.languageNote)}</p>` : ""}
    <p class="abstract">${escapeHtml(display.abstract || paper.abstract)}</p>
    ${links.length ? `<div class="dialog-links">${linkButtons(links)}</div>` : ""}
  `;
};

const attachPaperEvents = () => {
  document.querySelectorAll("[data-open-paper]").forEach((button) => {
    button.addEventListener("click", () => {
      const paper = state.papers.find((item) => item.slug === button.dataset.openPaper);
      if (paper) openPaperModal(paper);
    });
  });
};

const openPaperModal = (paper) => {
  const dialog = document.querySelector("[data-paper-modal]");
  if (!dialog) return;

  const versions = paper.versions || [];
  const activeVersion = versions[0];
  const languageSwitch = versions.length
    ? `<div class="language-switch" aria-label="Publication language">
        ${versions.map((version, index) => `
          <button type="button" class="${index === 0 ? "active" : ""}" data-version-code="${escapeHtml(version.code)}">
            ${escapeHtml(version.label)}
          </button>
        `).join("")}
      </div>`
    : "";

  const imagePanel = paper.image
    ? `<div class="dialog-image"><img src="${escapeHtml(paper.image)}" alt="${escapeHtml(paper.title)} thumbnail"></div>`
    : '<div class="dialog-image no-figure-panel"><span>Draft forthcoming</span></div>';

  dialog.innerHTML = `
    <div class="dialog-layout">
      ${imagePanel}
      <div class="dialog-body">
        <div class="dialog-top">
          <div class="paper-meta">${paperBadges(paper)}</div>
          <button class="dialog-close" type="button" data-close-modal aria-label="Close">x</button>
        </div>
        ${languageSwitch}
        <div data-version-content>${versionContent(paper, activeVersion)}</div>
      </div>
    </div>
  `;

  dialog.querySelector("[data-close-modal]").addEventListener("click", () => dialog.close());
  dialog.querySelectorAll("[data-version-code]").forEach((button) => {
    button.addEventListener("click", () => {
      const version = versions.find((item) => item.code === button.dataset.versionCode);
      dialog.querySelectorAll("[data-version-code]").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      dialog.querySelector("[data-version-content]").innerHTML = versionContent(paper, version);
    });
  });
  dialog.onclick = (event) => {
    if (event.target === dialog) dialog.close();
  };

  if (typeof dialog.showModal === "function") {
    dialog.showModal();
  }
};

const renderFeatured = () => {
  const container = document.querySelector("[data-featured-papers]");
  if (!container) return;
  const papers = state.papers.filter((paper) => paper.featured).slice(0, 4);
  container.innerHTML = papers.map(paperCard).join("");
  attachPaperEvents();
};

const renderResearch = (activeCategory = "All") => {
  const grid = document.querySelector("[data-paper-grid]");
  if (!grid) return;
  const papers = activeCategory === "All"
    ? state.papers
    : state.papers.filter((paper) => paper.category === activeCategory);
  grid.innerHTML = papers.map(paperCard).join("");
  attachPaperEvents();
};

const renderResearchWall = (activeCategory = "All") => {
  const wall = document.querySelector("[data-paper-wall]");
  if (!wall) return;
  const categories = [...new Set(state.papers.map((paper) => paper.category))];
  const rows = categories
    .map((category) => ({
      category,
      papers: state.papers.filter((paper) => paper.category === category),
    }))
    .filter((row) => activeCategory === "All" || row.category === activeCategory)
    .filter((row) => row.papers.length);

  wall.innerHTML = rows.map((row) => `
    <section class="paper-row" aria-label="${escapeHtml(row.category)}">
      <h2>${escapeHtml(row.category)}</h2>
      <div class="paper-nodes">
        ${row.papers.map(paperNode).join("")}
      </div>
    </section>
  `).join("");
  attachPaperEvents();
};

const renderFilters = () => {
  const filters = document.querySelector("[data-paper-filters]");
  if (!filters) return;
  const categories = ["All", ...new Set(state.papers.map((paper) => paper.category))];
  filters.innerHTML = categories
    .map((category, index) => `
      <button type="button" class="${index === 0 ? "active" : ""}" data-filter="${escapeHtml(category)}">
        ${filterIcon(category)}
        <span class="filter-label">${escapeHtml(category)}</span>
      </button>
    `)
    .join("");

  filters.querySelectorAll("button").forEach((button) => {
    button.addEventListener("click", () => {
      filters.querySelectorAll("button").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      renderResearch(button.dataset.filter);
      renderResearchWall(button.dataset.filter);
    });
  });
};

const renderTeaching = () => {
  const container = document.querySelector("[data-teaching-list]");
  if (!container) return;
  const courseMarkup = (courses = []) =>
    courses.length
      ? `<ul class="course-list">${courses.map((course) => {
        if (typeof course === "string") {
          return `<li>${escapeHtml(course)}</li>`;
        }
        return `
          <li>
            <div class="course-main">
              <span class="course-name">${escapeHtml(course.name)}</span>
              ${course.description ? `<p class="course-description">${escapeHtml(course.description)}</p>` : ""}
            </div>
            <div class="course-badges">
              <span class="badge-cell badge-cell-syllabus">
                ${course.syllabus ? `<a class="course-syllabus" href="${escapeHtml(course.syllabus.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(course.syllabus.label || "Latest syllabus")}</a>` : ""}
              </span>
              <span class="badge-cell badge-cell-terms">
                <span class="course-terms">${escapeHtml(course.terms)}</span>
              </span>
              <span class="badge-cell badge-cell-level">
                ${course.levelCode ? `<span class="course-level course-level-${escapeHtml(course.levelCode).toLowerCase()}">${escapeHtml(course.levelCode)}</span>` : ""}
              </span>
              ${course.note ? `<span class="course-note">${escapeHtml(course.note)}</span>` : ""}
            </div>
          </li>
        `;
      }).join("")}</ul>`
      : "";

  container.innerHTML = state.teaching.map((item) => `
    <article class="timeline-item">
      <div class="timeline-year">${escapeHtml(item.year)}</div>
      <div>
        <h2>${escapeHtml(item.title)}</h2>
        <p class="teaching-role">${escapeHtml(item.role || item.level)}</p>
        <p class="teaching-institution">${escapeHtml(item.institution)}</p>
        ${item.description ? `<p>${escapeHtml(item.description)}</p>` : ""}
        ${courseMarkup(item.courses)}
      </div>
    </article>
  `).join("");
};

const renderCv = () => {
  const buttons = document.querySelectorAll("[data-cv-download]");
  if (!buttons.length || !state.site?.cvUrl) return;
  buttons.forEach((button) => {
    button.href = state.site.cvUrl;
    button.classList.remove("hidden");
  });
};

const init = async () => {
  const page = document.body.dataset.page;
  try {
    const requests = [loadJson("data/papers.json"), loadJson("data/site.json")];
    if (page === "teaching") requests.push(loadJson("data/teaching.json"));

    const [papers, site, teaching = []] = await Promise.all(requests);
    state.papers = papers;
    state.site = site;
    state.teaching = teaching;

    renderFeatured();
    renderFilters();
    renderResearch();
    renderResearchWall();
    renderTeaching();
    renderCv();
  } catch (error) {
    console.error(error);
    document.querySelectorAll(".loading").forEach((node) => {
      node.textContent = "This content could not be loaded.";
      node.style.display = "block";
    });
  }
};

init();
