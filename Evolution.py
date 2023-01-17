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


import random
import Player
import math
POP_SIZE = 400
# number of payers chosen for each tournament
tourneyNum = 3
# number of parents to make a child 
numParents = 4
def Evolve(Generation):
    NextGeneration = []
    # do whatever selection we want
    TourneySelection(Generation, NextGeneration)
    return NextGeneration
def TourneySelection(Generation, NextGeneration):
    Selected = []
    # Create groups of players of size tourneyNum until the generation is empty
    while len(Generation) > 0:
        Tourney = []
        # choose, without replacement, random players from the generation 
        i = 0
        while i < tourneyNum:
            randomChoice = random.randint(0, len(Generation)-1)
            Tourney.append(Generation.pop(randomChoice))
            if len(Generation) == 0:
               i = tourneyNum
            i += 1
        # sort the players in the tournament
        Tourney.sort(key=lambda x: x.POOL, reverse=True)
        # append the best to the Selected
        Selected.append(Tourney[0])
    # THIS FILLS THE REST OF THE GENERATION
    # make 2 copies of the selected generation
    SelectedTemp = Selected.copy()
    # while the generation isn't full
    while len(NextGeneration) < POP_SIZE:
        # the remaining victors is less that how many parents/child
        if len(SelectedTemp) < numParents:
            # recopy the victors
            SelectedTemp = Selected.copy()
        parents = []
        # copy random parents into list "parents" without replacement
        for i in range(numParents):
            randomChoice = random.randint(0, len(SelectedTemp)-1)
            parents.append(SelectedTemp.pop(randomChoice))
        
        NextGeneration.append(CrossOverTourney(parents))




#Takes in an array of the 4 victor players of the previous generation. Returns a array of the next generation
def CrossOverTourney(Parents):
    sum = 0
    weights = []

    #Weights are calcuated as the % of the total winnings. Progressively summed to get 4 values that sum to 100, i.e 0 to w1 = Player 1 Pool / sum, w1 to w2 = Player 2 Pool / sum
    for player in Parents:
        sum += player.POOL

    for player in Parents:
        weights.append(player.POOL/sum)
      
    child = Player.player()
    #Fill in Hard hand table
    for row in child.STRATEGY_TABLE_HARD_HAND:        
        for elem in child.STRATEGY_TABLE_HARD_HAND[row]:
            child.STRATEGY_TABLE_HARD_HAND[row][elem] = random.choices([player.STRATEGY_TABLE_HARD_HAND[row][elem] for player in Parents], weights)[0]
    #Fill in Soft hand table
    for row in child.STRATEGY_TABLE_SOFT_HAND:        
        for elem in child.STRATEGY_TABLE_SOFT_HAND[row]:
            child.STRATEGY_TABLE_SOFT_HAND[row][elem] = random.choices([player.STRATEGY_TABLE_SOFT_HAND[row][elem] for player in Parents], weights)[0]
    #Fill in pairs tables
    for row in child.STRATEGY_TABLE_PAIR:        
        for elem in child.STRATEGY_TABLE_PAIR[row]:
            child.STRATEGY_TABLE_PAIR[row][elem] = random.choices([player.STRATEGY_TABLE_PAIR[row][elem] for player in Parents], weights)[0]
    
    return child
                 

