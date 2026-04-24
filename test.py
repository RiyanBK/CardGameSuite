from cmu_graphics import *
from blackjack import Blackjack, BlackjackPlayer
from card import Card, Hand

# Most of this file has been written by Claude

# Visual stress test: P1 and P2 both split, then pile up 2s and 3s.
# Lets us see how the dynamic card-step layout handles crowded hands.

def makeHand(cardDefs):
    h = Hand()
    for name, suit in cardDefs:
        c = Card(name, suit)
        c.faceUp = True
        h.addCard(c)
    return h

def onAppStart(app):
    app.width = 800
    app.height = 600
    bj = Blackjack(app)

    bj.numPlayers = 3
    bj.players = [BlackjackPlayer(f'Player {i + 1}') for i in range(3)]

    # Player 1: split 8s, then hits 2s and 3s on each hand
    # hand A: 8 2 3 2 3 2  → 20
    # hand B: 8 3 2 3 2    → 18
    p1 = bj.players[0]
    p1.hands = [
        makeHand([('8','Spades'),  ('2','Clubs'),   ('3','Diamonds'),
                  ('2','Spades'),  ('3','Clubs'),   ('2','Hearts')]),
        makeHand([('8','Hearts'),  ('3','Spades'),  ('2','Diamonds'),
                  ('3','Hearts'),  ('2','Clubs')]),
    ]
    p1.bets = [50, 50]
    p1.activeHandIndex = 0

    # Player 2: split 7s, then hits even more 2s and 3s
    # hand A: 7 2 3 2 3 2 2 → 21
    # hand B: 7 3 2 3 2 3   → 20
    p2 = bj.players[1]
    p2.hands = [
        makeHand([('7','Clubs'),   ('2','Spades'),  ('3','Hearts'),
                  ('2','Diamonds'),('3','Clubs'),   ('2','Spades'), ('2','Hearts')]),
        makeHand([('7','Diamonds'),('3','Spades'),  ('2','Clubs'),
                  ('3','Hearts'), ('2','Diamonds'), ('3','Clubs')]),
    ]
    p2.bets = [50, 50]
    p2.activeHandIndex = 0

    # Player 3: normal blackjack hand for comparison
    p3 = bj.players[2]
    p3.hands = [makeHand([('Ace','Hearts'), ('King','Spades')])]
    p3.bets = [50]
    p3.activeHandIndex = 0

    # Dealer: two face-up cards
    for name, suit in [('7','Spades'), ('10','Hearts')]:
        c = Card(name, suit)
        c.faceUp = True
        bj.dealerHand.addCard(c)

    bj.activePlayerIndex = 0
    bj.gamePhase = 'playing'

    app.bj = bj

def redrawAll(app):
    app.bj.render(app)

runApp(width=800, height=600)
