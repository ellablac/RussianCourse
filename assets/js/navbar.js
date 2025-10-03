/** Inject navbar HTML directly (works on file:// and static hosting) */
function injectNavbar(selector = "#navbar-placeholder") {
    const NAVBAR_HTML = `
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">
      <a class="navbar-brand" href="../index.html">
        <img src="../assets/basilika.png" alt="Logo" height="40">
      </a>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item"><a class="nav-link" href="../index.html">Home</a></li>
          <li class="nav-item"><a class="nav-link" href="../lessons.html">Lessons</a></li>
          <li class="nav-item"><a class="nav-link" href="../resources/resources.html">Resources</a></li>
        </ul>
        <form class="d-flex position-relative" role="search" id="site-search-form" autocomplete="off">
          <input id="site-search" class="form-control me-0" type="search"
                 placeholder="Search lessons & resources…" aria-label="Search"
                 aria-autocomplete="list" aria-controls="search-results" aria-expanded="false">
          <button class="btn btn-gradient" type="button" id="site-search-btn">Search</button>
          <ul id="search-results" class="search-dropdown" role="listbox"></ul>
        </form>
      </div>
    </div>
  </nav>`;

    const mount = document.querySelector(selector);
    if (mount) {
        mount.innerHTML = NAVBAR_HTML;
        highlightActiveLink(); // highlight current page
        if (typeof initSiteSearch === "function") initSiteSearch(); // init live search
    }
}

/** Auto-highlight the active link */
function highlightActiveLink() {
    const current = (location.pathname.split("/").pop() || "index.html").toLowerCase();
    document.querySelectorAll(".navbar .nav-link").forEach(a => {
        const href = (a.getAttribute("href") || "").split("/").pop().toLowerCase();
        a.classList.toggle("active", href === current || (current === "" && href === "index.html"));
    });
}