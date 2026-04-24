# Card Game Suite

**CMU 15-112 Final Project**
*Riyan Bilimoria Kadribegovic*

> *This README was styled with the help of Claude.*

A 8-bit style card game suite featuring two fully-playable games sharing a common table/UI framework: **War** (2-player) and **Blackjack** (1–3 players vs. dealer).

**[Watch the demo video](https://youtu.be/9dlZ-a0rPwg)**

---

## Key Features

### War
Phase-based state machine with full WAR sequence on ties, correct **double tie** handling (cards returned to owners), and hold-RIGHT to speed-play.

### Blackjack
1–3 players, 6-deck shoe, real betting (chip stacking + CLEAR), HIT / STAND / DOUBLE / SPLIT with parallel bet tracking, dealer stands on 17, 3:2 blackjack payout, sit-out at $0, and a game-over screen when all players are out of chips.

### Shared Framework
Rules screen, custom `Button` class with press animation, cohesive felt-table theme, and a reusable `Card` / `Deck` / `Hand` / `PresetDeck` layer.

---

## Grading Shortcuts

### Main Menu

| Key | Action |
|-----|--------|
| `R` | Open Rules screen |

### War Screen

| Control | Action |
|---------|--------|
| `DEV` button | 4-round scripted hand walking through every phase (see below) |
| `NORMAL` button | Exit dev mode, return to shuffled deck |
| `SPACE` | Flip / Next (mirrors on-screen button) |
| Hold `→` | Speed-play through rounds |

**War dev mode walkthrough:**
- **Round 1:** Normal win
- **Round 2:** Normal loss
- **Round 3:** Tie → war → player wins
- **Round 4:** Tie → war → **DOUBLE TIE** (cards returned to owners)

### Blackjack Screen

| Control | Action |
|---------|--------|
| `DEV` button | 3-player scripted demo with yellow highlight on the next button to press |

**Blackjack dev mode walkthrough:**
- **Hand 1:** HIT-to-bust, STAND, dealer 19
- **Hand 2:** Blackjack skip, SPLIT 8s (one win, one loss)
- **Hand 3:** Dealer blackjack PUSH, LOSE, HIT-to-bust

### All Games

| Control | Action |
|---------|--------|
| `MENU` button | Return to main menu (top-left, always visible) |

---