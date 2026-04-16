from cmu_graphics import *
import random

class Card:
    def __init__(self, name, suit):
        self.name = name # name is a string of the number or face (ex '2', 'Ace', 'Jack')
        self.suit = suit

    def __repr__(self):
        return f"{self.name} of {self.suit}"

    def flip(self):
        pass

    def getValue(self):
        return 

    def draw(self, deck):
        pass
    
class Deck:
    def __init__(self):
        self.cards = []
        for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']:
            for name in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']:
                self.cards.append(Card(name, suit))

    def __repr__(self):
        return f"Deck has {len(self.cards)} cards left"

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, numCards):
        pass

    def reset(self):
        pass


class Hand:
    def __init__(self):
        self.cards = []

    def __repr__(self):
        return f"Hand with cards: {[f'{card.name} of {card.suit}' for card in self.cards]}"

    def addCard(self, card):
        self.cards.append(card)

    def removeCard(self, card):
        self.cards.remove(card)
    
    def getCards(self):
        return self.cards
    
    def draw(self, deck):
        if len(deck.cards) > 0:
            card = deck.cards.pop()
            self.addCard(card)