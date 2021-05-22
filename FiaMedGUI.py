from FiaMedKvant import *
import random
import curses
import time

#initialize screen
sc = curses.initscr()
curses.start_color()
curses.curs_set(1)
h, w = sc.getmaxyx()
win = curses.newwin(h, w, 0, 0)

win.keypad(1)

horStep = 6
verStep = 2

horY = 1
verX = 2

curses.init_pair(1, curses.COLOR_RED,     curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_GREEN,   curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_YELLOW,  curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_BLUE,    curses.COLOR_BLACK)
curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
curses.init_pair(6, curses.COLOR_CYAN,    curses.COLOR_BLACK)

def initialPrompt(message):
    win.erase()

    win.addstr(h//2, (w-len(message))//2, message)

    try:
        return int(win.getstr(h//2+2, w//2))
    except ValueError:
        return -1

def gameMessage(message, colorId):
    win.move(h-4, 2)
    win.clrtoeol()
    win.addstr(h-4, 2, message, curses.color_pair(colorId))

def roundNoZero(value):
    if round(value) == 0:
        return ''
    return str(round(value))


def updateProbabilities():
    probabilities = Game.getProbabilities()
    for piece in range(Game.numPiece):
        win.move(verCoords[piece], horCoords[0])
        win.clrtoeol()
        probs = probabilities[piece]
        for probIndex in range(len(probs)-1):
            win.addstr(verCoords[piece], horCoords[probIndex], roundNoZero(100*probs[probIndex]), curses.color_pair(piece // Game.piecesPerPlayer % 6 + 1))

numPlay  = initialPrompt('Hello! How many players?')
if numPlay != -1:
    numPiece = numPlay*initialPrompt('How many pieces per player?')
    boardlen = initialPrompt('How long is the board?')
    maxRoll  = initialPrompt('How much is the maximum die roll?')
else:
    numPlay  = 2
    numPiece = 2*numPlay
    boardlen = 10
    maxRoll  = 6
win.erase()

horCoords = [6 + horStep*i for i in range(boardlen)]
verCoords = [3 + verStep*i for i in range(numPiece)]

if horCoords[-1]+3 >= w:
    curses.endwin()
    print(f'Board length too long! Board length was {boardlen}. Maximum board length for this terminal size is {w // horStep}.')

if verCoords[-1]+1 >= h - 3*(verStep+1):
    curses.endwin()
    print(f'Too many pieces! There were {numPiece} pieces. Maximum amount of pieces for this terminal size is {(h-3*(1+verStep)) // verStep - 1}.')

Game = FiaGame(numPlay, numPiece//numPlay, boardlen, maxRoll)

for i in range(len(horCoords)):
    win.addstr(horY, horCoords[i], str(i))

for i in range(len(verCoords)):
    win.addstr(verCoords[i], verX, str(i))

currentPlayer = 0
cursorPos = 0
phase = -1

win.move(horY, horCoords[0])

key = 0

while key != 27: # While ESC isn't pressed
    win.border(0)
    win.timeout(100)
    key = win.getch()

    if phase == -1:
        updateProbabilities()
        curses.curs_set(0)
        time.sleep(2)
        gameMessage(f"It is now player {currentPlayer + 1}'s turn. Press ENTER to roll. Your pieces are:", currentPlayer % 6 + 1)
        win.move(h-3, 0)
        win.clrtoeol()
        for i in range(Game.piecesPerPlayer):
            win.addstr(h-3, 2+horStep*i, str(Game.piecesPerPlayer*currentPlayer + i), curses.color_pair(currentPlayer % 6 + 1))

        phase = 0
        key = 0

    if phase == 0:
        if key == 10: # Enter
            roll = Game.roll()
            gameMessage(f"You rolled a {roll}. Which piece would you like to move?", currentPlayer % 6 + 1)
            curses.curs_set(1)
            cursorPos = currentPlayer*Game.piecesPerPlayer

            phase = 1
            key = 0

    if phase == 1:
        if key == curses.KEY_UP:
            cursorPos = max(currentPlayer*Game.piecesPerPlayer, cursorPos - 1)
        elif key == curses.KEY_DOWN:
            cursorPos = min((currentPlayer+1)*Game.piecesPerPlayer-1, cursorPos + 1)
        elif key == 10: # Enter
            Game.quantumMove(cursorPos, roll)
            cursorPos = 0
            phase = 2
            key = 0

            updateProbabilities()
            gameMessage('You may now observe a tile. Which tile would you like to observe?', currentPlayer % 6 + 1)

        win.move(verCoords[cursorPos], verX)

    if phase == 2:
        if key == curses.KEY_LEFT:
            cursorPos = max(0, cursorPos - 1)
        elif key == curses.KEY_RIGHT:
            cursorPos = min(boardlen-1, cursorPos + 1)
        elif key == 10: # Enter
            observedPieces = Game.observeTile(cursorPos)
            updateProbabilities()
            gameMessage(f'The following piece(s) are on tile {cursorPos}:', currentPlayer % 6 + 1)
            win.move(h-3, 0)
            win.clrtoeol()
            for i in range(len(observedPieces)):
                win.addstr(h-3, horStep*i+2, str(observedPieces[i]), curses.color_pair(observedPieces[i] // Game.piecesPerPlayer % 6 + 1))
            currentPlayer = (currentPlayer + 1) % numPlay
            phase = -1
            key = 0

        win.move(horY, horCoords[cursorPos])


curses.endwin()