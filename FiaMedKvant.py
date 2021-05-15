# -*- coding: utf-8 -*-
"""
Created on Thu May 13 22:10:24 2021

@author: soric
"""


import numpy.random as rnd

#         Red           Green         Yellow        Blue          Magenta       Cyan
colors = ['\u001b[31m', '\u001b[32m', '\u001b[33m', '\u001b[34m', '\u001b[35m', '\u001b[36m']
colorReset = '\u001b[0m'
def color(colorIndex, text):
    return colors[colorIndex] + str(text) + colorReset


class Node:
    def __init__(self, Connection=None):
        self.links = []
        self.NodeType = None
        if Connection != None:
            self.addLink(Connection)

    def addLink(self, Connection):
        """Adds either a single connection to the node, or a list of connections.
        The connections need to all be same as the NodeType, unless the Node is empty.
        """
        ConType = type(Connection)
        if ConType == list:
            ConType = type(Connection[0])
            for element in Connection:
                if ConType != type(element):
                    raise Exception('Error: Appended connections must all be of same type')

            if self.NodeType == None:
                if (ConType == Branch) or (ConType == Node):
                    self.links.extend(Connection)
                    self.NodeType = ConType
                else:
                    raise Exception('Error: Nodes can only connect to branches or other nodes')

            elif (ConType == self.NodeType):
                self.links.extend(Connection)

            else:
                raise Exception(f'Error: This list is of type {self.NodeType} not of {ConType}')

        elif self.NodeType == None:
            if (ConType == Branch) or (ConType == Node):
                self.links.append(Connection)
                self.NodeType = ConType
            else:
                raise Exception('Error: Nodes can only connect to branches or other nodes')

        elif (ConType == self.NodeType):
            self.links.append(Connection)

        else:
            raise Exception('Error: This list is of type {self.NodeType} not of {ConType}')

    def getLinks(self):
        """
        Returns a list of the links of the node
        """
        return self.links

    def getType(self):
        """
        Returns the node type
        """
        return self.NodeType

    def removeLink(self, link):
        """
        Removes a link from the node
        """
        try:
            self.links.remove(link)
        except:
            raise Exception('Error: Not a link of this node')

    def reset(self):
        """
        Resets all links and sets NodeType to none
        """
        self.links = []
        self.NodeType = None

    def length(self):
        """
        Returns the number of connections this node has, be it branches or other nodes
        """
        return len(self.links)

    def totalSize(self, visitedNodes = None):
        """
        Returns the total number of all nodes and branches under this one recursively, including itself.
        """
        if visitedNodes == None:
            visitedNodes = [self]
        else:
            visitedNodes.append(self)
        if self.NodeType == None:
            return 1
        elif self.NodeType == Branch:
            return len(self.links) + 1
        elif self.NodeType == Node:
            length = 0
            for link in self.links:
                if not link in visitedNodes:
                    length = length + link.totalSize(visitedNodes)
            return length + 1

    def observation(self, pieceId, position):
        """
        Given a list of observed pieces on a position, it passes this information to the nodes
        or branches under it.
        If any of its linked nodes/branches return false, (i.e they are not linked to any
        valid board state) it flags itself for removal and returns false.
        """
        removals = []
        for i in range(len(self.links)):
            if not self.links[i].observation(pieceId, position):
                removals.append(self.links[i])
        for i in range(len(removals)):
            self.removeLink(removals[i])
        if len(self.links) == 0:
            return False
        else:
            return True

    def quantumMove(self, pieceId, maxMove):
        """
        Given a pieceId and the maximum steps it took, it sends this information
        down to its linked nodes/branches.
        Any daughter branches are then replaced by nodes linking to the new branches
        coresponding to the new states.
        """
        if self.NodeType == Node:
            for element in self.links:
                element.quantumMove(pieceId, maxMove)
        elif self.NodeType == Branch:
            newNodes = [0]*len(self.links)
            for i in range(len(self.links)):
                newNodes[i] = self.links[i].quantumMove(pieceId, maxMove)
            self.reset()
            self.addLink(newNodes)

    def getStates(self):
        """
        Returns all linked states under this node and their weights.
        Also multiplies all weights by the number of links the node has.
        """
        bStates = []
        weights = []
        for element in self.links:
            elementStates, elementWeights = element.getStates()
            bStates.extend(elementStates)
            weights.extend(elementWeights)
        for i in range(len(weights)):
            weights[i] = weights[i]*len(self.links)
        return bStates, weights


class Branch:
    def __init__(self, board=None):
        if board != None:
            self.setBoard(board)

    def setBoard(self, board):
        self.board = board

    def getBoard(self):
        return self.board

    def quantumMove(self, pieceId, maxMove):
        newBranches = [0]*maxMove
        for i in range(maxMove):
            newBoard = self.board.getCopy()
            #print(newBoard.getState())
            newBoard.movePiece(pieceId, i+1)
            newBranches[i] = Branch(newBoard)
        return Node(newBranches)

    def observation(self, pieceId, position):
        return self.board.observation(pieceId, position)

    def getStates(self):
        return [self.board.getState()], [1]

