
#!/usr/bin/env python
#################################################################################
# 
# Evolutionary Blackjack
# Semester Project for CSCE A405 AI
# Austin Edwards, Tuva Granoien, and Logan Chamberlain
# Fall 2022
#
#
################################################################################

import poplib
import Player
import Dealer
from Evolution import Evolve
import time
import concurrent.futures
import multiprocessing.pool
import multiprocessing as mp
from multiprocessing import Queue
import random
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import dataframe_image as dfi
import sys
from PIL import Image, ImageFont, ImageDraw
import os
import time
import pickle


#Fills in the global deck variable with 52 strings of the form "value of suit"
def populate_deck():
    SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]
    ROYALTY_AND_ACE = ["Ace", "King", "Queen", "Jack"]
    for i in range(2,11):
        for SUIT in SUITS: 
            DECK.append(str(i) + " of " + SUIT)
    for FACE in ROYALTY_AND_ACE:
        for SUIT in SUITS:
            DECK.append(FACE + " of " + SUIT)


#Returns rank of random card (blackjack doesnt care about suits) from the populated deck
def get_random_card():
    if(len(DECK) > 52):
        #print("Error: populate deck prior to drawing card")
        return None
    card = DECK[random.randint(0, len(DECK)-1)]
    card = card.split(" of ")
    return card[0]


#Returns an array of the player's cards and the dealers visible card and not visible card in the form [[Player Card 1, Player Card 2], [Dealer Visible Card, Dealer not Visible Card]]. Example: [[]"7 of hearts", "King of Spades"], []"Jack of Diamonds", "3 of Clubs"]]
def deal(player, dealer):
    player_card_1 = get_random_card()
    player_card_2 = get_random_card()
    # checks if you can split i.e., cards are equal in rank
    if player_card_1 == player_card_2:
        player.can_split = True
    # store these rank values into hand in format [ace, other]
    get_card_value(player, player_card_1)
    get_card_value(player, player_card_2)

    dealer_card_1 = get_random_card()
    # store "hole card", this is the face up card our agent can see
    if dealer_card_1 == 'Ace':
        dealer.hole_card = 'Ace'
    elif dealer_card_1 == 'Jack' or dealer_card_1 == 'Queen' or dealer_card_1 == 'King':
        dealer.hole_card = 10
    else:
        dealer.hole_card = int(dealer_card_1)
    # store hole card in hand
    get_card_value(dealer, dealer.hole_card)
    # store hidden card in hand
    get_card_value(dealer, get_random_card())
    return 


#Takes a card in the form "Value of Suit" and returns an integer of the value unless Ace. Example: "7 of Hearts" -> 7, "King of Spades" -> 10, "Ace of Clubs" -> "Ace"
def get_card_value(player, value):
    if value == 'Ace':
        # player can only have 1 Ace without busting     i.e., hand [Ace, Ace] == [Ace, 1]
        # player can only have an Ace if total is < 11   i.e., hand [8, 8, Ace] == [8, 8, 1]
        if player.hand[0] != 11 and player.total < 11:
            player.hand[0] = 11
            player.total += 11
        else:
            player.hand[1] += 1
            player.total += 1
    elif value == 'King' or value == 'Queen' or value == 'Jack':
        player.hand[1] += 10
        player.total += 10
    else:
        value = int(value)
        player.hand[1] += value
        player.total += value
    if player.total > 21 and player.hand[0] == 11:
        player.total -= 10
        player.hand[0] = 0
        player.hand[1] += 1
    return


#Checks for the condition wherein a player is drawn an Ace and a 10 card (10 or any face card), resulting in an immediate Blackjack. Different conditions exist for player and dealers having a natural, returns None if not applicable, return a string describing who won is applicable. 
def check_naturals(player, dealer):
    if player.total == 21 and dealer.total != 21:
        # the player normally earns 3/2 odds -> on a $2 bet, +$3 is earned instead of the normal +$2
        player.POOL += (1.5 * player.BET_AMOUNT)
        player.hands_won += 1
        return "Player Blackjack: Player Win"
    if player.total != 21 and dealer.total == 21:
        # the player looses normally
        player.POOL -= player.BET_AMOUNT
        player.hands_lost += 1
        return "Dealer BlackJack: Player Lose"
    if player.total == 21 and dealer.total == 21:
        # the bet is a "push", no money exchanged
        player.hands_tied += 1
        return "Player and Dealer Blackjack: Push"
    else:
        return None


