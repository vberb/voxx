# model ideas:
# rename tables Vote, VoteChoice to Ballot etc.
# create Vote record for majoritarian votes too
# merge Choice fields 'votes' and 'rank' to 'result'


import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    class VotingSystem(models.TextChoices):
        MAJORITARIAN = 'M', 'Majoritarian'
        SCHULZE = 'S', 'Schulze'

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    voting_system = models.CharField(max_length=1, choices=VotingSystem.choices, default=VotingSystem.MAJORITARIAN)

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.PositiveIntegerField(default=0)
    rank = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.choice_text


class Vote(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    vote_datetime = models.DateTimeField('voting date and time')

    def __str__(self):
        ranked_choices = self.votechoice_set.order_by('rank')
        return ','.join(f'{c.choice}({c.rank})' for c in ranked_choices) + ' @' + str(self.vote_datetime)


class VoteChoice(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    rank = models.PositiveIntegerField('choice ranking')
