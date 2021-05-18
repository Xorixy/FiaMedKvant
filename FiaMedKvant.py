# -*- coding: utf-8 -*-
"""
Created on Thu May 13 22:10:24 2021

@author: soric
"""



import numpy as np

rnd = np.random


#         Red           Green         Yellow        Blue          Magenta       Cyan
colors = ['\u001b[31m', '\u001b[32m', '\u001b[33m', '\u001b[34m', '\u001b[35m', '\u001b[36m']
colorReset = '\u001b[0m'

def color(colorIndex, text):
    return colors[colorIndex] + str(text) + colorReset

def primesfrom2to(n):
    """ Input n>=6, Returns a array of primes, 2 <= p < n """
    sieve = np.ones(n//3 + (n%6==2), dtype=np.bool)
    for i in range(1,int(n**0.5)//3+1):
        if sieve[i]:
            k=3*i+1|1
            sieve[       k*k//3     ::2*k] = False
            sieve[k*(k-2*(i&1)+4)//3::2*k] = False
    return np.r_[2,3,((3*np.nonzero(sieve)[0][1:]+1)|1)]

def primes(n):
    """ Returns a array of primes, 2 <= p < n. If n <= 2, returns None """
    if n <= 2:
        return None
    elif n == 3:
        return np.array([2])
    elif n <= 5:
        return np.array([2,3])
    elif n == 6:
        return np.array([2,3,5])
    else:
        return primesfrom2to(n)

def findPrimeFactors(n):
    """Returns an array with all the prime factors of a positive number n"""
    if n < 1:
        raise Exception('Error. Number must be a positive integer to find its prime factors')
    elif n == 1:
        return None
    elif n == 2:
        return [2]
    elif n == 3:
        return [3]
    else:
        
        #If n itself is not a prime, it must be divisible by at least one prime <= sqrt(n)
        potentialPrimes = primes(int(np.sqrt(n))+1)
        primeFactors = []
        
        #Find all prime factors of n <= sqrt(n)
        for prime in potentialPrimes:
            if n%prime == 0:
                primeFactors.append(prime)
                
                #In order to simplify later calculations, we remove all powers of a found prime
                while(n%prime == 0):
                    n = n//prime
        #We have only found the prime factors of n that are <= sqrt(n)
        #There might be ONE factor (without powers) other greater than sqrt(n)
        #However, since we divided out all other prime factors from our n, thus either
        #n = 1, or n = prime that divided the first n
        #Thus in this case, if n != 1 we add it to the list
        if n != 1:
            primeFactors.append(n)
        return primeFactors
        
        
        

class FiaGame:
    def __init__(self, numPlay=None, piecesPerPlayer=None, boardLength=None, maxRoll=None, dataType = 'int'):
        """
        Initialises a new game instance of Fia med kvant.
        The playing variables can either be left as default or be specfied by the user,
        with checks that only proper values are used (i.e the pieces per player must be greater than one and so on)
        """
        
        if numPlay == None:
            numPlay = self.numPlay = 2
        if type(numPlay) != int or numPlay < 2:
            raise Exception('Error, number of players must either be left as default or be an integer greater than one')
        else:
            self.numPlay = numPlay


        if piecesPerPlayer == None:
            self.numPiece = 2*numPlay
            piecesPerPlayer = 2
        if type(piecesPerPlayer) != int or piecesPerPlayer < 1:
            raise Exception('Error, pieces per player must either be left as default or be an integer greater than zero')
        else:
            self.numPiece = piecesPerPlayer*self.numPlay
            self.piecesPerPlayer = piecesPerPlayer


        if boardLength == None:
            boardLength = self.boardLength = 10
        if type(boardLength) != int or boardLength < 1:
            raise Exception('Error, board length must either be left as default or be an integer greater than zero')
        else:
            self.boardLength = boardLength


        if maxRoll == None:
            maxRoll = self.maxRoll = 6
        if type(maxRoll) != int or maxRoll < 1:
            raise Exception('Error, maximum roll must either be left as default or be an integer greater than zero')
        else:
            self.maxRoll = maxRoll

        #self.dataType = dataType
        self.dataType = 'int'
        initialBoard = [0]*self.numPiece
        self.gameState = {tuple(initialBoard):1}
        self.totalWeight = 1



    def getParameters(self):
        """
        Returns the game parameters:
        Number of players, number of pieces, boardlength and maximum roll
        """
        return self.numPlay, self.numPiece, self.boardLength, self.maxRoll, self.dataType


    def roll(self):
        """
        Rolls a maxRoll-sided die and returns it
        """
        value = rnd.randint(1, self.maxRoll+1)
        return value


    def getProbabilities(self):
        if self.dataType == 'int':
            probabilities = np.zeros([self.numPiece, self.boardLength+1])
            for boardState in self.gameState:
                for i in range(self.numPiece):
                    probabilities[i][boardState[i]] = probabilities[i][boardState[i]] + self.gameState[boardState]/self.totalWeight
            return probabilities
                    

    def quantumMove(self, pieceId, maxMove):
        if self.dataType == 'int':
            #Dict with the new boards
            newGameState = {}
            
            #Every old board state creates maxMove new board states with the same weight
            #Thus, the total weight is simply multiplied by maxMove
            self.totalWeight = self.totalWeight*maxMove
            #We need to perform all possible steps for all possible gamestates
            for oldBoard in self.gameState:
                for step in range(1, maxMove+1):
                    
                    #For each old board and each possible step, we calculate the resulting new board
                    newBoard = self.normalMove(oldBoard, pieceId, step)
                    
                    #If the resulting boardstate is not part of the new states, we simply add
                    #it with the same weight as the old state:
                    if newBoard not in newGameState:
                        newGameState[newBoard] = self.gameState[oldBoard]
                    
                    #Otherwise, we add the weight of the old board to the resulting board in the new states
                    else:
                        newGameState[newBoard] = newGameState[newBoard] + self.gameState[oldBoard]
            
            
            #After all new states are calculated, we set them to be the current game state,
            #then we shorten the weights
            self.gameState = newGameState
            self.shortenWeights()
            return 0
        
        
        
        
        
    def observeTile(self, position):
        if self.dataType == 'int':
            #First, we have to choose a state based on it's weight and get the pieces on its position
            chosenState = None
            #We generate a number between 1-totalWeight
            if self.totalWeight > 1:
                ProbNumber = rnd.randint(1,self.totalWeight)
            else:
                ProbNumber = 1
            for boardState in self.gameState:
                #If this number is greater than the current weight, we make the number smaller by weight
                if ProbNumber > self.gameState[boardState]:
                    ProbNumber = ProbNumber - self.gameState[boardState]
                #Else, this is the randomly chosen state!
                else:
                    chosenState = boardState
                    break;
            
            #Some error handling in case the total weights are whack
            if chosenState == None:
                raise Exception('Error: Total weights should be the sum of all weights, something is wrong')
            
            #We now extract the observed pieces
            observedPieces = []
            for i in range(len(chosenState)):
                if chosenState[i] == position:
                    observedPieces.append(i)
            
            #Now we have to remove all states that do not match this observation
            self.makeObservation(observedPieces, position)
            return observedPieces
        
        
        
        
        
    def shortenWeights(self):
        """For integer data types, it might be wise to divide all the weights by their largest common
            denominator to shorten them"""
        if self.dataType == 'int':
            
            #First, find the smallest of all weights
            smallestWeight = np.inf
            for boardState in self.gameState:
                if self.gameState[boardState] < smallestWeight:
                    smallestWeight = self.gameState[boardState]
            
            
            #Now we find all the prime numbers that divide this smallest weight
            #If the smallest weight is one, then obviously the weights are minimal
            if smallestWeight != 1:
                dividingPrimes = findPrimeFactors(smallestWeight)
            else:
                dividingPrimes = []
            for boardState in self.gameState:
                
                #If there are no primes that divide all previous looked at weights,
                #the weights are already minimal, no point in conitnuing
                if dividingPrimes == []:
                    break
                
                #Else we check after bad primes, i.e primes that divide the smallest weight but not
                #this one (and thus per definition can't divide every weight)
                badPrimes = []
                for prime in dividingPrimes:
                    if self.gameState[boardState]%prime != 0:
                        badPrimes.append(prime)
                        
                #We then remove the bad primes from possible divisors
                for badPrime in badPrimes:
                    dividingPrimes.remove(badPrime)
                    
            #If no primes divide the weights, they are already minimal.
            #Else we divide them by the common primes, and run the algorithm again
            #since we might have powers of primes that divide
            if dividingPrimes != []:
                commonFactor = 1
                for prime in dividingPrimes:
                    commonFactor = commonFactor*prime
                for boardState in self.gameState:
                    self.gameState[boardState] = self.gameState[boardState]//commonFactor
                self.totalWeight = self.totalWeight//commonFactor
                self.shortenWeights()
            
    def normalMove(self, boardTuple, pieceId, step):
        """"Takes a single board and performs a normal fia move"""
        #We want to be able to edit the board state
        board = list(boardTuple)
        
        #In order to win, one must roll exactly the right roll
        if board[pieceId] + step <= self.boardLength:
            board[pieceId] = board[pieceId] + step
            
            #Now, if the piece is not at the end, we check if it has squashed another piece:
            #Remember, with n pieces per player, player number i has the pieces
            #i, i+1, i+2, ..., i+n-1
            #Thus, the piece with id K belongs to the player with id
            #(K - K%n)/n
            if board[pieceId] != self.boardLength:
                movingPlayerId = (pieceId - pieceId%self.piecesPerPlayer)//self.piecesPerPlayer
                for i in range(len(board)):
                    standingPlayerId = (i - i%self.piecesPerPlayer)//self.piecesPerPlayer
                    if (board[i] == board[pieceId]) and (movingPlayerId != standingPlayerId):
                        board[i] = 0
        return tuple(board)

    def makeObservation(self, pieceIds, position):
        """Removes any states that do not have the given pieces on the given position"""
        removedStates = []
        
        #First, find the boardStates that don't match the observation and subtract their weights from the weight total
        for boardState in self.gameState:
            for i in range(len(boardState)):
                if (i in pieceIds and boardState[i] != position) or (i not in pieceIds and boardState[i] == position):
                    removedStates.append(boardState)
                    self.totalWeight = self.totalWeight - self.gameState[boardState]
        
        
        #Now, remove them 

        for i in range(len(removedStates)):
            del self.gameState[removedStates[i]]
        
        #Lastly, shorten the weights
        self.shortenWeights()
            
        

        

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
            print(f'If you want to see the possible positions of a all pieces, type "{color(currentPlayer, "p")}".')
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
            print(f'If you want to see the possible positions of a all pieces, type "{color(currentPlayer, "p")}".')
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
                observedPieces = Game.observeTile(tile)
                if observedPieces != -1:
                    for i in range(len(observedPieces)):
                        observedPieces[i] = color(observedPieces[i] // numPlay, observedPieces[i])
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
            print(Game.getProbabilities())
            """
            if command == 'p':
                piecesId = range(Game.numPiece)
            else:
                try:
                    piecesId = [int(command[1:])]
                except:
                    piecesId = None
            if piecesId is not None:
                print(' '*(len(str(Game.numPiece))+2) + (' '*5).join([str(i) for i in range(boardlen+1)]))
                for piece in piecesId:
                    probs = Game.getProbabilities(piece)
                    print(color(piece // Game.piecesPerPlayer, f'{piece}:'.ljust(len(str(Game.numPiece))+2) + '  '.join(probs)))
            else:
                print('\nInvalid piece')
            """
        if command == 'states':
            print(Game.gameState)


if __name__ == "__main__":
    Play()














