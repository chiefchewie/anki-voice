# import the main window object (mw) from aqt
from aqt import mw

from aqt import gui_hooks

# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect

# import all of the Qt GUI library
from aqt.qt import *

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

def testFunction() -> None:
    # get the number of cards in the current collection, which is stored in
    # the main window
    if mw.col is not None:
        cardCount = mw.col.card_count()
        # show a message box
        _ = showInfo(f"Card count: {cardCount}")

# create a new menu item, "test"
action = QAction("test", mw)

# set it to call testFunction when it's clicked
qconnect(action.triggered, testFunction)

# and add it to the tools menu
mw.form.menuTools.addAction(action)


test_state = 1

# testing with hooks
def foo(card):
    print(f"!!! question show with card: {card.question()}")

    # this blocks ui thread, card will not be shown until foo returns
    ease = int(input("!!! please enter something: "))
    print(f"!!! user entered ease: {ease}")
    mw.col.sched.answerCard(card, ease)

gui_hooks.reviewer_did_show_answer.append(foo)
