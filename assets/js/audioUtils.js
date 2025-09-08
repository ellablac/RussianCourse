/**
 * Speak the given text in Russian using speech synthesis (Web Speech API).
 * Simple Text-to-speech API, no audio files needed. The quality of the russian
 * voice is not great. Currently used as a fallback if no audio file is found.
 * @see https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
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
    const voices = synth.getVoices ? synth.getVoices() : [];
    const ru = voices.find(v => v.lang && v.lang.toLowerCase().startsWith('ru'));
    if (ru) u.voice = ru;
    synth.cancel();
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
    let safe = text.replace(/[^\wа-яА-ЯёЁ]/g, '_');
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
    btn.setAttribute('aria-label', 'Play pronunciation');
    btn.textContent = '🔊';

    btn.addEventListener('click', function(ev) {
        ev.stopPropagation();
        const fileName = safeFileName(text);
        const audio = new Audio(`${audioPath}${fileName}.mp3`);
        audio.onerror = function() {
            speak(text, 'ru-RU');
        };
        audio.play().catch(() => {
            speak(text, 'ru-RU');
        });
    });

    return btn;
}