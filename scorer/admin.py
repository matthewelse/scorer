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

from django.contrib import admin
from scorer.models import *

# Register your models here.

def make_active_round(modeladmin, request, queryset):
	current_event = Event.objects.get(active=True)

	active = Round.objects.filter(active=True, event=current_event)
	active.update(active=False)

	queryset.update(active=True)
make_active_round.short_description = "Set Active Round"

def make_active_event(modeladmin, request, queryset):
	active = Event.objects.filter(active=True)
	active.update(active=False)

	queryset.update(active=True)
make_active_event.short_description = "Set Active Event"

def clear_active_round(modeladmin, request, queryset):
	current_event = Event.objects.get(active=True)

	active = Round.objects.filter(active=True, event=current_event)
	active.update(active=False)
clear_active_round.short_description = "Clear Active Round (Select Anything)"

def set_to_current_event(modeladmin, request, queryset):
	current_event = Event.objects.get(active=True)
	queryset.update(event=current_event)
set_to_current_event.short_description = "Move to Active Event"

class RoundScoreInline(admin.StackedInline):
	model = RoundScore
	extra = 3

class TeamAdmin(admin.ModelAdmin):
	list_display = ('name', 'used_joker', 'joker_round', 'score', 'position_pretty', 'rounds_scored')
	list_filter = ('event',)

	inlines = [RoundScoreInline]
	actions = [set_to_current_event]

class RoundAdmin(admin.ModelAdmin):
	list_display = ('full_name', 'active', 'average_score', 'jokers', 'can_use_joker', 'maximum_score')
	list_filter = ('event',)

	inlines = [RoundScoreInline]
	actions = [make_active_round, clear_active_round, set_to_current_event]

class RoundScoreAdmin(admin.ModelAdmin):
	list_display = ('round', 'team', 'score', 'joker_used')

class EventRoundInline(admin.StackedInline):
	model = Round
	extra = 3

class EventAdmin(admin.ModelAdmin):
	list_display = ('name', 'active')

	inlines = [EventRoundInline]
	actions = [make_active_event]

admin.site.register(Team, TeamAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Event, EventAdmin)
#admin.site.register(RoundScore, RoundScoreAdmin)
