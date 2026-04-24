"""
============================================================
CARD GAME SUITE — CMU 15-112 Final Project
Riyan Bilimoria Kadribegovic
============================================================
This string generated with the help of Claude.

An 8-bit style card game suite featuring two fully-playable games
sharing a common table/UI framework: WAR (2-player) and BLACKJACK
(1-3 players vs. dealer).

KEY FEATURES
------------
WAR: Phase-based state machine with full WAR sequence on ties,
correct DOUBLE TIE handling (cards returned to owners), and
hold-RIGHT to speed-play.

BLACKJACK: 1-3 players, 6-deck shoe, real betting (chip stacking +
CLEAR), HIT/STAND/DOUBLE/SPLIT with parallel bet tracking, dealer
stands on 17, 3:2 blackjack payout, sit-out at $0, game-over screen when 
all players out of chips.

SHARED: Rules screen, custom Button class with press animation,
cohesive felt-table theme, reusable Card/Deck/Hand/PresetDeck layer.

GRADING SHORTCUTS
-----------------
MAIN MENU:
  R         → Open Rules screen

WAR screen:
  DEV       → 4-round scripted hand walking through every phase:
              R1 normal win, R2 normal loss, R3 tie→war win,
              R4 tie→war DOUBLE TIE (cards returned)
  NORMAL    → Exit dev mode, return to shuffled deck
  SPACE     → Flip / Next (mirrors on-screen button)
  Hold →    → Speed-play through rounds

BLACKJACK screen:
  DEV       → 3-player scripted demo with yellow highlight on the
              next button to press. Showcases:
              Hand 1: HIT-to-bust, STAND, dealer 19
              Hand 2: blackjack skip, SPLIT 8s (one win/one loss)
              Hand 3: dealer blackjack PUSH, LOSE, HIT-to-bust

ALL GAMES:
  MENU      → Return to main menu (top-left, always visible)
============================================================
Grading Guidance
1. Blackjack equal card bet splitting
2. UX Blackjack dev mode with button highlights
3. 6-deck shoe, auto-reshuffle below 52 cards
4. Dynamic card spacing
5. Blackjack bankruptcy logic
6. War phase states
7. Hold right arrow to speed-play War
============================================================
AI USAGE NOTE:
Most AI indicator notes will be at the top of each file 
rather than before specific functions because a lot of the 
same categories of items (ex. rendering) are all written by
Claude. However, in cases where some logic was AI-written,
notes are included above functions.
"""

from cmu_graphics import *
from card import *
from button import *
from war import *
from blackjack import *
from rules import Rules
from theme import *

# All Button spacings, colors, etc. are written by Claude
# You can safely assume Claude wrote anything with "draw" or "render" in it
# Unless it's specific logic like the changing screens. I called the functions,
# but Claude wrote them

def onAppStart(app):
    app.screenMode = 'menu'
    app.width = 800
    app.height = 600
    app.warGame = None
    app.blackjackGame = None
    app.rulesScreen = None
    app.menuButtons = [
        Button('WAR',       app.width/2, 320, 260, 56,
               rgb(180, 50, 50),  rgb(220, 80, 80)),
        Button('BLACKJACK', app.width/2, 400, 260, 56,
               rgb(50, 50, 180),  rgb(80, 80, 220)),
    ]

def handleMenuButtons(app, button):
    if button.label == 'WAR':
        app.warGame = War(app)
        app.screenMode = 'war'
    elif button.label == 'BLACKJACK':
        app.blackjackGame = Blackjack(app)
        app.screenMode = 'blackjack'

def redrawAll(app):
    drawScreen(app)

def onMousePress(app, mouseX, mouseY):
    if app.screenMode == 'menu':
        for button in app.menuButtons:
            if button.isClicked(mouseX, mouseY):
                button.pressed = True
    elif app.screenMode == 'war':
        app.warGame.handleClick(app, mouseX, mouseY)
    elif app.screenMode == 'blackjack':
        app.blackjackGame.handleClick(app, mouseX, mouseY)
    elif app.screenMode == 'rules':
        app.rulesScreen.handleClick(app, mouseX, mouseY)

def onMouseRelease(app, mouseX, mouseY):
    if app.screenMode == 'menu':
        for button in app.menuButtons:
            if button.pressed and button.isClicked(mouseX, mouseY):
                handleMenuButtons(app, button)
            button.pressed = False
    elif app.screenMode == 'war':
        app.warGame.handleRelease(app, mouseX, mouseY)
    elif app.screenMode == 'blackjack':
        app.blackjackGame.handleRelease(app, mouseX, mouseY)
    elif app.screenMode == 'rules':
        app.rulesScreen.handleRelease(app, mouseX, mouseY)

def onKeyHold(app, keys):
    if app.screenMode == 'war':
        app.warGame.handleKeyHold(app, keys)

def onKeyPress(app, key):
    if app.screenMode == 'menu':
        if key == 'r':
            app.rulesScreen = Rules(app)
            app.screenMode = 'rules'
    if app.screenMode == 'war':
        app.warGame.handleKey(app, key)

def drawScreen(app):
    if app.screenMode == 'menu':
        drawMenu(app)
    elif app.screenMode == 'rules':
        app.rulesScreen.render(app)
    elif app.screenMode == 'war':
        app.warGame.render(app)
    elif app.screenMode == 'blackjack':
        app.blackjackGame.render(app)

def drawMenu(app):
    drawMenuScreen(app)
    for button in app.menuButtons:
        button.render()

def main():
    runApp()

main()
