from django.db import models

# Create your models here.

class Event(models.Model):
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=False)
    current_status = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=50)
    joker_round = models.ForeignKey('Round', null=True, blank=True, limit_choices_to={'can_use_joker': True})
    event = models.ForeignKey('Event', null=True)

    def used_joker(self):
        return self.joker_round is not None and len(RoundScore.objects.filter(team=self, round=self.joker_round)) != 0
    used_joker.boolean = True

    def score(self):
        round_scores = RoundScore.objects.filter(team=self)
        scores = [score.score * (2 if self.joker_round == score.round else 1) for score in round_scores]

        return sum(scores)

    def position_raw(self):
        scores = list(sorted([team.score() for team in Team.objects.filter(event=self.event)], reverse=True))
        return scores.index(self.score()) + 1

    def position(self):
        current_event = Event.objects.get(active=True)
        scores = list(sorted([team.score() for team in Team.objects.filter(event=self.event)], reverse=True))
        return scores.index(self.score()) + 1, scores.count(self.score()) >= 2

    def position_pretty(self):
        score, joint = self.position()
        return "%s%i" % ('=' if joint else '', score)

    def rounds_scored(self):
        return len(RoundScore.objects.filter(team=self))

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
    name = models.CharField(max_length=50)
    can_use_joker = models.BooleanField(default=True)
    maximum_score = models.DecimalField(default=10.0, decimal_places=1, max_digits=5)
    active = models.BooleanField(default=False)
    event = models.ForeignKey('Event', null=True)

    def average_score(self):
        if len(RoundScore.objects.filter(round=self)) == 0:
            return None
        else:
            scores = [x.score for x in RoundScore.objects.filter(round=self)]
            return "%.1f" % (sum(scores)/len(scores))

    def jokers(self):
        return len(Team.objects.filter(joker_round=self))

    def full_name(self):
        return "%s/%s" % (self.event.name, self.name)

    def __str__(self):
        return "%s/%s" % (self.event.name, self.name)

class RoundScore(models.Model):
    round = models.ForeignKey('Round', limit_choices_to={'event__active': True})
    team = models.ForeignKey('Team', limit_choices_to={'event__active': True})

    score = models.DecimalField(decimal_places=1, max_digits=5)

    def joker_used(self):
        return (self.team.joker_round == self.round)
    joker_used.boolean = True

    def __str__(self):
        return "%s (%s)" % (self.team.name, self.round.name)
