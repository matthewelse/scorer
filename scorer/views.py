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

import csv

from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponse

from scorer.models import Team, Round, Event, RoundScore

# Create your views here.

def big_screen(request):
	current_event = Event.objects.get(active=True)

	context = {
		'quiz_name': current_event.name
	}
	return render(request, 'scorer/container.html', context)

def podium(request):
	current_event = Event.objects.get(active=True)
	teams = sorted(list(Team.objects.filter(event=current_event)), key=lambda team: team.score(), reverse=True)

	if len(teams) < 3:
		print("uh oh")
		return rank(request)

	first_place = teams.pop(0)
	second_place = teams.pop(0)
	third_place = teams.pop(0)

	try:
		current_round = Round.objects.get(active=True, event=current_event).name
	except:
		current_round = ""

	context = {
		'quiz_name': current_event.name,
		'current_round': current_round,
		'first_place': first_place,
		'second_place': second_place,
		'third_place': third_place,
		'other_teams': teams,
	}

	return render(request, 'scorer/podium.html', context)
	
def top3(request):
	current_event = Event.objects.get(active=True)
	teams = sorted(list(Team.objects.filter(event=current_event)), key=lambda team: team.score(), reverse=True)

	if len(teams) < 3:
		print("uh oh")
		return rank(request)

	first_place = teams.pop(0)
	second_place = teams.pop(0)
	third_place = teams.pop(0)

	try:
		current_round = Round.objects.get(active=True, event=current_event).name
	except:
		current_round = ""

	context = {
		'quiz_name': current_event.name,
		'current_round': current_round,
		'first_place': first_place,
		'second_place': second_place,
		'third_place': third_place,
	}

	return render(request, 'scorer/top3.html', context)

def rank(request):
	current_event = Event.objects.get(active=True)
	teams = sorted(list(Team.objects.filter(event=current_event)), key=lambda team: team.score(), reverse=True)

	try:
		current_round = Round.objects.get(active=True, event=current_event).name
	except:
		current_round = ""

	context = {
		'quiz_name': current_event.name,
		'current_round': current_round,
		'teams': teams,
	}

	return render(request, 'scorer/scoreboard.html', context)

def controls(request):
	return render(request, 'scorer/controls.html')

def set_status(request, type):
	print(type)

	current_event = Event.objects.get(active=True)
	current_event.current_status=type
	current_event.save()

	return HttpResponse("")

def get_status(request):
	current_event = Event.objects.get(active=True)
	status = current_event.current_status

	current_event.current_status = None
	current_event.save()

	return HttpResponse(status)

def export_csv(request):
    current_event = Event.objects.get(active=True)
    rounds = list(Round.objects.filter(event=current_event))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + current_event.name + '.csv'

    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))

    headings = [u"Team Name", u"Total Score", u"Position", u"Rounds Scored", u"Joker Round"]
    for round in rounds:
	headings.append(round.name)

    writer.writerow(headings)
    teams = list(Team.objects.filter(event=current_event))

    scores = []

    for team in teams:
        team_data = [team.name, team.score(), team.position_pretty(), team.rounds_scored(), team.joker_round.name]
	scores.append(team.score())
        for round in rounds:
		score = RoundScore.objects.get(team=team, round=round).score
		if team.joker_round == round:
			score = score * 2
		team_data.append(score)
	writer.writerow(team_data)

    mean_score = sum(scores) / len(scores)

    averages = [u"Means", mean_score, u"N/A", u"N/A", u"N/A"]
    for round in rounds:
	averages.append(round.average_score())
    writer.writerow(averages)

    return response
