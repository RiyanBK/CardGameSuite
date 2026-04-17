from cmu_graphics import *

# button functionality for easier button making
class Button:
    def __init__(self, label, x, y, width, height):
        self.label = label
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def isClicked(self, mouseX, mouseY):
        return ((self.x - self.width / 2 < mouseX < self.x + self.width / 2) and 
                (self.y - self.height / 2 < self.mouseY < self.y + self.height / 2))
    
    def render(self, app):
        pass
    