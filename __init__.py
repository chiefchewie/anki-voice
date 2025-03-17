from typing import Any

import aqt.reviewer
from aqt import gui_hooks, mw
import aqt.webview

PYCMD_IDENTIFIER = "vox"


def on_reviewer_did_show_answer(_card):
    reviewer = mw.reviewer
    reviewer.bottom.web.eval("testFunction()")


def webview_message_handler(reviewer: aqt.reviewer.Reviewer, message: str):
    print(f"!!! RECEIVED MESSAGE: {message}")
    pass


def on_webview_did_receive_js_message(
    handled: tuple[bool, Any], message: str, context: Any
):
    if not isinstance(context, aqt.reviewer.ReviewerBottomBar):
        return handled

    if not message.startswith(PYCMD_IDENTIFIER):
        return handled

    reviewer = context.reviewer
    response = webview_message_handler(reviewer, message)

    return (True, response)

def on_webview_will_set_content(web_content: aqt.webview.WebContent, context: Any):
    addon_package = mw.addonManager.addonFromModule(__name__)
    web_content.js.append(f"/_addons/{addon_package}/web/index.js")

gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
gui_hooks.reviewer_did_show_answer.append(on_reviewer_did_show_answer)
gui_hooks.webview_did_receive_js_message.append(on_webview_did_receive_js_message)


# https://github.com/glutanimate/speed-focus-mode/
# automatically alert/show/again after x seconds
# can use what they did as inspiration
# to launch voice-recognizer process, and process voice cmd to show/answer accordingly

# basic idea:
# on_show_answer: from python hook, call a js function that sends a message (and also does the voice recognition)
# on_receive_js_msg: filter for the js message, determine the command (show/answer) and run it
