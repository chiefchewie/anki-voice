const PYCMD_IDENTIFIER = "py";

function testFunction() {
    const x = pycmd(`${PYCMD_IDENTIFIER}:HELLO FROM JAVASCRIPT`);
}

/**
 * @param {string} text
 * @returns {void}
 */
function onSpeechRecognized(text) {
    const x = pycmd(
        `${PYCMD_IDENTIFIER}:HELLO FROM JAVASCRIPT, RECOGNIZED TEXT: ${text}`
    );
}
