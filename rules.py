from cmu_graphics import *
from theme import drawTableBackground, drawPixelText
from button import Button

class Rules:
    def __init__(self, app):
        cx = app.width / 2
        self.subScreen = 'main'

        self.warBtn       = Button('WAR RULES',       cx, app.height * 0.42, 240, 52,
                                   rgb(180, 50, 50),  rgb(220, 80, 80))
        self.blackjackBtn = Button('BLACKJACK RULES', cx, app.height * 0.55, 240, 52,
                                   rgb(50, 50, 180),  rgb(80, 80, 220))
        self.menuBtn      = Button('BACK TO MENU',    cx, app.height * 0.68, 240, 52,
                                   rgb(80, 80, 80),   rgb(120, 120, 120))
        self.backBtn      = Button('BACK',            cx, app.height * 0.9,  160, 44,
                                   rgb(80, 80, 80),   rgb(120, 120, 120))

    def render(self, app):
        drawTableBackground(app)
        if self.subScreen == 'main':
            self._renderMain(app)
        elif self.subScreen == 'war':
            self._renderWarRules(app)
        elif self.subScreen == 'blackjack':
            self._renderBlackjackRules(app)

    def _renderMain(self, app):
        cx = app.width / 2
        drawPixelText('RULES & HOW TO PLAY', cx, app.height * 0.25,
                      rgb(255, 230, 150), scale=1.5)
        drawPixelText('select a game to view its rules', cx, app.height * 0.33,
                      rgb(180, 160, 100), scale=0.8)
        self.warBtn.render()
        self.blackjackBtn.render()
        self.menuBtn.render()

    def _renderWarRules(self, app):
        cx = app.width / 2
        drawPixelText('HOW TO PLAY: WAR', cx, 75, rgb(220, 80, 80), scale=1.3)

        lines = [
            ('SETUP',        rgb(180, 140, 60)),
            ('A 52-card deck is split evenly — 26 cards each.',       rgb(210, 210, 190)),
            ('',             None),
            ('EACH ROUND',   rgb(180, 140, 60)),
            ('Both players flip their top card.',                      rgb(210, 210, 190)),
            ('Higher card wins — winner takes both cards.',            rgb(210, 210, 190)),
            ('Card ranking: 2 (low) — 10 — J — Q — K — Ace (high).', rgb(210, 210, 190)),
            ('',             None),
            ('WAR (TIE)',    rgb(180, 140, 60)),
            ('Each player places up to 3 cards face-down,',           rgb(210, 210, 190)),
            ('then flips one battle card. Higher card takes all.',     rgb(210, 210, 190)),
            ('Double tie during war: all cards return to their owners.', rgb(210, 210, 190)),
            ('',             None),
            ('WINNING',      rgb(180, 140, 60)),
            ('First player to collect all 52 cards wins!',            rgb(210, 210, 190)),
        ]

        startY = 120
        lineH  = 28
        for i, (text, color) in enumerate(lines):
            if text and color:
                bold = color == rgb(180, 140, 60)
                drawLabel(text, cx, startY + i * lineH,
                          size=13, bold=bold, fill=color, font='monospace')

        self.backBtn.render()

    def _renderBlackjackRules(self, app):
        cx = app.width / 2
        drawPixelText('HOW TO PLAY: BLACKJACK', cx, 75, rgb(80, 130, 220), scale=1.3)

        lines = [
            ('GOAL',         rgb(180, 140, 60)),
            ('Beat the dealer by getting closer to 21 without going over.',  rgb(210, 210, 190)),
            ('Up to 3 players compete against the dealer.',                  rgb(210, 210, 190)),
            ('',             None),
            ('CARD VALUES',  rgb(180, 140, 60)),
            ('Numbered cards = face value.  J / Q / K = 10.  Ace = 1 or 11.', rgb(210, 210, 190)),
            ('',             None),
            ('YOUR TURN',    rgb(180, 140, 60)),
            ('HIT    — take another card.',                                   rgb(210, 210, 190)),
            ('STAND  — end your turn and keep your total.',                   rgb(210, 210, 190)),
            ('DOUBLE — double your bet, receive exactly one more card.',      rgb(210, 210, 190)),
            ('SPLIT  — if your two opening cards match, split into two hands.', rgb(210, 210, 190)),
            ('',             None),
            ('PAYOUTS',      rgb(180, 140, 60)),
            ('Blackjack (Ace + 10-value on the deal) pays 3 to 2.',          rgb(210, 210, 190)),
            ('Dealer must hit until 17 or higher. Bust = lose your bet.',     rgb(210, 210, 190)),
            ('Each player starts with $500. Players at $0 sit out.',          rgb(210, 210, 190)),
        ]

        startY = 120
        lineH  = 26
        for i, (text, color) in enumerate(lines):
            if text and color:
                bold = color == rgb(180, 140, 60)
                drawLabel(text, cx, startY + i * lineH,
                          size=13, bold=bold, fill=color, font='monospace')

        self.backBtn.render()

    def _allButtons(self):
        return [self.warBtn, self.blackjackBtn, self.menuBtn, self.backBtn]

    def _releaseAll(self):
        for b in self._allButtons():
            b.pressed = False

    def handleClick(self, app, mouseX, mouseY):
        for b in self._allButtons():
            if b.isClicked(mouseX, mouseY):
                b.pressed = True

    def handleRelease(self, app, mouseX, mouseY):
        self._releaseAll()
        if self.subScreen == 'main':
            if self.warBtn.isClicked(mouseX, mouseY):
                self.subScreen = 'war'
            elif self.blackjackBtn.isClicked(mouseX, mouseY):
                self.subScreen = 'blackjack'
            elif self.menuBtn.isClicked(mouseX, mouseY):
                app.screenMode = 'menu'
        else:
            if self.backBtn.isClicked(mouseX, mouseY):
                self.subScreen = 'main'
