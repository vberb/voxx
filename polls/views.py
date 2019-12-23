from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Choice, Question
from .process import process_results


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if question.voting_system == 'M':  # Majoritarian
        try:
            selected_choice = question.choice_set.filter(pk=request.POST['choice'])
        except (KeyError, Choice.DoesNotExist):
            # Redisplay the question voting form.
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message':  "You didn't select a choice.",
            })
        else:
            selected_choice.update(votes=F('votes') + 1)
            process_results(question)
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

    if question.voting_system == 'S':  # Schulze
        try:
            # form = {'select<choice_id>': '<choice_rank>'}
            form = {s: request.POST[s] for s in request.POST if s.startswith('select')}  # KeyError exc.?
            choices_count = question.choice_set.count()
            if len(form) != choices_count:
                raise ValueError  # Ballot args missing
            # ranked_choices = {<Choice: ...>: <choice_rank>}
            ranked_choices = dict()
            for key in form:
                choice_id = int(key[6:])  # ValueError exc.?
                choice = question.choice_set.get(pk=choice_id)  # Choice.DoesNotExist exc.?
                choice_rank = int(form[key]) if form[key] != '\xa0' else choices_count  # ValueError exc.?
                if choice_rank < 1 or choice_rank > choices_count:
                    raise ValueError
                ranked_choices[choice] = choice_rank
            if all(ranked_choices[choice] == choices_count for choice in ranked_choices):
                raise ValueError  # Empty ballot
        except (KeyError, ValueError, Choice.DoesNotExist):
            # Redisplay the question voting form.
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message':  "Wrong ballot.",
            })
        else:
            new_vote = question.vote_set.create(vote_datetime=timezone.now())
            for choice in ranked_choices:
                new_vote.votechoice_set.create(choice_id=choice.id, rank=ranked_choices[choice])
            process_results(question)
            return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