class BoardState:
    def __init__(self, boardLength=None, numOfPieces=None, numOfTeams=None, state = None):
        if boardLength == None:
            boardLength = 10
        if numOfPieces == None:
           numOfPieces = 2
        if numOfTeams == None:
            numOfTeams = 2

        self.boardLength = boardLength
        self.pieceCount = numOfPieces
        self.playerCount = numOfTeams

        if self.pieceCount % self.playerCount != 0:
            raise Exception('Error: Number of players must divide number of pieces!')

        self.bState = [0]*self.pieceCount
        if state != None:
            self.bState = state


    def getCopy(self):
        return BoardState(self.boardLength, self.pieceCount, self.playerCount, self.bState[:])

    def getState(self):
        return self.bState

    def setState(self, board):
        self.bState = board

    def movePiece(self, pieceId, step):
        team = (pieceId - pieceId%(self.pieceCount//self.playerCount))//(self.pieceCount//self.playerCount)
        if self.bState[pieceId] <= self.boardLength - step:
            self.bState[pieceId] = self.bState[pieceId] + step
            if self.bState[pieceId] != self.boardLength:
                for i in range(self.pieceCount):
                    if (i - i%(self.pieceCount//self.playerCount))//(self.pieceCount//self.playerCount) != team:
                        if self.bState[i] == self.bState[pieceId]:
                            self.bState[i] = 0

        #pieceId is a number 0, 1, ...
        #Each player has n = pieceCount/playerCount pcs
        #pieces 0, 1, ... , n - 1 belong to player 1,
        #pieces n,  n + 1, ... , 2n - 1 to player 2 and so on
        #If a piece lands on a space occupied by a piece from another player,
        #the other piece gets knocked off the board and goes back to start

    def observation(self, pieceId, position):
        piecesOnPosition = []
        for i in range(len(self.bState)):
            if self.bState[i] == position:
                piecesOnPosition.append(i)
        if sorted(piecesOnPosition) == sorted(pieceId):
            return True
        else:
            return False


class FiaGame:
    def __init__(self, numPlay=None, piecesPerPlayer=None, boardLength=None, maxRoll=None):
        """
        Initialises a new game instance of Fia med kvant.
        The playing variables can either be left as default or be specfied by the user,
        with checks that only proper values are used (i.e the pieces per player must be greater than one and so on)
        """
        if numPlay == None:
            self.numPlay = 2
        if type(numPlay) != int or numPlay < 2:
            raise Exception('Error, number of players must either be left as default or be an integer greater than one')
        else:
            self.numPlay = numPlay


        if piecesPerPlayer == None:
            self.numPiece = 2*numPlay
        if type(piecesPerPlayer) != int or piecesPerPlayer < 1:
            raise Exception('Error, pieces per player must either be left as default or be an integer greater than zero')
        else:
            self.numPiece = piecesPerPlayer*self.numPlay
            self.piecesPerPlayer = piecesPerPlayer


        if boardLength == None:
            self.boardLength = 10
        if type(boardLength) != int or boardLength < 1:
            raise Exception('Error, board length must either be left as default or be an integer greater than zero')
        else:
            self.boardLength = boardLength


        if maxRoll == None:
            self.maxRoll = 6
        if type(maxRoll) != int or maxRoll < 1:
            raise Exception('Error, maximum roll must either be left as default or be an integer greater than zero')
        else:
            self.maxRoll = maxRoll



        self.GameState = Node(Branch(BoardState(self.boardLength, self.numPiece, self.numPlay)))



    def getParameters(self):
        """
        Returns the game parameters:
        Number of players, number of pieces, boardlength and maximum roll
        """
        return self.numPlay, self.numPiece, self.boardLength, self.maxRoll


    def roll(self):
        """
        Rolls a maxRoll-sided die and returns it
        """
        value = rnd.randint(1, self.maxRoll+1)
        return value


    def getProbabilities(self, pieceId):
        """
        Returns the probabilities of the position of the piece with a given ID
        If given an invalid ID, returns -1
        """
        if type(pieceId) == int and (0 <= pieceId < self.numPiece):
            probs = [0]*(self.boardLength+1)
            States, weights = self.GameState.getStates()
            for i in range(len(States)):
                probs[States[i][pieceId]] = probs[States[i][pieceId]] + 1/weights[i]
            return probs
        else:
            return -1


    def quantumMove(self, pieceId, maxMove):
        """
        Performs a quantum move of a piece up to the number of steps specified
        If the move was performed, returns 0
        If an invalid piece is given, returns -1
        If an invalid number of steps is given, returns -2
        If both are invalid, returns -3
        """
        returnVal = -3
        validID = False
        validMaxMove = False
        if type(pieceId) == int and 0 <= pieceId < self.numPiece:
            validID = True
            returnVal = returnVal + 1
        if type(maxMove) == int and maxMove > 0:
            validMaxMove = True
            returnVal = returnVal + 2

        if validID and validMaxMove:
            self.GameState.quantumMove(pieceId, maxMove)
        return returnVal

    def observe(self, position):
        """
        Observes a certain position, returns an array with all pieces on the position
        If the given position is invalid, returns -1
        """
        if type(position) == int and 0 <= position <= self.boardLength:
            RandRoll = rnd.random()
            SProb = 0
            States, weights = self.GameState.getStates()
            for i in range(len(States)):
                if SProb <= RandRoll <= SProb + 1/weights[i]:
                    observedState = States[i]
                    break
                else:
                    SProb = SProb + 1/weights[i]
            observedPieces = []
            for i in range(len(observedState)):
                if observedState[i] == position:
                    observedPieces.append(i)
            self.GameState.observation(observedPieces, position)
            if self.GameState.getType() == Node and self.GameState.length() == 1:
                newState = self.GameState.getLinks()[0]
                del self.GameState
                self.GameState = newState
            return observedPieces
        else:
            return -1

    def getStates(self):
        return self.GameState.getStates()

def Play():
    print('Hello! How many players?')
    numPlay = input()
    if numPlay == '':
        numPlay = 2
        numPiece = 2*numPlay
        boardlen = 10
        maxRoll = 6
    else:
        numPlay = int(numPlay)
        print('How many pieces per player?')
        numPiece = int(input())*numPlay
        print('How long is the board?')
        boardlen = int(input())
        print('How much is the maximum die roll?')
        maxRoll = int(input())

    Game = FiaGame(numPlay, numPiece//numPlay, boardlen, maxRoll)
    currentPlayer = 0
    phase = 0
    while(True):
        if phase == 0:
            print("\n" + color(currentPlayer, f"It is now player {currentPlayer + 1}'s turn"))
            pieces = []
            for i in range(numPiece//numPlay):
                pieces.append(i + currentPlayer*numPiece//numPlay)
            print(f'Your pieces are {", ".join([color(currentPlayer, piece) for piece in pieces])}')
            print(f'It is your turn to roll. In order to roll a die press {color(currentPlayer, "r")}.')
            print(f'If you want to see the possible positions of a piece n, type "{color(currentPlayer, "pn")}".')
            command = input()
            if len(command) == 0:
                command = '0'
            if command == 'r':
                roll = Game.roll()
                phase = 1
        elif phase == 1:
            print(f'You rolled a {color(currentPlayer, roll)}\n')
            print(f'Which piece would you like to move? Your pieces are {", ".join([color(currentPlayer, piece) for piece in pieces])}')
            print(f'If you want to see the possible positions of a piece n, type "{color(currentPlayer, "pn")}".')
            command = input()
            if len(command) == 0:
                command = 'None'
            try:
                pieceId = int(command)
            except:
                pieceId = -1
            if not (currentPlayer*numPiece//numPlay) <= pieceId < (currentPlayer + 1)*numPiece//numPlay:
                pieceId = -1
            returnCode = Game.quantumMove(pieceId, roll)
            if returnCode == 0:
                phase = 2
                print(f'\nMoved piece {color(currentPlayer, pieceId)} up to {roll} spaces.')
            elif returnCode == -1:
                print('\nInvalid piece')
            else:
                print('Something weird is happening, invalid steps. Should not be able to happen, debug your code you idiot!')
        if phase == 2:
            print(f'You may now observe a tile, the board has spaces from 0 to {boardlen}')
            print(f'To observe a tile n, type "{color(currentPlayer, "on")}"')
            command = input()
            if len(command) == 0:
                command = '0'
            if command[0] == 'o':
                try:
                    tile = int(command[1:])
                except:
                    tile = None
                observedPieces = Game.observe(tile)
                if observedPieces != -1:
                    print(f'The following piece(s) are on tile {tile}: {", ".join(observedPieces)}')
                    phase = 3
                else:
                    print('\nInvalid position')
        elif phase == 3:
            currentPlayer = currentPlayer + 1
            phase = 0
            if currentPlayer == numPlay:
                currentPlayer = 0
        if command == 'q':
            break
        if command[0] == 'p':
            try:
                pieceId = int(command[1:])
            except:
                pieceId = None
            probs = Game.getProbabilities(pieceId)
            if probs == -1:
                print('\nInvalid piece')
            else:
                print(probs)
        if command == 'states':
            S, w = Game.getStates()
            print(S)
            print(w)


if __name__ == "__main__":
    Play()














