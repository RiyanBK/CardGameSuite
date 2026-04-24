from cmu_graphics import *
from theme import drawBlackjackTable, drawPixelText
from button import Button
from card import *

class Blackjack:
    def __init__(self, app):
        self.deck = Deck(numDecks=6)
        self.dealerHand = Hand()
        self.gamePhase = 'playerSelect'  # playerSelect, betting, playing, dealerTurn, result
        self.resultMessage = ''

        # players and turn tracking — populated when player count is chosen
        self.players = []
        self.numPlayers = 0
        self.activePlayerIndex = 0  # whose turn it is to bet or play

        cx = app.width / 2

        # player count selection buttons
        self.playerSelectButtons = [
            Button('1 PLAYER',  cx, app.height * 0.5,  160, 48, rgb(180, 50, 50),  rgb(220, 80, 80)),
            Button('2 PLAYERS', cx, app.height * 0.62, 160, 48, rgb(50, 50, 180),  rgb(80, 80, 220)),
            Button('3 PLAYERS', cx, app.height * 0.74, 160, 48, rgb(50, 150, 80),  rgb(80, 180, 110)),
        ]

        # gameplay action buttons — spread to 4-wide row to leave room for split
        # order: HIT, STAND, DOUBLE, MENU (SPLIT is separate, conditionally shown)
        self.buttons = [
            Button('HIT',    cx - 195, app.height * 0.92, 110, 44, rgb(180, 50, 50),  rgb(220, 80, 80)),
            Button('STAND',  cx - 65,  app.height * 0.92, 110, 44, rgb(50, 50, 180),  rgb(80, 80, 220)),
            Button('DOUBLE', cx + 65,  app.height * 0.92, 110, 44, rgb(180, 140, 30), rgb(220, 180, 60)),
            Button('MENU',   100,      app.height * 0.05, 80,  36, rgb(100, 100, 100), rgb(140, 140, 140)),
        ]
        # split button rendered only when the active player's hand qualifies
        self.splitButton = Button('SPLIT', cx + 195, app.height * 0.92, 110, 44,
                                  rgb(100, 50, 180), rgb(140, 80, 220))

        # result screen buttons
        self.nextRoundButton = Button('NEXT ROUND', cx - 100, app.height * 0.9,
                                      160, 48, rgb(50, 150, 80), rgb(80, 180, 110))
        self.resultMenuButton = Button('MENU', cx + 100, app.height * 0.9,
                                       160, 48, rgb(100, 100, 100), rgb(140, 140, 140))

        # betting phase buttons (chip amounts + deal + clear)
        self.betButtons = [
            Button('$10',   cx - 130, app.height * 0.76, 80,  40, rgb(180, 50, 50),  rgb(220, 80, 80)),
            Button('$25',   cx,       app.height * 0.76, 80,  40, rgb(50, 50, 180),  rgb(80, 80, 220)),
            Button('$50',   cx + 130, app.height * 0.76, 80,  40, rgb(50, 150, 80),  rgb(80, 180, 110)),
            Button('DEAL',  cx - 70,  app.height * 0.85, 120, 44, rgb(180, 140, 30), rgb(220, 180, 60)),
            Button('CLEAR', cx + 70,  app.height * 0.85, 120, 44, rgb(120, 40, 40),  rgb(160, 60, 60)),
        ]

    def render(self, app):
        drawBlackjackTable(app)
        cx = app.width / 2

        # shared table chrome — always visible except on player select screen
        if self.gamePhase != 'playerSelect':
            drawPixelText('DEALER', cx, app.height * 0.08, rgb(180, 140, 60), scale=1.2)
            drawRect(cx - app.width * 0.25, app.height * 0.13, app.width * 0.5, 2, fill=rgb(180, 140, 60))
            # dealer hand value — show once all cards are face up
            dealerCards = self.dealerHand.getCards()
            if dealerCards and all(c.faceUp for c in dealerCards):
                dealerVal = self.getHandValue(self.dealerHand)
                valColor = rgb(255, 80, 80) if dealerVal > 21 else rgb(255, 230, 150)
                drawPixelText(str(dealerVal), cx, app.height * 0.11, valColor, scale=0.9)
            drawPixelText('BLACKJACK PAYS 3 TO 2', cx, app.height * 0.38,
                          rgb(180, 50, 50), scale=0.8)
            drawPixelText('Dealer stands on 17', cx, app.height * 0.42,
                          rgb(150, 150, 130), scale=0.7)
            drawRect(cx - app.width * 0.25, app.height * 0.46, app.width * 0.5, 2, fill=rgb(180, 140, 60))

        # route to the correct phase renderer
        if self.gamePhase == 'playerSelect':
            self.renderPlayerSelect(app)
        elif self.gamePhase == 'betting':
            self.renderBetting(app)
        elif self.gamePhase == 'playing':
            self.renderPlaying(app)
        elif self.gamePhase == 'result':
            self.renderResult(app)
        elif self.gamePhase == 'gameOver':
            self.renderGameOver(app)

    def renderPlayerSelect(self, app):
        cx = app.width / 2
        drawPixelText('BLACKJACK', cx, app.height * 0.3, rgb(255, 230, 150), scale=2)
        drawPixelText('SELECT NUMBER OF PLAYERS', cx, app.height * 0.41,
                      rgb(180, 140, 60), scale=0.8)
        for button in self.playerSelectButtons:
            button.render()

    def getBetAmounts(self, player):
        if player.chips >= 50:
            return [10, 25, 50]
        elif player.chips >= 10:
            return [10, 25, player.chips]
        else:
            return [1, 5, player.chips]

    def renderBetting(self, app):
        cx = app.width / 2
        player = self.players[self.activePlayerIndex]
        drawPixelText(f'{player.name} — PLACE YOUR BET', cx, app.height * 0.52,
                      rgb(255, 230, 150), scale=1.2)
        drawPixelText(f'CHIPS: ${player.chips}', cx, app.height * 0.59,
                      rgb(180, 140, 60), scale=0.9)
        if player.bets[0] > 0:
            drawPixelText(f'Current bet: ${player.bets[0]}', cx, app.height * 0.65,
                          rgb(200, 200, 180), scale=0.9)
        # update chip button labels dynamically based on available chips
        amounts = self.getBetAmounts(player)
        for i, button in enumerate(self.betButtons[:3]):
            button.label = f'${amounts[i]}'
            button.render()
        # DEAL and CLEAR only appear once a bet has been placed
        if player.bets[0] > 0:
            self.betButtons[3].render()  # DEAL
            self.betButtons[4].render()  # CLEAR

    def getSeatPositions(self, app):
        cx = app.width / 2
        if self.numPlayers == 1:
            return [cx]
        elif self.numPlayers == 2:
            return [cx - app.width * 0.22, cx + app.width * 0.22]
        else:
            return [cx - app.width * 0.3, cx, cx + app.width * 0.3]

    def renderPlaying(self, app):
        self.renderDealerCards(app)
        seatPositions = self.getSeatPositions(app)
        for i, player in enumerate(self.players):
            self.renderPlayerSeat(app, player, seatPositions[i], i == self.activePlayerIndex)
        # action buttons always visible during play
        for button in self.buttons:
            button.render()
        # split only appears when the active player's current hand qualifies
        if self.players[self.activePlayerIndex].canSplit():
            self.splitButton.render()

    def renderPlayerSeat(self, app, player, seatX, isActive):
        cardY = app.height * 0.62
        step = 60       # pixels between card left edges
        handGap = 20    # gap between split hands

        # compute total width needed to fit all hands side by side
        if player.sittingOut:
            totalW = 100
        else:
            totalW = sum(max(1, len(h.getCards())) * step for h in player.hands)
            totalW += handGap * (len(player.hands) - 1)
        seatW = max(totalW + 20, 120)

        borderColor = rgb(255, 215, 50) if isActive else rgb(100, 100, 80)
        drawRect(seatX - seatW / 2, cardY - 32, seatW, 145, fill=None,
                 border=borderColor, borderWidth=2, opacity=70 if isActive else 25)

        nameColor = rgb(255, 230, 150) if isActive else rgb(160, 140, 90)
        drawPixelText(player.name, seatX, cardY - 22, nameColor, scale=0.8)
        drawPixelText(f'${player.chips}', seatX, cardY - 10, rgb(140, 200, 140), scale=0.7)

        if player.sittingOut:
            drawPixelText('OUT OF CHIPS', seatX, cardY + 40, rgb(180, 80, 80), scale=0.75)
            return

        # lay out each hand left to right with no overlap
        handWidths = [max(1, len(h.getCards())) * step for h in player.hands]
        totalHandsW = sum(handWidths) + handGap * (len(player.hands) - 1)
        curX = seatX - totalHandsW / 2  # left edge of first hand

        for handIdx, hand in enumerate(player.hands):
            cards = hand.getCards()
            handW = handWidths[handIdx]
            handCenterX = curX + handW / 2
            for i, card in enumerate(cards):
                card.render(curX + i * step, cardY)
            val = self.getHandValue(hand)
            valColor = rgb(255, 80, 80) if val > 21 else rgb(255, 230, 150)
            drawPixelText(str(val), handCenterX, cardY + 97, valColor, scale=0.8)
            drawPixelText(f'Bet: ${player.bets[handIdx]}', handCenterX, cardY + 110,
                          rgb(200, 200, 180), scale=0.7)
            curX += handW + handGap

    def renderGameOver(self, app):
        cx = app.width / 2
        # render blank poker table not with blackjack text
        drawPixelText('GAME OVER', cx, app.height * 0.38, rgb(220, 80, 80), scale=2)
        drawPixelText('ALL PLAYERS OUT OF CHIPS', cx, app.height * 0.5,
                      rgb(180, 140, 60), scale=0.9)
        self.resultMenuButton.render()

    def renderResult(self, app):
        self.renderDealerCards(app)
        seatPositions = self.getSeatPositions(app)
        for i, player in enumerate(self.players):
            self.renderPlayerSeat(app, player, seatPositions[i], False)
            # result label for each hand, stacked below the seat
            for handIdx, result in enumerate(player.results):
                seatW = app.width * 0.18
                handX = seatPositions[i] + handIdx * (seatW * 0.5)
                labelColor = {
                    'WIN':        rgb(100, 220, 100),
                    'BLACKJACK!': rgb(255, 215, 50),
                    'PUSH':       rgb(200, 200, 180),
                    'LOSE':       rgb(220, 80, 80),
                    'BUST':       rgb(220, 80, 80),
                }.get(result, rgb(255, 230, 150))
                drawPixelText(result, handX, app.height * 0.83, labelColor, scale=0.9)
        self.nextRoundButton.render()
        self.resultMenuButton.render()

    def renderDealerCards(self, app):
        cards = self.dealerHand.getCards()
        step = 68
        startX = app.width / 2 - (len(cards) * step) / 2
        for i, card in enumerate(cards):
            card.render(startX + i * step, 80)

    def getHandValue(self, hand):
        value = 0
        aces = 0
        for card in hand.getCards():
            if card.name in ['Jack', 'Queen', 'King']:
                value += 10
            elif card.name == 'Ace':
                value += 11
                aces += 1
            else:
                value += int(card.name)
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        return value

    def handleClick(self, app, mouseX, mouseY):
        allButtons = (self.playerSelectButtons + self.buttons + [self.splitButton]
                      + self.betButtons + [self.nextRoundButton, self.resultMenuButton])
        for button in allButtons:
            if button.isClicked(mouseX, mouseY):
                button.pressed = True

    def _releaseAllButtons(self):
        allButtons = (self.playerSelectButtons + self.buttons + [self.splitButton]
                      + self.betButtons + [self.nextRoundButton, self.resultMenuButton])
        for button in allButtons:
            button.pressed = False

    def handleRelease(self, app, mouseX, mouseY):
        self._releaseAllButtons()
        if self.gamePhase == 'playerSelect':
            for i, button in enumerate(self.playerSelectButtons):
                if button.isClicked(mouseX, mouseY):
                    self.numPlayers = i + 1
                    self.players = [BlackjackPlayer(f'Player {j + 1}')
                                    for j in range(self.numPlayers)]
                    self.activePlayerIndex = 0
                    self.gamePhase = 'betting'

        elif self.gamePhase == 'betting':
            player = self.players[self.activePlayerIndex]
            amounts = self.getBetAmounts(player)
            for i, button in enumerate(self.betButtons[:3]):
                if button.isClicked(mouseX, mouseY) and player.chips >= amounts[i]:
                    player.placeBet(amounts[i])
            # CLEAR — refund the whole bet back to chips
            if player.bets[0] > 0 and self.betButtons[4].isClicked(mouseX, mouseY):
                player.chips += player.bets[0]
                player.bets[0] = 0
            # DEAL — confirm bet and advance
            if player.bets[0] > 0 and self.betButtons[3].isClicked(mouseX, mouseY):
                nextIdx = self.nextActivePlayerIndex(self.activePlayerIndex)
                if nextIdx != -1:
                    self.activePlayerIndex = nextIdx
                else:
                    self.dealCards()
                    self.activePlayerIndex = next(j for j, p in enumerate(self.players)
                                                  if not p.sittingOut)
                    self.skipInitialBlackjacks()
                    self.gamePhase = 'playing'

        elif self.gamePhase == 'playing':
            player = self.players[self.activePlayerIndex]
            hit, stand, double, menu = self.buttons

            if menu.isClicked(mouseX, mouseY):
                self.resetGame()
                app.screenMode = 'menu'
                return

            if hit.isClicked(mouseX, mouseY):
                card = self.deck.draw()
                card.faceUp = True
                player.currentHand().addCard(card)
                # bust — hand is done, move on automatically
                if self.getHandValue(player.currentHand()) > 21:
                    self.advanceTurn()

            elif stand.isClicked(mouseX, mouseY):
                self.advanceTurn()

            elif double.isClicked(mouseX, mouseY):
                # double only legal on the opening 2-card hand with enough chips
                hand = player.currentHand()
                bet = player.currentBet()
                if hand.getCount() == 2 and player.chips >= bet:
                    player.chips -= bet
                    player.bets[player.activeHandIndex] += bet
                    card = self.deck.draw()
                    card.faceUp = True
                    hand.addCard(card)
                    self.advanceTurn()  # exactly one card then forced stand

            elif self.splitButton.isClicked(mouseX, mouseY) and player.canSplit():
                player.split()
                # deal one face-up card to each hand so both are playable
                for hand in player.hands:
                    if hand.getCount() == 1:
                        card = self.deck.draw()
                        card.faceUp = True
                        hand.addCard(card)
                # stay on hand 0 (activeHandIndex is still 0 after split)

        elif self.gamePhase == 'result':
            if self.nextRoundButton.isClicked(mouseX, mouseY):
                self.startNextRound()
            elif self.resultMenuButton.isClicked(mouseX, mouseY):
                self.resetGame()
                app.screenMode = 'menu'

        elif self.gamePhase == 'gameOver':
            if self.resultMenuButton.isClicked(mouseX, mouseY):
                self.resetGame()
                app.screenMode = 'menu'

    def skipInitialBlackjacks(self):
        # after the deal, auto-advance past any player who has a natural blackjack
        while self.activePlayerIndex < self.numPlayers:
            player = self.players[self.activePlayerIndex]
            if player.sittingOut:
                break
            hand = player.currentHand()
            if hand.getCount() == 2 and self.getHandValue(hand) == 21:
                nextIdx = self.nextActivePlayerIndex(self.activePlayerIndex)
                if nextIdx != -1:
                    self.activePlayerIndex = nextIdx
                else:
                    self.runDealerTurn()
                    return
            else:
                break

    def nextActivePlayerIndex(self, fromIdx):
        # returns index of next non-sitting-out player after fromIdx, or -1 if none
        for i in range(fromIdx + 1, self.numPlayers):
            if not self.players[i].sittingOut:
                return i
        return -1

    def advanceTurn(self):
        player = self.players[self.activePlayerIndex]
        # if this player has another split hand to play, move to it
        if player.activeHandIndex < len(player.hands) - 1:
            player.activeHandIndex += 1
        else:
            nextIdx = self.nextActivePlayerIndex(self.activePlayerIndex)
            if nextIdx != -1:
                self.activePlayerIndex = nextIdx
            else:
                self.runDealerTurn()

    def runDealerTurn(self):
        # flip the hidden card
        for card in self.dealerHand.getCards():
            card.faceUp = True
        # dealer hits until reaching 17 or higher
        while self.getHandValue(self.dealerHand) < 17:
            card = self.deck.draw()
            card.faceUp = True
            self.dealerHand.addCard(card)
        self.calculateResults()
        self.gamePhase = 'result'

    def calculateResults(self):
        dealerVal = self.getHandValue(self.dealerHand)
        dealerBlackjack = (self.dealerHand.getCount() == 2 and dealerVal == 21)
        for player in self.players:
            player.results = []
            if player.sittingOut:
                continue
            for handIdx, hand in enumerate(player.hands):
                val = self.getHandValue(hand)
                bet = player.bets[handIdx]
                playerBlackjack = (hand.getCount() == 2 and val == 21)
                if val > 21:
                    # bust — chips already gone when bet was placed
                    player.results.append('BUST')
                elif playerBlackjack and dealerBlackjack:
                    player.chips += bet          # push — return bet
                    player.results.append('PUSH')
                elif playerBlackjack:
                    player.chips += int(bet * 2.5)   # 3:2 payout
                    player.results.append('BLACKJACK!')
                elif dealerVal > 21 or val > dealerVal:
                    player.chips += bet * 2      # return bet + equal winnings
                    player.results.append('WIN')
                elif val == dealerVal:
                    player.chips += bet          # push — return bet
                    player.results.append('PUSH')
                else:
                    player.results.append('LOSE')

    def startNextRound(self):
        # keep players and their chip counts; reset hands, bets, and turn order
        self.dealerHand = Hand()
        for player in self.players:
            player.hands = [Hand()]
            player.bets = [0]
            player.results = []
            player.activeHandIndex = 0
            player.sittingOut = (player.chips == 0)
        if self.deck.getCardsLeft() < 52:
            self.deck.reset()
        # if every player is broke, end the game
        if all(player.sittingOut for player in self.players):
            self.gamePhase = 'gameOver'
            return
        # start betting from the first player who still has chips
        self.activePlayerIndex = next(i for i, p in enumerate(self.players)
                                      if not p.sittingOut)
        self.gamePhase = 'betting'

    def resetGame(self):
        # full reset — return to player select with a clean slate
        self.dealerHand = Hand()
        self.players = []
        self.numPlayers = 0
        self.activePlayerIndex = 0
        self.resultMessage = ''
        if self.deck.getCardsLeft() < 52:
            self.deck.reset()
        self.gamePhase = 'playerSelect'

    def dealCards(self):
        # deal two face-up cards to each active player, then dealer gets one up one down
        for player in self.players:
            if player.sittingOut:
                continue
            card1 = self.deck.draw()
            card2 = self.deck.draw()
            card1.faceUp = True
            card2.faceUp = True
            player.hands[0].addCard(card1)
            player.hands[0].addCard(card2)
        dealerUp = self.deck.draw()
        dealerDown = self.deck.draw()
        dealerUp.faceUp = True
        dealerDown.faceUp = False   # hidden until dealer's turn
        self.dealerHand.addCard(dealerUp)
        self.dealerHand.addCard(dealerDown)

