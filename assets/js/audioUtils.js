/**
 * Speak the given text in Russian using speech synthesis (Web Speech API).
 * Simple Text-to-speech API, no audio files needed. The quality of the russian
 * voice is not great. Currently used as a fallback if no audio file is found.
 * 
 * Update: Added logic to select better voices if available: Google Russian voice
 * (Chrome) or Microsoft Svetlana Natural Online (Edge). These sound much better,
 * but may not be available in all browsers. Using audio files is still preferred
 * for robustness and portability.
 * @see https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis
 * @see https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
 */

// Cache the preferred voice once voices are available.
let preferredVoiceRu = null;
// Initialize on page load.
document.addEventListener('DOMContentLoaded', initVoices);
if (document.readyState !== 'loading') {
    // If DOMContentLoaded has already fired, initialize immediately.
    // It is OK if it runs twice as long as initVoices is idempotent
    // and event listeners are not added multiple times.
    initVoices();
}

function initVoices() {
    const synth = window.speechSynthesis;
    if (!synth) return;
    // avoid adding multiple event listeners
    if (!synth.onvoiceschanged) {
        synth.onvoiceschanged = () => updatePreferredVoice();
    }
    updatePreferredVoice();
}

/**
 * Pick the best available TTS voice from a list.
 * Priority: 
 * 1. Google voice is available in Chrome only
 * 2. Microsoft Svetlana Online (Natural) is only in Edge.
 * 3. Any Russian voice available, the quality may vary in Firefox, Safari, etc.
 * @param {SpeechSynthesisVoice[]} voices - Available voices from speechSynthesis.
 * @returns {SpeechSynthesisVoice|null} The selected voice, or null if none match.
 */
function selectPreferredVoice(voices) {
    const googleVoice = voices.find(v => {
        const name = v.name ? v.name.toLowerCase() : '';
        // find() loops until includes() returns true at which point v contains the target voice
        return name.includes('google') && name.includes('русский');
    }
    // shortcut callback function (=>), v is returned here and stored in googleVoice if found
    );
    if (googleVoice)
        return googleVoice;

    const svetlana = voices.find(v => {
        const name = v.name ? v.name.toLowerCase() : '';
        return (
            name.includes('microsoft') &&
            name.includes('svetlana') &&
            name.includes('online') &&
            name.includes('natural')
        );
    });
    if (svetlana)
        return svetlana;
    
    const ru = voices.find(v => v.lang && v.lang.toLowerCase().startsWith('ru'));
    return ru || null;
}


function updatePreferredVoice() {
    const synth = window.speechSynthesis;
    if (!synth || !synth.getVoices) return;
    const voices = synth.getVoices();
    if (!voices.length) {
        console.info('Speech voices not loaded yet');
        return;
    }
    preferredVoiceRu = selectPreferredVoice(voices);

    if (preferredVoiceRu) {

        console.info('The updatePreferredVoice ran and UPDATED PREFERRED VOICE:', preferredVoiceRu.name, preferredVoiceRu.lang || '');
    }
    else {
        console.info('The updatePreferredVoice ran but found NO SUITABLE  VOICE.');
    }
}

/*
 * @param {string} text - The text to speak.
 * @param {string} [lang='ru-RU'] - The language code for speech synthesis.
 */
function speak(text, lang = 'ru-RU') {
    const synth = window.speechSynthesis;
    if (!synth) {
        console.warn('SpeechSynthesis not supported in this browser');
        return;
    }
    const u = new SpeechSynthesisUtterance(text);
    u.lang = lang;
    u.rate = 0.9;

    if (!preferredVoiceRu) {
        updatePreferredVoice();
        console.info('Preferred voice updated in speak():', preferredVoiceRu ? preferredVoiceRu.name : 'none');
    }
    if (preferredVoiceRu) {
        u.voice = preferredVoiceRu;
    }
    else {
        // The browser's built‑in TTS engine has default voices that are available
        // even before the voices are loaded. These are low quality and 
        // sound very robotic.
        // Higher-quality voices load asynchronously and may not be
        // available when the user first clicks the play button.
        // To ensure better voice selection, voices are loaded immediately on page load.        
        console.info('No suitable Russian voice found.');
        console.info('Speaking with defaultvoice:', u.voice ? u.voice.name : '(default / unknown)');
    }
    synth.cancel(); //stops any ongoing or queued speech immediately so new speech starts right away
    synth.speak(u);
}

/**
 * Make a safe filename from the given text.
 * Allows Russian and English letters, numbers, and underscores.
 * Replaces spaces and special characters with underscores.
 * Trims to a desired length.
 * @param {string} text - The input text to convert.
 * @param {number} [maxLength=20] - Maximum length of the resulting filename.
 * @returns {string} The sanitized filename.
 */
function safeFileName(text, maxLength = 20) {
    // Replace anything that's not a letter, number, or underscore with an underscore
    let safe = text.replaceAll('?', '_q');
    safe = safe.replaceAll('!', '_ex');
    safe = safe.replace(/[^\wа-яА-ЯёЁ]/g, '_');
    // Collapse multiple underscores
    safe = safe.replace(/_+/g, '_');
    // Remove underscores from start/end
    safe = safe.replace(/^_+|_+$/g, '');
    // Limit length
    return safe.substring(0, maxLength);
}

/**
 * Create a speaker button and add a click event to play audio or fallback to TTS.
 * @param {string} text - The text to use for audio and speech synthesis.
 * @param {string} [audioPath='../assets/sound/male/'] - The path to the audio files, ending with a slash.
 * @returns {HTMLButtonElement} The created button element.
 */
function createAudioButton(text, audioPath = '../assets/sound/male/') {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'btn btn-sm btn-outline-secondary me-2 speak-btn';
    btn.setAttribute('data-say', text);
    // Accessible label includes the text; keep it short and safe for screen readers
    const safeLabel = `Play pronunciation for ${text}`;
    btn.setAttribute('aria-label', safeLabel);
    btn.textContent = '🔊';

    btn.addEventListener('click', function(ev) {
        ev.stopPropagation();
        const fileName = safeFileName(text);
        const url = `${audioPath}${fileName}.mp3`;
        // encodeURI so non-ASCII filenames (Cyrillic) work in browsers/servers
        const audio = new Audio(encodeURI(url));
        audio.preload = 'metadata';
        audio.onerror = function() {
            speak(text, 'ru-RU');
        };
        audio.play().catch(() => {
            speak(text, 'ru-RU');
        });
    });

    return btn;
}