#ACTION: Finished drawing, check player hand against dealer's. Returns a bool of if game was won or not
def stand(player):
    player.done_with_hand = True


#ACTION: player asks for a new card to be added to their hand
def hit(player):
    card = get_random_card()
    get_card_value(player, card)



#ACTION: Double Down. Player hits one more time and bets a doubled amount. After hitting one more, procedure is the same as stand (see above)
def double_down(player):
    if not player.first_action:
        #print("Error: can only double down with 2 cards")
        # if the AIs table says double and you have 3 cards, Hit instead
        hit(player)
        return None
    player.BET_AMOUNT = 2 * player.BET_AMOUNT
    #print("Doubling Down with bet: $" + str(player.BET_AMOUNT))
    hit(player)
    player.done_with_hand = True


#ACTION: Checks if there is a pair and player has not split.  Stores pair value so it can evaluate the hands individually
def split(player, dealer):
    # Set can split to false since we cannot split twice
    player.can_split = False
    # if we have a pair of aces, set our hand to [11, 0], split card = 11, and we are done with hand after a single hit
    if player.hand[0] == 11:
        player.hand[1] = 0
        player.split_card = 11
        player.hand[0] = 11
        player.done_with_hand = True
    # if we have any other pair, set our hand to [0, value], split card = value
    else:
        player.split_card = int(player.total/2)
        player.hand[1] = player.split_card
    # reset player total to the split card 
    player.total = player.split_card
    # mandatory hit, not technically mandatory in blackjack rules but no rational player will stand after splitting
    hit(player)
    # play hand #1
    play_hand(player, dealer)    
    # Create second hand similar to first hand
    player.done_with_hand = False
    if player.split_card == 11:
        player.hand[0] = 11
        player.hand[1] = 0
        player.done_with_hand = True
    else:
        player.hand[0] = 0
        player.hand[1] = player.split_card
    player.total = player.split_card
    hit(player)
    # play hand #2
    # plays second hand when it exits into play_hand() function


 #Checks action the AI will take until "done with hand"
def play_hand(player, dealer):
    # this is only in play if the player splits and hits to 21. This condition is not caught by naturals
    if player.total == 21:
        player.done_with_hand = True

    while not player.done_with_hand:
        # choose action from randomized table
        # Hit, stand, double down, or split based on soft-hand, hard-hand, or pair

        #print("Player Hand: {}".format(player.hand) + " Total: " + str(check_player_hand(player.hand)))

        action = ''

        # Pair condition:   
        if player.can_split:
            if player.hand[0] == 11:
                action = player.STRATEGY_TABLE_PAIR["A-A"][dealer.hole_card]
                #player.COUNT_TABLE_PAIR["A-A"][dealer.hole_card] += 1
                #print("PAIR: A-A\n")

            else:
                value = str(int(player.total/2))
                action = player.STRATEGY_TABLE_PAIR[value + "-" + value][dealer.hole_card]
                #player.COUNT_TABLE_PAIR[value + "-" + value][dealer.hole_card] += 1
                #print("PAIR: " + value + "-" + value + "\n")

        # Soft Hand condition:
        elif player.hand[0] == 11:
            if player.hand[1] == 1:
                action = player.STRATEGY_TABLE_SOFT_HAND["A-A"][dealer.hole_card]
                #player.COUNT_TABLE_SOFT_HAND["A-A"][dealer.hole_card] += 1
                #print("SOFT HAND: A-A\n")

            else:
                action = player.STRATEGY_TABLE_SOFT_HAND["A-" + str(player.hand[1])][dealer.hole_card]
                #player.COUNT_TABLE_SOFT_HAND["A-" + str(player.hand[1])][dealer.hole_card] += 1
                #print("SOFT HAND: A-" + str(player.hand[1]) + "\n")
        # Hard hand condtion:
        else:
            action = player.STRATEGY_TABLE_HARD_HAND[player.hand[1]][dealer.hole_card]
            #player.COUNT_TABLE_HARD_HAND[player.hand[1]][dealer.hole_card] += 1
            #print("HARD HAND: " + str(player.hand[1]) + "\n")
           
        #action = input("Enter your action (H,S,D,P): ")

        if action == 'H':
            hit(player)
        elif action == 'S':
            stand(player)
        elif action == 'D':
            double_down(player)
        elif action == 'P':
            player.first_action = False
            split(player, dealer)
        player.first_action = False

        # if our total is > 21 -> bust
        if player.total > 20:
            player.done_with_hand = True
    
    evaluate_hands(player, dealer)
    return


