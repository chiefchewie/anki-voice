import logging
import os
import sys

# set up path to installed pip packages
package_path = "lib"
sys.path.append(os.path.join(os.path.abspath(__file__), package_path))

from aqt import gui_hooks, mw
from aqt.operations import QueryOp

from .mic import get_vocabulary, initialize, voice_control

# set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# set up add-on
config = mw.addonManager.getConfig(__name__)
vocab = get_vocabulary(config)
device, samplerate, recognizer, stream = initialize(vocab)


def on_profile_did_open():
    stream.start()
    logger.info("main: stream opened")


def on_profile_will_close():
    stream.stop()
    stream.close()
    logger.info("main: stream closed")


def on_success(op_val) -> None:
    logger.info(f"on_success: op finished with return value {op_val}")
    if op_val == vocab.show:
        mw.reviewer._showAnswer()
    elif op_val == vocab.again:
        mw.reviewer._answerCard(1)
    elif op_val == vocab.good:
        mw.reviewer._answerCard(mw.reviewer._defaultEase())


def on_card_will_show(text: str, card, kind: str):
    voice_timeout = config.get("timeout", 10)
    op = QueryOp(
        parent=mw,
        op=lambda _col: voice_control(
            stream, 8000, recognizer, kind, vocab, voice_timeout
        ),
        success=on_success,
    )
    op.with_progress("voice mode in progress... say 'STOP' to stop").run_in_background()
    return text


gui_hooks.profile_did_open.append(on_profile_did_open)
gui_hooks.profile_will_close.append(on_profile_will_close)
gui_hooks.card_will_show.append(on_card_will_show)
