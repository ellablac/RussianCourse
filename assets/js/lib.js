/** Library of shared Javascript functions for the website */

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