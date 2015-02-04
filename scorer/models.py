# Copyright (c) 2015, Matthew Else matthewelse1997@gmail.com

# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=30)
    active = models.BooleanField(default=False)
    current_status = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=30)
    joker_round = models.ForeignKey('Round', null=True, blank=True, limit_choices_to={'can_use_joker': True})
    event = models.ForeignKey('Event', null=True)

    def used_joker(self):
        return self.joker_round is not None
    used_joker.boolean = True

    def score(self):
        round_scores = RoundScore.objects.filter(team=self)
        scores = [score.score * (2 if self.joker_round == score.round else 1) for score in round_scores]

        return sum(scores)

    def position(self):
        scores = [team.score() for team in Team.objects.all()]
        return scores.index(self.score()) + 1, scores.count(self.score()) >= 2

    def position_pretty(self):
        score, joint = self.position()
        return "%s%i" % ('=' if joint else '', score)

    def position_web(self):
        ordinals = {
            0: 'th',
            1: 'st',
            2: 'nd',
            3: 'rd',
            4: 'th',
            5: 'th',
            6: 'th',
            7: 'th',
            8: 'th',
            9: 'th'
        }

        score, joint = self.position()
        return "%s%i<sup>%s</sup>" % ('=' if joint else '', score, ordinals[score % 10])

    def __str__(self):
        return self.name

class Round(models.Model):
    name = models.CharField(max_length=20)
    can_use_joker = models.BooleanField(default=True)
    maximum_score = models.DecimalField(default=10.0, decimal_places=1, max_digits=5)
    active = models.BooleanField(default=False)
    event = models.ForeignKey('Event', null=True)

    def average_score(self):
        if len(RoundScore.objects.filter(round=self)) == 0:
            return None
        else:
            scores = [x.score for x in RoundScore.objects.filter(round=self)]
            return sum(scores)/len(scores)

    def jokers(self):
        return len(Team.objects.filter(joker_round=self))

    def full_name(self):
        return "%s/%s" % (self.event.name, self.name)

    def __str__(self):
        return "%s/%s" % (self.event.name, self.name)

class RoundScore(models.Model):
    round = models.ForeignKey('Round')
    team = models.ForeignKey('Team', limit_choices_to={'event__active': True})

    score = models.DecimalField(decimal_places=1, max_digits=5)

    def joker_used(self):
        return (self.team.joker_round == self.round)
    joker_used.boolean = True

    def __str__(self):
        return "%s (%s)" % (self.team.name, self.round.name)