class BlackjackPlayer:
    def __init__(self, name, chips=500):
        self.name = name
        self.chips = chips
        self.hands = [Hand()]       # start with one empty hand; split adds more
        self.bets = [0]             # one bet per hand, parallel to self.hands
        self.results = []           # result strings per hand, filled after dealer turn
        self.activeHandIndex = 0    # which hand is currently being played
        self.sittingOut = False     # True when player has no chips to bet this round

    def placeBet(self, amount):
        # each chip button click stacks onto the existing bet
        self.chips -= amount
        self.bets[self.activeHandIndex] += amount

    def canSplit(self):
        # split is only legal on the opening two cards of the same value
        hand = self.currentHand()
        cards = hand.getCards()
        return (len(cards) == 2 and cards[0].name == cards[1].name
                and self.chips >= self.currentBet())

    def split(self):
        # pull the second card out and give it its own hand with a matching bet
        hand = self.currentHand()
        splitCard = hand.removeTopCard()
        newHand = Hand()
        newHand.addCard(splitCard)
        self.hands.append(newHand)
        bet = self.currentBet()
        self.chips -= bet
        self.bets.append(bet)

    def currentHand(self):
        return self.hands[self.activeHandIndex]

    def currentBet(self):
        return self.bets[self.activeHandIndex]