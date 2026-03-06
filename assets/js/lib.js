/** Library of shared Javascript functions for the website */

/**
 * Creates the standard site footer.
 * @returns {HTMLFooterElement}
 */
function createSiteFooter() {
    const footer = document.createElement('footer');
    footer.className = 'site-footer text-center py-3';

    const copy = document.createTextNode('\u00a9 ');
    const yearSpan = document.createElement('span');
    yearSpan.id = 'y';
    yearSpan.textContent = String(new Date().getFullYear());
    const tail = document.createTextNode(' Sky4Tech, LLC');

    footer.append(copy, yearSpan, tail);
    return footer;
}

/**
 * Inserts the Fair Use note when the page hosts external videos.
 * @param {HTMLElement} footer
 * @returns {void}
 */
function insertFairUseNoteIfNeeded(footer) {
    if (!document.querySelector('main.external-video')) return;
    if (footer.querySelector('.fair-use-note')) return;

    const note = document.createElement('div');
    note.className = 'fair-use-note mb-3';
    note.textContent =
        'This site is an educational resource. All embedded videos are the property of their respective owners and are used here for instructional analysis under Fair Use (17 U.S.C. \u00a7 107).';

    footer.insertBefore(note, footer.firstChild);
}

/**
 * Ensures the site footer exists unless the page opts out with body.no-footer.
 * @returns {void}
 */
function ensureSiteFooter() {
    if (document.body && document.body.classList.contains('no-footer')) return;

    const existingFooter = document.querySelector('.site-footer');
    const footer = existingFooter || createSiteFooter();

    if (!existingFooter) {
        const main = document.querySelector('main');
        if (main && typeof main.insertAdjacentElement === 'function') {
            main.insertAdjacentElement('afterend', footer);
        } else {
            document.body.appendChild(footer);
        }
    }

    insertFairUseNoteIfNeeded(footer);
}

/**
 * Initializes footer creation after DOM is ready.
 * @returns {void}
 */
function initSiteFooter() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSiteFooter);
        return;
    }
    ensureSiteFooter();
}

initSiteFooter();

// Add a speaker button with audio to any <li class="word-with-audio" data-text="...">
function decorateWords(audioPath = '../assets/sound/male/words/') {
    document.querySelectorAll('.word-with-audio').forEach(li => {
        // Prevent duplicate buttons
        if (li.querySelector('.speak-btn')) return;

        // Pull Russian text from data-text (preferred) or fallback to text content
        const text = (li.dataset.text || li.textContent || '').trim();
        if (!text) return;

        const btn = createAudioButton(text, audioPath);
        li.prepend(btn);
    });
}

// Add a speaker button with audio to all letters in the alphabet table on the page
function decorateTable(audioPath='../assets/sound/male/') {
    document.querySelectorAll('.alphabet-table tbody tr').forEach(tr => {
        const cells = tr.querySelectorAll('td');
        if (cells.length < 3) return;
        const say = (cells[2].textContent || '').trim() || (cells[0].textContent || '').trim();
        if (!say) return;
        if (cells[0].querySelector('.speak-btn')) return;
        // Use the shared createAudioButton function
        const btn = createAudioButton(say, audioPath);
        cells[0].prepend(btn);
    });
}

/**
 * Attach overlay audio buttons to images with class `img-with-audio`.
 * This keeps per-page markup minimal; images should carry a `data-text` attribute
 * whose value maps to the mp3 filename (e.g. data-text="э?").
 */
function decorateImages(audioPath = '../assets/sound/male/words/') {
    if (typeof createAudioButton !== 'function') {
        console.error("createAudioButton function is not defined");
        return;
    }
    document.querySelectorAll('img.img-with-audio').forEach(img => {
        try {
            // Avoid duplicate buttons
            if (img.parentElement.querySelector('.speak-btn')) return;
            const text = (img.dataset.text || '').trim();
            if (!text) return;

            // Ensure the image is wrapped by a positionable container
            let wrapper = img.parentElement;
            if (getComputedStyle(wrapper).position === 'static') {
                const wrap = document.createElement('div');
                wrap.className = 'position-relative d-inline-block';
                wrapper.replaceChild(wrap, img);
                wrap.appendChild(img);
                wrapper = wrap;
            }

            const btn = createAudioButton(text, audioPath);
            btn.classList.add('position-absolute', 'top-0', 'end-0', 'm-2', 'img-sound-btn');

            wrapper.appendChild(btn);
        } catch (e) {
            // swallowing errors so other pages aren't impacted
            console.warn('attachImageAudio error', e);
        }
    });
}
