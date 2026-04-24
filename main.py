from cmu_graphics import *
from card import *
from button import *
from war import *
from blackjack import *
from rules import Rules
from theme import *

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

def onKeyPress(app, key):
    if app.screenMode == 'menu':
        if key == 'r':
            app.rulesScreen = Rules(app)
            app.screenMode = 'rules'
    if app.screenMode == 'war':
        app.warGame.handleKey(app, key)

def onStep(app):
    pass

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
