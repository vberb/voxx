from collections import defaultdict
from itertools import product


def process_results(question):
    if question.voting_system == 'M':  # Majoritarian
        for rank, choice in enumerate(question.choice_set.order_by('-votes')):
            choice.rank = rank + 1
            choice.save()

    # https://en.wikipedia.org/wiki/Schulze_method
    if question.voting_system == 'S':  # Schulze
        # d matrix
        d = defaultdict(int)
        for vote in question.vote_set.all():
            votechoices = vote.votechoice_set.all()
            for (choiceV, choiceW) in product(votechoices, votechoices):
                if choiceV.rank < choiceW.rank:  # the one with smaller rank wins
                    d[choiceV.choice, choiceW.choice] += 1

        # p matrix
        choices = question.choice_set.all()
        p = defaultdict(int)
        for (choiceV, choiceW) in product(choices, choices):
            strength = d[choiceV, choiceW]
            if strength > d[choiceW, choiceV]:
                p[choiceV, choiceW] = strength

        for (choiceU, choiceV, choiceW) in product(choices, choices, choices):
            if choiceU != choiceV and choiceV != choiceW and choiceW != choiceU:
                p[choiceV, choiceW] = max(p[choiceV, choiceW], min(p[choiceV, choiceU], p[choiceU, choiceW]))


        # wins = {number_of_wins: [choice, ...]}
        wins = defaultdict(list)

        for choiceV in choices:
            wins[sum(map(bool, (p[choiceV, choiceW] > p[choiceW, choiceV] for choiceW in choices)))].append(choiceV)

        sorted_wins = sorted(wins, reverse=True)
        for rank, wins_count in enumerate(sorted_wins):
            for choice in wins[wins_count]:
                choice.rank = rank + 1
                choice.save()
