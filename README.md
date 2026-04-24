============================================================
CARD GAME SUITE — CMU 15-112 Final Project
Riyan Bilimoria Kadribegovic
============================================================
This string generated with the help of Claude.

A retro pixel-art card game suite featuring two fully-playable games
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
See video "112 final project.mp4" for more playing details.
Linked here: https://youtu.be/9dlZ-a0rPwg