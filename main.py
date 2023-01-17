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
from TestingAgent import TestingAgent
import Evolution
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


#NOTE: The dealer has an infinite deck for the purposes of our algorithm

#Proven strategy tables data sourced from: https://towardsdatascience.com/winning-blackjack-using-machine-learning-681d924f197c
#MOVES ARE INDEX by TABLE[PLAYER SUM][DEALER CARD]
PROVEN_STRATEGY_TABLE_HARD_HAND = {20:{2:"S", 3:"S", 4:"S", 5:"S", 6:"S", 7:"S", 8:"S", 9:"S", 10:"S", "Ace":"S"}, 
                              19:{2:"S", 3:"S", 4:"S", 5:"S", 6:"S", 7:"S", 8:"S", 9:"S", 10:"S", "Ace":"S"},
                              18:{2:"S", 3:"S", 4:"S", 5:"S", 6:"S", 7:"S", 8:"S", 9:"S", 10:"S", "Ace":"S"},
                              17:{2:"S", 3:"S", 4:"S", 5:"S", 6:"S", 7:"S", 8:"S", 9:"S", 10:"S", "Ace":"S"},
                              16:{2:"S", 3:"S", 4:"S", 5:"S", 6:"S", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"},
                              15:{2:"S", 3:"S", 4:"S", 5:"S", 6:"S", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"},
                              14:{2:"S", 3:"S", 4:"S", 5:"S", 6:"S", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"},
                              13:{2:"S", 3:"S", 4:"S", 5:"S", 6:"S", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"},
                              12:{2:"H", 3:"H", 4:"S", 5:"S", 6:"S", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"},
                              11:{2:"D", 3:"D", 4:"D", 5:"D", 6:"D", 7:"D", 8:"D", 9:"D", 10:"D", "Ace":"D"},
                              10:{2:"D", 3:"D", 4:"D", 5:"D", 6:"D", 7:"D", 8:"D", 9:"D", 10:"H", "Ace":"H"},
                              9:{2:"H", 3:"D", 4:"D", 5:"D", 6:"D", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"}, 
                              8:{2:"H", 3:"H", 4:"H", 5:"H", 6:"H", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"},
                              7:{2:"H", 3:"H", 4:"H", 5:"H", 6:"H", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"},
                              6:{2:"H", 3:"H", 4:"H", 5:"H", 6:"H", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"},
                              5:{2:"H", 3:"H", 4:"H", 5:"H", 6:"H", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"},
                              4:{2:"H", 3:"H", 4:"H", 5:"H", 6:"H", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"}}
                             
PROVEN_STRATEGY_TABLE_SOFT_HAND = {"A-9":{2:"S", 3:"S", 4:"S", 5:"S", 6:"S", 7:"S", 8:"S", 9:"S", 10:"S", "Ace":"S"}, 
                                   "A-8":{2:"S", 3:"S", 4:"S", 5:"S", 6:"D", 7:"S", 8:"S", 9:"S", 10:"S", "Ace":"S"},
                                   "A-7":{2:"D", 3:"D", 4:"D", 5:"D", 6:"D", 7:"S", 8:"S", 9:"H", 10:"H", "Ace":"H"},
                                   "A-6":{2:"H", 3:"D", 4:"D", 5:"D", 6:"D", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"},
                                   "A-5":{2:"H", 3:"H", 4:"D", 5:"D", 6:"D", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"},
                                   "A-4":{2:"H", 3:"H", 4:"D", 5:"D", 6:"D", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"},
                                   "A-3":{2:"H", 3:"H", 4:"H", 5:"D", 6:"D", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"},
                                   "A-2":{2:"H", 3:"H", 4:"H", 5:"D", 6:"D", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"}}

PROVEN_STRATEGY_TABLE_PAIR = {"A-A":{2:"P", 3:"P", 4:"P", 5:"P", 6:"P", 7:"P", 8:"P", 9:"P", 10:"P", "Ace":"P"}, 
                                   "10-10":{2:"S", 3:"S", 4:"S", 5:"S", 6:"S", 7:"S", 8:"S", 9:"S", 10:"S", "Ace":"S"},
                                   "9-9":{2:"P", 3:"P", 4:"P", 5:"P", 6:"P", 7:"S", 8:"P", 9:"P", 10:"S", "Ace":"S"},
                                   "8-8":{2:"P", 3:"P", 4:"P", 5:"P", 6:"P", 7:"P", 8:"P", 9:"P", 10:"P","Ace":"P"},
                                   "7-7":{2:"P", 3:"P", 4:"P", 5:"P", 6:"P", 7:"P", 8:"H", 9:"H", 10:"H", "Ace":"H"},
                                   "6-6":{2:"P", 3:"P", 4:"P", 5:"P", 6:"P", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"},
                                   "5-5":{2:"D", 3:"D", 4:"D", 5:"D", 6:"D", 7:"D", 8:"D", 9:"D", 10:"H", "Ace":"H"},
                                   "4-4":{2:"H", 3:"H", 4:"H", 5:"P", 6:"P", 7:"H", 8:"H", 9:"H", 10:"H", "Ace":"H"},
                                   "3-3":{2:"P", 3:"P", 4:"P", 5:"P", 6:"P", 7:"P", 8:"H", 9:"H", 10:"H", "Ace":"H"},
                                   "2-2":{2:"P", 3:"P", 4:"P", 5:"P", 6:"P", 7:"P", 8:"H", 9:"H", 10:"H", "Ace":"H"}}
                                   


def _color_table(val):
    color = ''
    if(val == 'S'):
        color = 'red'
    elif(val == 'H'):
        color = 'green'
    elif(val == 'D'):
        color = 'yellow'
    elif(val == 'P'):
        color = 'purple'
    else:
        color = 'white'
    return 'background-color: %s' % color


def visualize_strategy_tables(player, mode):
    if(mode == "TOUR2"):
        path = "./Strategy Table Images/Tournament Selection 2/"
    elif(mode == "TOUR3"):
        path = "./Strategy Table Images/Tournament Selection 3/"
    elif(mode == "TOUR4"):
        path = "./Strategy Table Images/Tournament Selection 4/"
    elif(mode == "T4"):
        path = "./Strategy Table Images/Top 4//"
    elif(mode == "M"):
        path = "./Strategy Table Images/Mutation/"
    elif(mode == "OP"):
        path = "./Strategy Table Images/Optimal Player/"
    if not os.path.exists(path):
        os.makedirs(path)
    player_designation = str(player.player_number) + "_"

    info_text = "Generation: " + str(player.generation) + "\nPlayer: "+ str(player.player_number) +"\nRemaining Funds: $"+ str(player.POOL)
    font = ImageFont.truetype("arial.ttf", size=20)
    info_img = Image.new('RGB', (300, 100), color=(255,255,255))
    imgDraw = ImageDraw.Draw(info_img)
    imgDraw.text((10,10), info_text, font=font, fill=(0,0,0))
    info_img.save(path+player_designation+"info.png")

    df_hard_hand = pd.DataFrame(player.STRATEGY_TABLE_HARD_HAND).T
    df_hard_hand.style.set_table_attributes("style='display:inline'").set_caption('Hard Hand')
    df_styled_hard_hand = df_hard_hand.style.applymap(_color_table)
    dfi.export(df_styled_hard_hand,path+player_designation+"hard_hand.png")
    
    df_soft_hand = pd.DataFrame(player.STRATEGY_TABLE_SOFT_HAND).T
    df_styled_soft_hand = df_soft_hand.style.applymap(_color_table)
    dfi.export(df_styled_soft_hand,path+player_designation+"soft_hand.png")

    df_pair = pd.DataFrame(player.STRATEGY_TABLE_PAIR).T
    df_styled_pair = df_pair.style.applymap(_color_table)
    dfi.export(df_styled_pair,path+player_designation+"pair.png")

    images = [Image.open(x) for x in [path+player_designation+"hard_hand.png", path+player_designation+"soft_hand.png", path+player_designation+"pair.png"]]
    widths, heights = zip(*(i.size for i in images))
    total_width = sum(widths)
    max_height = max(heights)
    all_tables = Image.new('RGB', (total_width, max_height), color = (255, 255, 255))
    info_img = Image.open(path+player_designation+"info.png")
    x_offset = 0
    PASTED_INFO = False
    for im in images:
        all_tables.paste(im, (x_offset,0))
        if(x_offset != 0 and not PASTED_INFO):
            all_tables.paste(info_img, (x_offset + 300, 400))
            PASTED_INFO = True
        x_offset += im.size[0]
    file_name = path + "Generation " + str(player.generation) + ".png"
    all_tables.save(file_name)
    os.remove(path+player_designation+"hard_hand.png")
    os.remove(path+player_designation+"soft_hand.png")
    os.remove(path+player_designation+"pair.png")
    os.remove(path+player_designation+"info.png")


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
def play_game(player,RESULTS):
    populate_deck()
    dealer = Dealer.dealer()
    while player.hands_played < player.LIMIT:
        deal(player, dealer)
        #print("Dealer Hand: {}".format(player.dealer_hand[0]))
        result = check_naturals(player, dealer)
        if not result:
            play_hand(player, dealer)
        #else:
            #print(result + " had naturals")
            #print("Balance: " + str(player.POOL))
        reset(player, dealer)
        player.hands_played += 1
    #Build array of result information to determine victors
    # use this when using processes 
    RESULTS.put(player)
    #RESULTS.append(player)
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



#Returns a random move depending on the mode (hard hard, soft hand, and pair)
def generate_random_move(mode):
    if(mode == "Hard Hand" or mode == "Soft Hand"):
        move = random.choice(["S", "H", "D"]) 
    if(mode == "Pair"):
        move = random.choice(["P", "S", "H", "D"])
    return move


#Creates an array of Player objects with randomly filled strategy tables. Takes in an integer denoting how many players to create
def generate_inital_population(num_players):
    initial_population = []
    for i in range(num_players):
        initial_population.append(Player.player())
        initial_population[i].player_number = i + 1

    for player in initial_population:
        #Fill Hard hand table
        for row in player.STRATEGY_TABLE_HARD_HAND:        
            for elem in player.STRATEGY_TABLE_HARD_HAND[row]:
                player.STRATEGY_TABLE_HARD_HAND[row][elem] = generate_random_move("Hard Hand")
        #Fill in Soft hand table
        for row in player.STRATEGY_TABLE_SOFT_HAND:        
            for elem in player.STRATEGY_TABLE_SOFT_HAND[row]:
                player.STRATEGY_TABLE_SOFT_HAND[row][elem] = generate_random_move("Soft Hand")
        #Fill in pairs tables
        for row in player.STRATEGY_TABLE_PAIR:        
            for elem in player.STRATEGY_TABLE_PAIR[row]:
                player.STRATEGY_TABLE_PAIR[row][elem] = generate_random_move("Pair")

    return initial_population


def save_current_population(pop, mode):
    print("Saving current generation...")
    if(mode == "TOUR2"):
        path = "./Population States/Tournament Selection 2/"
    elif(mode == "TOUR3"):
        path = "./Population States/Tournament Selection 3/"
    elif(mode == "TOUR4"):
        path = "./Population States/Tournament Selection 4/"
    elif(mode == "T4"):
        path = "./Population States/Top 4/"
    elif(mode == "M"):
        path = "./Population States/Mutation/"
    if not os.path.exists(path):
        os.makedirs(path)

    file_pop = open(path+"pop.pickle", "wb")
    pickle.dump(pop, file_pop)

    #loss per hand data
    file_LPH = open(path+"lph.pickle", "wb")
    pickle.dump(pop, file_LPH)


def save_current_lps_data(lps_data, mode):
    print("Saving agent performance measure generation...")
    if(mode == "TOUR2"):
        path = "./Population States/Tournament Selection 2/"
    elif(mode == "TOUR3"):
        path = "./Population States/Tournament Selection 3/"
    elif(mode == "TOUR4"):
        path = "./Population States/Tournament Selection 4/"
    elif(mode == "T4"):
        path = "./Population States/Top 4/"
    elif(mode == "M"):
        path = "./Population States/Mutation/"
    if not os.path.exists(path):
        os.makedirs(path)
    #loss per hand data
    f = open(path+"lph.pickle", "wb")
    pickle.dump(lps_data, f)



def retrieve_population(mode):
    print("Getting saved generation...")
    if(mode == "TOUR2"):
        path = "./Population States/Tournament Selection 2/pop.pickle"
    elif(mode == "TOUR3"):
        path = "./Population States/Tournament Selection 3/pop.pickle"
    elif(mode == "TOUR4"):
        path = "./Population States/Tournament Selection 4/pop.pickle"
    elif(mode == "T4"):
        path = "./Population States/Top 4/pop.pickle"
    elif(mode == "M"):
        path = "./Population States/Mutation/pop.pickle"

    #Return none if no saved population
    if not os.path.exists(path):
        return None
    f = open(path, 'rb') 
    pop = pickle.load(f)
    return pop

def retrieve_lps_data(mode):
    print("Getting saved agent performance measure...")
    if(mode == "TOUR2"):
        path = "./Population States/Tournament Selection 2/lph.pickle"
    elif(mode == "TOUR3"):
        path = "./Population States/Tournament Selection 3/lph.pickle"
    elif(mode == "TOUR4"):
        path = "./Population States/Tournament Selection 4/lph.pickle"
    elif(mode == "T4"):
        path = "./Population States/Top 4/lph.pickle"
    elif(mode == "M"):
        path = "./Population States/Mutation/lph.pickle"

    #Return none if no saved population
    if not os.path.exists(path):
        return None
    f = open(path, 'rb') 
    lps_data = pickle.load(f)
    return lps_data


def create_agent_performance_plot(victor_lost_per_hand, mode):
    if(mode == "TOUR2"):
        path = "./Performance Measure/Tournament Selection 2/"
    elif(mode == "TOUR3"):
        path = "./Performance Measure/Tournament Selection 3/"
    elif(mode == "TOUR4"):
        path = "./Performance Measure/Tournament Selection 4/"
    elif(mode == "T4"):
        path = "./Performance Measure/Top 4/"
    elif(mode == "M"):
        path = "./Performance Measure/Mutation/"
    if not os.path.exists(path):
        os.makedirs(path)

    Gen = np.arange(0, GenerationNum, 1)
    OP_plot = []
    for i in range(len(victor_lost_per_hand)):
        OP_plot.append(-0.0144)

    plt.plot(Gen, victor_lost_per_hand, label = "Agent")
    plt.plot(Gen, OP_plot, label = "Optimal")
    plt.xlabel('Generations')
    plt.ylabel('$ lost per hand')
  
    # naming the title of the plot
    plt.title('Performance Measure: Tournament 3')
    plt.legend(loc='lower right')
    plt.savefig(path+'Performance_Measure3.png')



DECK = []
OPTIMAL_PLAYER = None
VICTOR_RESULTS_LIST = []
POP_SIZE = 400
num_processes = os.cpu_count()
#Processes = [None]*num_processes


if __name__ == "__main__":    


    TOUR2LPS = retrieve_lps_data('TOUR2')
    TOUR3LPS = retrieve_lps_data('TOUR3')
    TOUR4LPS = retrieve_lps_data('TOUR4')

    Gen2 = np.arange(0, len(TOUR2LPS), 1)
    Gen3 = np.arange(0, len(TOUR3LPS), 1)
    Gen4 = np.arange(0, len(TOUR4LPS), 1)

    OP_plot = []
    for i in range(len(TOUR2LPS)):
        OP_plot.append(-0.0144)

    plt.plot(Gen2, TOUR2LPS, label = "Tour 2")
    plt.plot(Gen3, TOUR3LPS, label = "Tour 3")
    plt.plot(Gen4, TOUR4LPS, label = "Tour 4")
    plt.plot(Gen2, OP_plot, label = "Optimal")
    plt.xlabel('Generations')
    plt.ylabel('$ lost per hand')
  
    # naming the title of the plot
    plt.title('Performance Measure: Tournament Comparison')
    plt.legend(loc='lower right')
    plt.savefig('Performance_Measure3.png')



    mode = input("ENTER MODE TOURNAMENT (TOUR2, TOUR3, TOUR4), TOP 4 (T4) or with Mutation (M): ")
    if(mode != "M" and mode != "TOUR2" and mode != "TOUR3" and mode != "TOUR4" and mode != "T4"):
        mode = input("INVALID INPUT: ENTER MODE TOURNAMENT (TOUR2, TOUR3, TOUR4), TOP 4 (T4) or with Mutation (M): ")

    retrieve_saved = input("Retrieve saved population and resume? Enter mode of saved population, enter N to start new: ")
    if(retrieve_saved == "N"):
        print("Starting new...")
        population = generate_inital_population(POP_SIZE)
        GenerationNum = 0
        victor_lost_per_hand = []
    elif(retrieve_saved == "TOUR2"):
        population = retrieve_population("TOUR2")
        victor_lost_per_hand = retrieve_lps_data("TOUR2")
        GenerationNum = population[0].generation
    elif(retrieve_saved == "TOUR3"):
        population = retrieve_population("TOUR3")
        victor_lost_per_hand = retrieve_lps_data("TOUR3")
        GenerationNum = population[0].generation
    elif(retrieve_saved == "TOUR4"):
        population = retrieve_population("TOUR4")
        victor_lost_per_hand = retrieve_lps_data("TOUR4")
        GenerationNum = population[0].generation
    elif(retrieve_saved == "T4"):
        population = retrieve_population("T4")
        GenerationNum = population[0].generation
    elif(retrieve_saved == "M"):
        population = retrieve_population("M")
        GenerationNum = population[0].generation
    OPTIMAL_PLAYER = Player.player()
    OPTIMAL_PLAYER.STRATEGY_TABLE_HARD_HAND = PROVEN_STRATEGY_TABLE_HARD_HAND
    OPTIMAL_PLAYER.STRATEGY_TABLE_SOFT_HAND = PROVEN_STRATEGY_TABLE_SOFT_HAND
    OPTIMAL_PLAYER.STRATEGY_TABLE_PAIR = PROVEN_STRATEGY_TABLE_PAIR
    visualize_strategy_tables(OPTIMAL_PLAYER, "OP")
    
    # Running with Miltiprocessing
    ##################################################################################################
    # the mp.Queue() is how we extract individual process results
    while GenerationNum < 202:
        RESULTS = mp.Queue()
        FinishedGeneration = []
        i = 0
        Start = time.time()
        # loops through population
        processesRunning = False
        while i < len(population):
            Processes = []
            # thread index is population % desired number of threads
            processIndex = i % num_processes
            # play game through each thread and write result into RESULTS
            Processes.append(mp.Process(target=play_game, args=(population[i],RESULTS,)))
            Processes[len(Processes)-1].start()
            processesRunning = True
            # if you reach the max number of threads, wait for all threads to finish
            if processIndex == num_processes-1:
                for j in range(num_processes):
                    #Processes[j].join()
                    FinishedGeneration.append(RESULTS.get(timeout = 20))
                    print("Process: " + str(i))
                    processesRunning = False
            i += 1

        # after looping through population, wait for remaining threads started before htting the (processIndex == num_processes-1) condition
        if processesRunning == True:
            for j in range(processIndex + 1):
                #Processes[j].join()
                FinishedGeneration.append(RESULTS.get(timeout = 20))
                print("Process: " + str(i))
        # print time elapsed to finish generation
        End = time.time()
        print("Time: " + str(End-Start))
        # Sort the finished generation by pool for evoluation
        FinishedGeneration.sort(key=lambda x: x.POOL, reverse=True)
        # print the results
        for results in FinishedGeneration:
            print(results.player_number, results.hands_won, results.hands_lost, results.hands_tied)
        # collect the victor "money lost per hand" stat
        victor_lost_per_hand.append((FinishedGeneration[0].POOL - 1_000_000)/100_000)    
        visualize_strategy_tables(FinishedGeneration[0], mode)

        # UNCOMMENT THIS WHEN DONE TO TEST THE TOP AGENT FROM THE POPULATION
        TestingAgent(FinishedGeneration[0])

        if(mode == 'T4'):
            Victors = FinishedGeneration[0:4]
            population = Evolution.CrossOver(Victors)
        else:
            population = Evolution.Evolve(FinishedGeneration)

        GenerationNum +=1

        for i in range(POP_SIZE):
            population[i].generation = GenerationNum
            population[i].player_number = i + 1
            population[i].hands_played = 0
            population[i].hands_won = 0
            population[i].hands_lost = 0
            population[i].hands_tied = 0
            population[i].POOL = 1_000_000
            population[i].LIMIT = 100_000

        create_agent_performance_plot(victor_lost_per_hand, mode)
        save_current_population(population, mode)
        save_current_lps_data(victor_lost_per_hand, mode)



        # Running without Treads
        ##################################################################################################
    '''
    for i in range(POP_SIZE):
        population[i].generation = 0
        population[i].player_number = i + 1

    RESULTS = []
    i = 0
    Start = time.time()
    populate_deck()
    for players in population:
        play_game(players, RESULTS)
    print(str(population[0].player_number) + " " + str(population[0].hands_played))
    for players in population:
        print(str(10_000_000 - players.POOL))
    End = time.time()
    print(population[0].player_number, population[0].hands_won, population[0].hands_lost, population[0].hands_tied)
    print("Time: " + str(End-Start))
    '''

        