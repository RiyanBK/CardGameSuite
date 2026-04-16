from cmu_graphics import *
import random

class Card:
    # initializes a card with a name, suit, and specification for face up/down
    def __init__(self, name, suit, faceUp=False):
        self.name = name # name is a string of the number or face (ex '2', 'Ace', 'Jack')
        self.suit = suit
        self.faceUp = faceUp

    # string representation of card
    def __repr__(self):
        currString = f"{self.name} of {self.suit}, face "
        if self.faceUp:
            return currString + 'up'
        else:
            return currString + 'down'

    # flips card from face up to down and vice versa
    def flip(self):
        self.faceUp = not self.faceUp

    def render(self, x, y):
        pass
    
class Deck:
    # initializes new deck, with boolean shuffled default to true
    def __init__(self, shuffled=True, numDecks=1):
        self.shuffled = shuffled
        self.numDecks = numDecks
        self.buildDeck()

    # actually initializes the deck
    def buildDeck(self):
        self.cards = []
        for _ in range(self.numDecks):
            for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']:
                for name in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']:
                    self.cards.append(Card(name, suit))
        if self.shuffled:
            self.shuffle()

    # string representing the deck showing how many cards left
    def __repr__(self):
        return f"Deck has {len(self.cards)} cards left"

    # shuffles the deck
    def shuffle(self):
        random.shuffle(self.cards)
        return None

    # draws a card from the top of the deck by returning a Card
    def draw(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            print("Deck is empty!")
            return None

    # puts the number of cards drawn from the top of the deck to a given Hand
    def deal(self, hand, numCards):
        for i in range(numCards):
            card = self.draw()
            if card is not None:
                hand.addCard(card)

    def reset(self):
        self.buildDeck()

    def getCardsLeft(self):
        return len(self.cards)


class Hand:
    # initializes an empty hand
    def __init__(self):
        self.cards = []

    # string representation of hand
    def __repr__(self):
        return f"Hand with cards: {[f'{card.name} of {card.suit}' for card in self.cards]}"

    # adds a given Card to the hand
    def addCard(self, card):
        self.cards.append(card)

    # removes a specific Card from the hand
    def removeCard(self, card):
        self.cards.remove(card)
    
    # returns a list of all the cards in the hand
    def getCards(self):
        return self.cards
    
    # returns the number of cards in the hand
    def getCount(self):
        return len(self.cards)
    
    # renders the card on the screen at a given position
    def render(self, x, y):
        pass