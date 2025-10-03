function initSiteSearch() {
    const input = document.getElementById('site-search');
    const btn = document.getElementById('site-search-btn');
    const list = document.getElementById('search-results');
    const form = document.getElementById('site-search-form');
    if (!input || !list) return; // navbar not loaded yet

    const index = [
        { "title": "Home", "url": "../index.html", "tag": "Page", "keywords": "main" },
        { "title": "Lessons", "url": "../lessons.html", "tag": "Index", "keywords": "all" },
        { "title": "Alphabet", "url": "../lesson1/alphabet.html", "tag": "Lesson 1", "keywords": "letters" },
        { "title": "False Friends", "url": "../lesson1/false_friends.html", "tag": "Lesson 1", "keywords": "faux amis" },
        { "title": "Resources", "url": "../resources/resources.html", "tag": "Page", "keywords": "links" },
        { "title": "Techniques", "url": "../techniques.html", "tag": "Page", "keywords": "methods" },
        { "title": "Vowels", "url": "../lesson1/vowels.html", "tag": "Lesson 1", "keywords": "а о у э е ё ю я и ы" },
        { "title": "Introduction", "url": "../introduction.html", "tag": "Lesson 1", "keywords": "about" },
        { "title": "Old Friends", "url": "../lesson1/friends.html", "tag": "Lesson 1", "keywords": "cognates" },
        { "title": "Sibilants", "url": "../lesson1/sibilants.html", "tag": "Lesson 1", "keywords": "ш щ ж ч" },
        { "title": "Signs", "url": "../lesson1/signs.html", "tag": "Lesson 1", "keywords": "ъ ь" },
    ];
    let current = -1;
    const MAX_RESULTS = 8;
    const HIDE = () => {
        list.style.display = 'none';
        input.setAttribute('aria-expanded', 'false');
    };
    const SHOW = () => {
        list.style.display = 'block';
        input.setAttribute('aria-expanded', 'true');
    };

    const escRe = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

    function highlight(text, q) {
        if (!q) return text;
        const re = new RegExp(escRe(q), 'ig');
        return text.replace(re, m => `<mark>${m}</mark>`);
    }

    function render(results, q) {
        list.innerHTML = '';
        current = -1;

        if (!q) { HIDE(); return; }

        // Render local matches
        results.slice(0, MAX_RESULTS).forEach((r, i) => {
                    const li = document.createElement('li');
                    li.setAttribute('role', 'option');
                    li.id = 'sr-' + i;
                    li.innerHTML = `<a href="${r.url}">${highlight(r.title, q)}</a>
                        ${r.tag?`<span class="search-tag">${r.tag}</span>`:''}`;
        li.addEventListener('mouseenter',()=>setActive(i));
        li.addEventListener('mouseleave',()=>setActive(-1));
        li.addEventListener('click',()=>{ location.href = r.url; });
        list.appendChild(li);
        });
      // Always add Google fallback at the bottom
        const liGoogle = document.createElement('li');
        liGoogle.innerHTML = `
            <a href="${googleSiteLink(q)}" target="_blank" rel="noopener">
            🔍 Search Google on <strong>RussianCourse</strong> for “<mark>${q}</mark>”
            </a>`;
        list.appendChild(liGoogle);

        SHOW();
    }

  function setActive(i) {
    current = i;
    Array.from(list.children).forEach((li, idx) => {
      li.setAttribute('aria-selected', idx === i ? 'true' : 'false');
    });
  }

  function chooseActive() {
    if (current < 0) {
      const first = list.querySelector('a'); if (first) window.location.href = first.href;
      return;
    }
    const a = list.children[current]?.querySelector('a'); if (a) window.location.href = a.href;
  }

  let t = 0;
  function onInput() {
    const q = input.value.trim().toLowerCase();
    if (!q) { HIDE(); return; }
    const results = q ? index.filter(it => matches(it, q)) : [];
    render(results, q);
  }
    function matches(item, q) {
    const t = (item.title || "").toLowerCase();
    const u = (item.url || "").toLowerCase();
    const k = (item.keywords || "").toLowerCase();
    return t.includes(q) || u.includes(q) || k.includes(q);
    }

    function googleSiteLink(query) {
    // Hard-code your intended domain for stability
    const site = "ellablac.github.io/RussianCourse";
    return `https://www.google.com/search?q=site:${encodeURIComponent(site)}+${encodeURIComponent(query)}`;
    }

  input.addEventListener('input', () => { clearTimeout(t); t = setTimeout(onInput, 120); });
  input.addEventListener('keydown', (e) => {
    switch (e.key) {
      case 'ArrowDown': e.preventDefault(); setActive(Math.min(current + 1, list.children.length - 1)); break;
      case 'ArrowUp':   e.preventDefault(); setActive(Math.max(current - 1, 0)); break;
      case 'Enter':     e.preventDefault(); chooseActive(); break;
      case 'Escape':    HIDE(); break;
    }
  });
  btn.addEventListener('click', () => { if (list.style.display !== 'block') onInput(); else chooseActive(); });
  document.addEventListener('click', (e) => { if (!form.contains(e.target)) HIDE(); });

}