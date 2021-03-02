import os
import random
from lists import na_characters

def matchup(args: list):
    pnum = len(args)
    mnum = pnum//2
    matchups = []
    for _ in range(mnum):
        p1, p2 = random.sample(args, 2)
        matchups.append([p1, p2])
        args.remove(p1)
        args.remove(p2)
    return(matchups)

def teamsel():
    random.shuffle(na_characters)
    return(' **|** '.join(random.sample(na_characters, 3)))