#Takes in an array of the 4 victor players of the previous generation. Returns a array of the next generation
def CrossOver(victors):
    sum = 0
    n = 0
    #Weights are calcuated as the % of the total winnings. Progressively summed to get 4 values that sum to 100, i.e 0 to w1 = Player 1 Pool / sum, w1 to w2 = Player 2 Pool / sum
    for player in victors:
        sum += player.POOL
    w1 = (victors[0].POOL / sum) * 100  
    w2 = ((victors[1].POOL / sum) + w1 / 100) * 100
    w3 = ((victors[2].POOL / sum) + w2 / 100) * 100 
      
    players_per_generation = 400
    new_generation = []
    prev_gen_number = victors[0].generation
    new_gen_number = prev_gen_number + 1
    for i in range(players_per_generation):
        new_player = Player.player()
        new_player.player_number = i + 1
        new_player.generation = new_gen_number
        new_generation.append(new_player)

    for player in new_generation:

        for row in player.STRATEGY_TABLE_HARD_HAND:
            for elem in player.STRATEGY_TABLE_HARD_HAND[row]:
                n = random.randint(0, 100)
                if(n < w1):
                    player.STRATEGY_TABLE_HARD_HAND[row][elem] = victors[0].STRATEGY_TABLE_HARD_HAND[row][elem]
                elif(n >= w1 and n < w2):
                    player.STRATEGY_TABLE_HARD_HAND[row][elem] = victors[1].STRATEGY_TABLE_HARD_HAND[row][elem]
                elif(n >= w2 and n < w3):
                    player.STRATEGY_TABLE_HARD_HAND[row][elem] = victors[2].STRATEGY_TABLE_HARD_HAND[row][elem]
                elif(n >= w3):
                    player.STRATEGY_TABLE_HARD_HAND[row][elem] = victors[3].STRATEGY_TABLE_HARD_HAND[row][elem]

        for row in player.STRATEGY_TABLE_SOFT_HAND:
            for elem in player.STRATEGY_TABLE_SOFT_HAND[row]:
                n = random.randint(0, 100)
                if(n < w1):
                    player.STRATEGY_TABLE_SOFT_HAND[row][elem] = victors[0].STRATEGY_TABLE_SOFT_HAND[row][elem]
                elif(n >= w1 and n < w2):
                    player.STRATEGY_TABLE_SOFT_HAND[row][elem] = victors[1].STRATEGY_TABLE_SOFT_HAND[row][elem]
                elif(n >= w2 and n < w3):
                    player.STRATEGY_TABLE_SOFT_HAND[row][elem] = victors[2].STRATEGY_TABLE_SOFT_HAND[row][elem]
                elif(n >= w3):
                    player.STRATEGY_TABLE_SOFT_HAND[row][elem] = victors[3].STRATEGY_TABLE_SOFT_HAND[row][elem]

        for row in player.STRATEGY_TABLE_PAIR:
            for elem in player.STRATEGY_TABLE_PAIR[row]:
                n = random.randint(0, 100)
                if(n < w1):
                    player.STRATEGY_TABLE_PAIR[row][elem] = victors[0].STRATEGY_TABLE_PAIR[row][elem] 
                elif(n >= w1 and n < w2):
                    player.STRATEGY_TABLE_PAIR[row][elem] = victors[1].STRATEGY_TABLE_PAIR[row][elem]
                elif(n >= w2 and n < w3):
                    player.STRATEGY_TABLE_PAIR[row][elem] = victors[2].STRATEGY_TABLE_PAIR[row][elem] 
                elif(n >= w3):
                    player.STRATEGY_TABLE_PAIR[row][elem] = victors[3].STRATEGY_TABLE_PAIR[row][elem]
                 
    return new_generation




def Mutation(child):
    choices = ["H","S","D"]
    pair_choices = ["H","S","D","P"]
    card_value = [2,3,4,5,6,7,8,9,10,"Ace"]
    values_soft_hand = ["A-9","A-8", "A-7", "A-6", "A-5", "A-4", "A-3", "A-2"]
    values_pair = ["A-A", "10-10", "9-9", "8-8", "7-7", "6-6", "5-5", "4-4", "3-3", "2-2"]

    # mutatoion rate in percentage - set to 5%
    percentage_mutation = 5
    hard_hand = math.floor(170*(percentage_mutation/100))
    soft_hand = math.floor(80*(percentage_mutation/100))
    pair_hand = math.floor(100*(percentage_mutation/100))


    # hard hands
    for i in range(hard_hand):
        row = random.randint(4,20)
        elem = random.choice(card_value)
        interchange = random.choice(choices)
        child.STRATEGY_TABLE_HARD_HAND[row][elem] = interchange
    
    # soft hands
    for i in range(soft_hand):
        row = random.choice(values_soft_hand)
        elem = random.choice(card_value)
        interchange = random.choice(choices)
        child.STRATEGY_TABLE_SOFT_HAND[row][elem] = interchange

    # pair hands
    for i in range(pair_hand):
        row = random.choice(values_pair)
        elem = random.choice(card_value)
        interchange = random.choice(pair_choices)
        child.STRATEGY_TABLE_PAIR[row][elem] = interchange
        
    return child


#IGNORE THE BELOW, USED IT TO GENERATE THE CROSS OVER DEMO IMAGES
'''
if __name__ == "__main__":
    victors = []
    for i in range(4):
        p = Player.player()
        p.generation = 1
        p.player_number = i + 1
        victors.append(p)
    print(victors)
    player = victors[0]
    player.POOL = 320
    for row in player.STRATEGY_TABLE_HARD_HAND:
            for elem in player.STRATEGY_TABLE_HARD_HAND[row]:
                player.STRATEGY_TABLE_HARD_HAND[row][elem] = 'P'
    player = victors[1]
    player.POOL = 27
    for row in player.STRATEGY_TABLE_HARD_HAND:
            for elem in player.STRATEGY_TABLE_HARD_HAND[row]:
                player.STRATEGY_TABLE_HARD_HAND[row][elem] = 'D'
    player = victors[2]
    player.POOL = 27
    for row in player.STRATEGY_TABLE_HARD_HAND:
            for elem in player.STRATEGY_TABLE_HARD_HAND[row]:
                player.STRATEGY_TABLE_HARD_HAND[row][elem] = 'H'
    player = victors[3]
    player.POOL = 27
    for row in player.STRATEGY_TABLE_HARD_HAND:
            for elem in player.STRATEGY_TABLE_HARD_HAND[row]:
                player.STRATEGY_TABLE_HARD_HAND[row][elem] = 'S'
    
    for v in victors: 
        main.visualize_strategy_tables(v)
    new_gen = CrossOver(victors)
    for g in new_gen:
        main.visualize_strategy_tables(g)

 '''