# As per the game rules, the dealer hits automatically if the total is under 17 and stands automatically if over 17 but under 21. Bust if 21 or over
def get_dealer_hand(dealer):
    # this is assuming the dealer is playing by Soft-17 rules (dealer must stand on a soft 17 e.g., [Ace, 6], [2, 4, Ace])
    # Solf-17 gives the dealer a slight advantage
        while dealer.total < 17:
            card = get_random_card()
            get_card_value(dealer, card)
        return


 #Evaluates Hands after play is complete, prints winner, and returns True or False for a Win
def evaluate_hands(player, dealer):
    get_dealer_hand(dealer)
    if(player.total > 21):
        #print("Dealer Hand: {}  Total: {}\nPlayer Hand: {}  Total: {}".format(player.dealer_hand, player.dealer_total, player.hand, player.total))
        #print("Player Lose, Bust")
        player.POOL -= player.BET_AMOUNT
        player.hands_lost += 1
        return False
    elif(dealer.total > 21):
        #print("Dealer Hand: {}  Total: {}\nPlayer Hand: {}  Total: {}".format(player.dealer_hand, player.dealer_total, player.hand, player.total))
        #print("Player wins, dealer bust")
        player.POOL += player.BET_AMOUNT
        player.hands_won += 1
        return True
    elif(player.total > dealer.total):
        #print("Dealer Hand: {}  Total: {}\nPlayer Hand: {}  Total: {}".format(player.dealer_hand, player.dealer_total, player.hand, player.total))
        #print("Player Wins")
        player.POOL += player.BET_AMOUNT
        player.hands_won += 1
        return True
    elif(player.total == dealer.total):
        #print("Dealer Hand: {}  Total: {}\nPlayer Hand: {}  Total: {}".format(player.dealer_hand, player.dealer_total, player.hand, player.total))
        #print("Push")
        player.hands_tied += 1
        return True
    else:
        #print("Dealer Hand: {}  Total: {}\nPlayer Hand: {}  Total: {}".format(player.dealer_hand, player.dealer_total, player.hand, player.total))
        #print("Player Lose")
        player.POOL -= player.BET_AMOUNT
        player.hands_lost += 1
        return False


    #Plays a game with a player until 1000 hands or player pool is 0
def play_game(player):
    dealer = Dealer.dealer()
    while player.hands_played < player.LIMIT:
        if player.hands_played % 10_000 == 0:
            print(str(player.hands_played))
        deal(player, dealer)
        #print("Dealer Hand: {}".format(player.dealer_hand[0]))
        result = None
        result = check_naturals(player, dealer)
        if not result:
            play_hand(player, dealer)
        #else:
            #print(result + " had naturals")
            #print("Balance: " + str(player.POOL))
        reset(player, dealer)
        player.hands_played += 1
    return 


 #Resets values of player and dealer in between hands
def reset(player, dealer):
    player.done_with_hand = False
    player.BET_AMOUNT = 2
    player.hand = [0, 0]
    player.total = 0
    player.dealer_hand = []
    player.dealer_total = 0
    player.can_split = False
    player.split_card = None
    player.first_action = True

    dealer.hand = [0, 0]
    dealer.hole_card
    dealer.total = 0

DECK = []

def TestingAgent(player):    
    player.POOL = 10_000_000
    player.LIMIT = 10_0_000
    player.hands_played = 0
    player.hands_won = 0
    player.hands_tied = 0
    player.hands_lost = 0
    populate_deck()
    play_game(player)
    print("$ Lost Per hand (Optimal = -$0.0144): " + str((player.POOL - 10_000_000) / 10_000_000))
    print("Hands Won: "  + str(player.hands_won) + "  Hands Lost: "  + str(player.hands_lost) + "  Hands Tied: "   + str(player.hands_tied))


        