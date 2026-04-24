from cmu_graphics import *
from card import Deck, Hand
from button import Button
from theme import drawTableBackground, drawPixelText

# All Button spacings, colors, etc. are written by Claude

class War:
    def __init__(self, app):
        # CHANGED: removed unused self.cx/cy, condensed cardValues to one line per row
        self.deck = Deck()
        self.cardValues = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
            '7': 7, '8': 8, '9': 9, '10': 10,
            'Jack': 11, 'Queen': 12, 'King': 13, 'Ace': 14
        }
        self.initializeHands()

        # ADDED: buttons stored in a dict so handlers can look them up by name.
        # All positions/sizes use proportional multipliers so the layout scales
        # correctly if the window size ever changes.
        # 'flip' and 'next' share the same position — only one is shown at a time.
        cx, cy = app.width / 2, app.height / 2
        self.buttons = {
            # CHANGED: moved flip/next down to cy*1.47 to stop overlapping the "YOU" label
            'flip':  Button('FLIP',       cx,       cy * 1.47, app.width * 0.2,  app.height * 0.08, rgb(180, 50, 50),  rgb(220, 80, 80)),
            'next':  Button('NEXT',       cx,       cy * 1.47, app.width * 0.2,  app.height * 0.08, rgb(50, 130, 80),  rgb(80, 180, 110)),
            'menu':  Button('MENU',       cx * 0.2, cy * 0.17, app.width * 0.125, app.height * 0.06, rgb(80, 80, 80),  rgb(120, 120, 120)),
            # CHANGED: moved again up so it stays inside the game-over box
            'again': Button('PLAY AGAIN', cx,       cy * 1.43, app.width * 0.25, app.height * 0.08, rgb(50, 130, 80),  rgb(80, 180, 110)),
            'dev':    Button('DEV',    cx * 1.8, cy * 0.17, app.width * 0.1, app.height * 0.06, rgb(80, 50, 120),  rgb(120, 80, 180)),
            'normal': Button('NORMAL', cx * 1.8, cy * 0.17, app.width * 0.1, app.height * 0.06, rgb(140, 80, 30),  rgb(190, 120, 50)),
        }
        self.devMode = False

        # ADDED: phase controls which screen and buttons are shown each frame:
        #   'idle'     — waiting for the player to press FLIP
        #   'result'   — a normal flip resolved; one player won the round
        #   'war'      — a tie triggered war and war resolved; someone won
        #   'draw'     — a double tie occurred; all cards were returned to owners
        #   'gameOver' — one player ran out of cards; game is over
        self.phase = 'idle'
        self.card1 = None       # player's most recently flipped card (shown in result phase)
        self.card2 = None       # opponent's most recently flipped card
        self.roundWinner = 0    # 1 = player won, 2 = opponent won, 0 = tie/draw
        self.resultText = ''    # message shown in the result/war/draw banner
        self.gameWinner = 0     # set when phase becomes 'gameOver': 1 or 2
        # warFaceDown/warCard hold the cards placed during a war sequence so
        # render() can display them after _startWar() has already moved the
        # cards into the winner's hand
        self.warFaceDown1 = []  # the ≤3 face-down cards player 1 put up in the last war
        self.warFaceDown2 = []  # the ≤3 face-down cards player 2 put up in the last war
        self.warCard1 = None    # player 1's war reveal card
        self.warCard2 = None    # player 2's war reveal card
        # CHANGED: warPot1/2 are now instance variables because the war sequence is
        # split into two phases (warSetup → war/draw) separated by a button press;
        # the pots need to persist between _setupWar() and _resolveWar()
        self.warPot1 = []       # all cards from player 1 in the current war pot
        self.warPot2 = []       # all cards from player 2 in the current war pot


    def initializeHands(self):
        self.hand1, self.hand2 = Hand(), Hand()
        self.hands = [self.hand1, self.hand2]
        # deals out the deck alternatingly
        for i in range(52):
            self.deck.deal(self.hands[i % 2], 1)

    # CHANGED: rewrote handleFlip — original had three bugs:
    #   1. getWarGameValue received a Card object but indexed with it directly (needed card.name)
    #   2. cards were never set faceUp=True, so render() would show them face-down
    #   3. war logic called playWarSequence which had its own bugs (see _startWar below)
    def handleFlip(self):
        # safety check in case game-over state was somehow missed
        if self.hand1.getCount() == 0 or self.hand2.getCount() == 0:
            self._checkGameOver()
            return

        self.card1 = self.hand1.removeTopCard()
        self.card2 = self.hand2.removeTopCard()
        # flip face-up so render() draws the front of the card
        self.card1.faceUp = True
        self.card2.faceUp = True

        val1 = self.getWarGameValue(self.card1)
        val2 = self.getWarGameValue(self.card2)

        if val1 > val2:
            self.roundWinner = 1
            self.resultText = 'YOU WIN THIS ROUND!'
            # CHANGED: addCardToBottom so won cards go to the opposite end of the
            # deck from where cards are drawn, preventing the same card looping back
            self.hand1.addCardToBottom(self.card1)
            self.hand1.addCardToBottom(self.card2)
            self.phase = 'result'
        elif val2 > val1:
            self.roundWinner = 2
            self.resultText = 'OPPONENT WINS!'
            self.hand2.addCardToBottom(self.card1)
            self.hand2.addCardToBottom(self.card2)
            self.phase = 'result'
        else:
            # Tie — seed each player's pot with their flipped card,
            # then _setupWar draws the face-down cards and waits for the player to flip
            self.warPot1 = [self.card1]
            self.warPot2 = [self.card2]
            self._setupWar()

    # CHANGED: fixed bug where card (a Card object) was used as a dict key directly;
    # needs card.name to look up the string key in cardValues
    def getWarGameValue(self, card):
        return self.cardValues[card.name]

    # ADDED: phase 1 of the war sequence — draws the face-down cards from each
    # player's hand and sets phase='warSetup' so the player can see them before
    # pressing FLIP to reveal the war card
    def _setupWar(self):
        if self.hand1.getCount() == 0:
            self.gameWinner = 2
            self.phase = 'gameOver'
            return
        if self.hand2.getCount() == 0:
            self.gameWinner = 1
            self.phase = 'gameOver'
            return

        # each player puts up to 3 cards face-down; always reserve at least 1 for the reveal
        faceDown1 = min(3, self.hand1.getCount() - 1)
        faceDown2 = min(3, self.hand2.getCount() - 1)

        self.warFaceDown1 = []
        self.warFaceDown2 = []

        for _ in range(faceDown1):
            c = self.hand1.removeTopCard()
            c.faceUp = False
            self.warFaceDown1.append(c)
            self.warPot1.append(c)

        for _ in range(faceDown2):
            c = self.hand2.removeTopCard()
            c.faceUp = False
            self.warFaceDown2.append(c)
            self.warPot2.append(c)

        self.phase = 'warSetup'

    # ADDED: phase 2 of the war sequence — called when the player presses FLIP
    # in the warSetup phase; draws the reveal cards, compares them, and awards
    # the pot to the winner (or returns all cards on a double tie)
    def _resolveWar(self):
        if self.hand1.getCount() == 0:
            self.gameWinner = 2
            self.phase = 'gameOver'
            return
        if self.hand2.getCount() == 0:
            self.gameWinner = 1
            self.phase = 'gameOver'
            return

        self.warCard1 = self.hand1.removeTopCard()
        self.warCard2 = self.hand2.removeTopCard()
        self.warCard1.faceUp = True
        self.warCard2.faceUp = True
        self.warPot1.append(self.warCard1)
        self.warPot2.append(self.warCard2)

        val1 = self.getWarGameValue(self.warCard1)
        val2 = self.getWarGameValue(self.warCard2)

        if val1 > val2:
            self.roundWinner = 1
            self.resultText = 'YOU WIN THE WAR!'
            for c in self.warPot1 + self.warPot2:
                self.hand1.addCardToBottom(c)
            self.warPot1 = []
            self.warPot2 = []
            self.phase = 'war'
        elif val2 > val1:
            self.roundWinner = 2
            self.resultText = 'OPPONENT WINS THE WAR!'
            for c in self.warPot1 + self.warPot2:
                self.hand2.addCardToBottom(c)
            self.warPot1 = []
            self.warPot2 = []
            self.phase = 'war'
        else:
            # Double tie — return every card to its original owner; no winner
            self.roundWinner = 0
            self.resultText = 'All cards returned.'
            for c in self.warPot1:
                self.hand1.addCardToBottom(c)
            for c in self.warPot2:
                self.hand2.addCardToBottom(c)
            self.warPot1 = []
            self.warPot2 = []
            self.phase = 'draw'

    # ADDED: sets gameWinner and phase='gameOver' if either hand is empty
    def _checkGameOver(self):
        if self.hand1.getCount() == 0:
            self.gameWinner = 2
            self.phase = 'gameOver'
        elif self.hand2.getCount() == 0:
            self.gameWinner = 1
            self.phase = 'gameOver'

    # ADDED: called when the player presses NEXT or SPACE after seeing a result.
    # checks for game over first (in case the last round emptied a hand),
    # then clears all per-round display state and returns to 'idle'
    def _nextRound(self):
        self._checkGameOver()
        if self.phase != 'gameOver':
            self.phase = 'idle'
            self.card1 = self.card2 = None
            self.warCard1 = self.warCard2 = None
            self.warFaceDown1 = []
            self.warFaceDown2 = []
            self.warPot1 = []   # CHANGED: pots are now instance vars, clear them here
            self.warPot2 = []
            self.roundWinner = 0
            self.resultText = ''

    # ADDED: main render dispatcher — draws the shared background, player labels,
    # and deck piles every frame, then calls the helper for the current phase
    def render(self, app):
        drawTableBackground(app)
        cx, cy = app.width / 2, app.height / 2

        # CHANGED: tightened vertical layout so labels, cards, and buttons don't overlap.
        # Opponent zone: y≈75 (label), y≈96 (cards).  Player zone: y≈270 (cards), y≈384 (label).
        drawPixelText('OPPONENT', cx * 0.65, cy * 0.25,  rgb(180, 140, 60), scale=1)
        drawPixelText(f'{self.hand2.getCount()} cards', cx * 1.55, cy * 0.25, rgb(150, 150, 130), scale=0.8)
        drawPixelText('YOU',      cx * 0.83, cy * 1.28,  rgb(180, 140, 60), scale=1)
        drawPixelText(f'{self.hand1.getCount()} cards', cx * 1.55, cy * 1.28, rgb(150, 150, 130), scale=0.8)

        # deck piles: opponent top-left, player bottom-right — y aligned with card zones
        if self.hand2.getCount() > 0:
            self._drawCardPile(app.width * 0.08, cy * 0.32, self.hand2.getCount())
        if self.hand1.getCount() > 0:
            self._drawCardPile(app.width * 0.84, cy * 0.90, self.hand1.getCount())

        if self.phase == 'idle':
            self._renderIdle(app, cx, cy)
        elif self.phase == 'result':
            self._renderResult(app, cx, cy)
        elif self.phase == 'warSetup':
            self._renderWarSetup(app, cx, cy)
        elif self.phase == 'war':
            self._renderWar(app, cx, cy)
        elif self.phase == 'draw':
            self._renderDraw(app, cx, cy)
        elif self.phase == 'gameOver':
            self._renderGameOver(app, cx, cy)

        self.buttons['menu'].render()
        if self.devMode:
            self.buttons['normal'].render()
        else:
            self.buttons['dev'].render()

    # ADDED: draws the pre-flip state — ghost outlines where cards will appear,
    # a centered VS divider line, and the FLIP button
    def _renderIdle(self, app, cx, cy):
        # ghost card outlines showing where each player's card will land on flip
        drawRect(cx - 30, cy * 0.32, 60, 84, fill=None,
                 border=rgb(180, 140, 60), borderWidth=1, opacity=50)
        drawRect(cx - 30, cy * 0.90, 60, 84, fill=None,
                 border=rgb(180, 140, 60), borderWidth=1, opacity=50)
        # horizontal gold divider with VS label centered on it
        drawRect(cx - app.width * 0.35, cy * 0.71, app.width * 0.7, 2, fill=rgb(180, 140, 60))
        drawPixelText('VS', cx, cy * 0.71, rgb(180, 140, 60), scale=1.2)
        self.buttons['flip'].render()
        drawPixelText('[ SPACE ]', cx, cy * 1.63, rgb(120, 120, 100), scale=0.7)

    # ADDED: shows the two flipped cards face-up and a colored result banner
    # (green if player won, red if opponent won)
    def _renderResult(self, app, cx, cy):
        if self.card2:
            self.card2.render(cx - 30, cy * 0.32)  # opponent's card in the top half
        if self.card1:
            self.card1.render(cx - 30, cy * 0.90)  # player's card in the bottom half
        color = rgb(50, 180, 80) if self.roundWinner == 1 else rgb(180, 50, 50)
        self._drawBanner(cx, cy * 0.72, app.width * 0.5, app.height * 0.08, color, self.resultText)
        self.buttons['next'].render()
        drawPixelText('[ SPACE ]', cx, cy * 1.63, rgb(120, 120, 100), scale=0.7)

    # ADDED: shown after a tie before the war reveal flip.
    # Tied cards are displayed in the center; each player's ≤3 face-down war
    # cards fan out towards the outside edges of the table.
    # The player presses FLIP (or SPACE) to draw the war reveal cards.
    def _renderWarSetup(self, app, cx, cy):
        # tied flip cards stay in the center
        if self.card2:
            self.card2.render(cx - 30, cy * 0.32)
        if self.card1:
            self.card1.render(cx - 30, cy * 0.90)
        # opponent's face-down war cards fan left from the tied card (step=66px)
        for i, c in enumerate(self.warFaceDown2):
            c.render(cx - 110 - i * 66, cy * 0.32)
        # player's face-down war cards fan right from the tied card (step=66px)
        for i, c in enumerate(self.warFaceDown1):
            c.render(cx + 50 + i * 66, cy * 0.90)
        # gold TIE banner
        self._drawBanner(cx, cy * 0.72, app.width * 0.52, app.height * 0.08,
                         rgb(100, 80, 20), 'TIE!  WAR NEEDED...')
        self.buttons['flip'].render()
        drawPixelText('[ SPACE ]', cx, cy * 1.63, rgb(120, 120, 100), scale=0.7)

    # ADDED: war layout — face-down stacks on the outer sides, reveal cards closer
    # to center so the two reveal cards face each other across the divider.
    # Cards are iterated in reverse so index 0 (front card) is drawn last (on top).
    def _renderWar(self, app, cx, cy):
        # opponent's face-down stack (left of center), then their reveal (right of center)
        for i in range(len(self.warFaceDown2) - 1, -1, -1):
            self.warFaceDown2[i].render(cx - 110 - i * 66, cy * 0.32)
        if self.warCard2:
            self.warCard2.render(cx + 50, cy * 0.32)
        # player's reveal (left of center), then their face-down stack (right of center)
        if self.warCard1:
            self.warCard1.render(cx - 110, cy * 0.90)
        for i in range(len(self.warFaceDown1) - 1, -1, -1):
            self.warFaceDown1[i].render(cx + 50 + i * 66, cy * 0.90)
        # red WAR! banner + result text below it
        self._drawBanner(cx, cy * 0.72, app.width * 0.5, app.height * 0.08, rgb(140, 25, 25),
                         'W A R !', scale=1.3)
        resultColor = rgb(50, 180, 80) if self.roundWinner == 1 else rgb(180, 50, 50)
        drawPixelText(self.resultText, cx, cy * 0.87, resultColor, scale=0.85)
        self.buttons['next'].render()
        drawPixelText('[ SPACE ]', cx, cy * 1.63, rgb(120, 120, 100), scale=0.7)

    # ADDED: same card layout as _renderWar but with a gold "DOUBLE TIE!" banner
    # since no one won; the cards shown are the ones that were just returned to owners
    def _renderDraw(self, app, cx, cy):
        for i in range(len(self.warFaceDown2) - 1, -1, -1):
            self.warFaceDown2[i].render(cx - 110 - i * 66, cy * 0.32)
        if self.warCard2:
            self.warCard2.render(cx + 50, cy * 0.32)
        if self.warCard1:
            self.warCard1.render(cx - 110, cy * 0.90)
        for i in range(len(self.warFaceDown1) - 1, -1, -1):
            self.warFaceDown1[i].render(cx + 50 + i * 66, cy * 0.90)
        self._drawBanner(cx, cy * 0.72, app.width * 0.525, app.height * 0.08, rgb(100, 80, 20),
                         'DOUBLE TIE!', scale=1.3)
        drawPixelText(self.resultText, cx, cy * 0.87, rgb(200, 200, 180), scale=0.85)
        self.buttons['next'].render()
        drawPixelText('[ SPACE ]', cx, cy * 1.63, rgb(120, 120, 100), scale=0.7)

    # ADDED: dims the screen, draws a centered bordered box, and shows
    # a win/loss message with a PLAY AGAIN button
    def _renderGameOver(self, app, cx, cy):
        drawRect(0, 0, app.width, app.height, fill='black', opacity=50)
        bw, bh = app.width * 0.65, app.height * 0.33
        bx, by = cx - bw / 2, cy - bh / 2
        # outer dark box + inner dark-red fill + gold pixel border on all four sides
        drawRect(bx,     by,     bw,     bh,     fill=rgb(30, 15, 8))
        drawRect(bx + 2, by + 2, bw - 4, bh - 4, fill=rgb(70, 25, 25))
        drawRect(bx,          by,          bw, 4,  fill=rgb(200, 160, 50))
        drawRect(bx,          by + bh - 4, bw, 4,  fill=rgb(200, 160, 50))
        drawRect(bx,          by,          4,  bh,  fill=rgb(200, 160, 50))
        drawRect(bx + bw - 4, by,          4,  bh,  fill=rgb(200, 160, 50))
        if self.gameWinner == 1:
            drawPixelText('YOU WIN!', cx, cy * 0.85, rgb(255, 230, 150), scale=2)
            drawPixelText('Congratulations!', cx, cy * 1.07, rgb(200, 200, 180), scale=1)
        else:
            drawPixelText('OPPONENT WINS', cx, cy * 0.85, rgb(255, 100, 100), scale=1.5)
            drawPixelText('Better luck next time.', cx, cy * 1.07, rgb(200, 200, 180), scale=1)
        self.buttons['again'].render()

    # ADDED: reusable banner drawn from a center x and a top y.
    # Layers: dark backing → colored fill → gold top/bottom border lines → centered text
    def _drawBanner(self, cx, y, w, h, fillColor, text, scale=1):
        hw = w / 2
        drawRect(cx - hw,     y,         w,     h,     fill=rgb(30, 15, 8))
        drawRect(cx - hw + 2, y + 2,     w - 4, h - 4, fill=fillColor)
        drawRect(cx - hw,     y,         w,     3,     fill=rgb(200, 160, 50))
        drawRect(cx - hw,     y + h - 3, w,     3,     fill=rgb(200, 160, 50))
        drawPixelText(text, cx, y + h / 2 - 4, rgb(255, 230, 150), scale=scale)

    # ADDED: draws a face-down card pile at (x, y).
    # Each card is offset 2px right and 2px down from the card in front of it,
    # giving a depth illusion. Back cards are drawn first so the front card sits on top.
    # Depth capped at 6 so even a 26-card hand stays a tidy pile.
    def _drawCardPile(self, x, y, count):
        depth = min(count, 6)
        for i in range(depth - 1, -1, -1):  # draw back-to-front
            ox, oy = i * 2, i * 2
            drawRect(x + ox, y + oy, 60, 84,
                     fill=rgb(180, 30, 30), border=rgb(60, 60, 60), borderWidth=1)
            drawRect(x + ox + 3, y + oy + 3, 54, 78,
                     fill=None, border='white', borderWidth=1)

    # CHANGED: only marks a button as pressed if it is currently visible for
    # the active phase — fixes a bug where 'flip' and 'next' share the same
    # screen position, causing both to fire on one click and skip the result screen
    def handleClick(self, app, mouseX, mouseY):
        for key, btn in self.buttons.items():
            if self._buttonVisible(key) and btn.isClicked(mouseX, mouseY):
                btn.pressed = True

    def _buttonVisible(self, key):
        if key == 'flip':
            return self.phase in ('idle', 'warSetup')
        if key == 'next':
            return self.phase in ('result', 'war', 'draw')
        if key == 'again':
            return self.phase == 'gameOver'
        if key == 'dev':
            return not self.devMode
        if key == 'normal':
            return self.devMode
        return True  # 'menu' always visible

    # ADDED: on release, fires the button action only if the mouse is still
    # over the same button that was pressed (standard click behavior);
    # then clears all pressed states regardless
    def handleRelease(self, app, mouseX, mouseY):
        for key, btn in self.buttons.items():
            if btn.pressed and btn.isClicked(mouseX, mouseY):
                self._onButton(app, key)
            btn.pressed = False

    # ADDED: routes button presses to the correct action based on current phase,
    # so off-screen buttons that share a position can't fire accidentally
    def _onButton(self, app, key):
        if key == 'flip' and self.phase == 'idle':
            self.handleFlip()
        elif key == 'flip' and self.phase == 'warSetup':  # ADDED: war reveal flip
            self._resolveWar()
        elif key == 'next' and self.phase in ('result', 'war', 'draw'):
            self._nextRound()
        elif key == 'menu':
            app.screenMode = 'menu'
        elif key == 'again' and self.phase == 'gameOver':
            app.warGame = War(app)
        elif key == 'dev':
            self._devTest()
        elif key == 'normal':
            self._exitDev()

    # ADDED: replaces both hands with a 13-card preset that walks through every phase
    # in order. Cards are listed bottom→top (last element = drawn first).
    # Sequence: R1 player wins (A vs 2), R2 opponent wins (3 vs K),
    #           R3 tie→war player wins (7v7, then K vs 5 reveal),
    #           R4 tie→war double tie (Q vs Q, then J vs J reveal).
    # After R4 both players' cards are returned, player retains enough for a win.
    def _devTest(self):
        from card import Card
        self.hand1.cards = [
            Card('Ace',   'Hearts'),    # index 0  — deep buffer, drawn last
            Card('Jack',  'Hearts'),    # index 1  — R4 war reveal (J ties J → double tie)
            Card('8',     'Spades'),    # index 2  — R4 war fd3
            Card('5',     'Spades'),    # index 3  — R4 war fd2
            Card('3',     'Spades'),    # index 4  — R4 war fd1
            Card('Queen', 'Spades'),    # index 5  — R4 tie card (Q vs Q)
            Card('King',  'Hearts'),    # index 6  — R3 war reveal (K beats 5 → win)
            Card('6',     'Diamonds'),  # index 7  — R3 war fd3
            Card('4',     'Diamonds'),  # index 8  — R3 war fd2
            Card('2',     'Diamonds'),  # index 9  — R3 war fd1
            Card('7',     'Hearts'),    # index 10 — R3 tie card (7 vs 7)
            Card('3',     'Clubs'),     # index 11 — R2 flip (3 loses to K)
            Card('Ace',   'Spades'),    # index 12 — R1 flip (A beats 2) ← drawn first
        ]
        self.hand2.cards = [
            Card('2',     'Hearts'),    # index 0  — deep buffer, drawn last
            Card('Jack',  'Diamonds'),  # index 1  — R4 war reveal (J ties J → double tie)
            Card('9',     'Hearts'),    # index 2  — R4 war fd3
            Card('6',     'Hearts'),    # index 3  — R4 war fd2
            Card('4',     'Hearts'),    # index 4  — R4 war fd1
            Card('Queen', 'Hearts'),    # index 5  — R4 tie card (Q vs Q)
            Card('5',     'Clubs'),     # index 6  — R3 war reveal (5 loses to K)
            Card('2',     'Clubs'),     # index 7  — R3 war fd3
            Card('10',    'Clubs'),     # index 8  — R3 war fd2
            Card('9',     'Clubs'),     # index 9  — R3 war fd1
            Card('7',     'Diamonds'), # index 10 — R3 tie card (7 vs 7)
            Card('King',  'Clubs'),     # index 11 — R2 flip (K beats 3)
            Card('2',     'Spades'),    # index 12 — R1 flip (2 loses to A) ← drawn first
        ]
        # reset all per-round state so the preset starts clean from 'idle'
        self.phase = 'idle'
        self.card1 = self.card2 = None
        self.warCard1 = self.warCard2 = None
        self.warFaceDown1 = []
        self.warFaceDown2 = []
        self.warPot1 = []
        self.warPot2 = []
        self.roundWinner = 0
        self.resultText = ''
        self.gameWinner = 0
        self.devMode = True

    def _exitDev(self):
        self.deck = Deck()
        self.initializeHands()
        self.phase = 'idle'
        self.card1 = self.card2 = None
        self.warCard1 = self.warCard2 = None
        self.warFaceDown1 = []
        self.warFaceDown2 = []
        self.warPot1 = []
        self.warPot2 = []
        self.roundWinner = 0
        self.resultText = ''
        self.gameWinner = 0
        self.devMode = False

    # ADDED: space mirrors the visible action button (FLIP or NEXT);
    # escape returns to the main menu from anywhere in the game
    def handleKey(self, app, key):
        if key == 'space':
            if self.phase == 'idle':
                self.handleFlip()
            elif self.phase == 'warSetup':   # ADDED: war reveal flip via spacebar
                self._resolveWar()
            elif self.phase in ('result', 'war', 'draw'):
                self._nextRound()
        elif key == 'escape':
            app.screenMode = 'menu'

    def handleKeyHold(self, app, keys):
        if 'space' in keys and self.phase != 'gameOver':
            self.handleKey(app, 'space')
