#!/usr/bin/env python
# Evolutionary Blackjack
# Semester Project for CSCE A405 AI
# Austin Edwards, Tuva Granoien, and Logan Chamberlain
# Fall 2022
#
#
################################################################################


class dealer():
    def __init__(self):
        self.hand = [0, 0]
        self.hole_card = 0
        self.total = 0
