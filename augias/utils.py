import datetime
import json
from markupsafe import escape, Markup
from dateutil.relativedelta import relativedelta, MO
from collections import defaultdict
import dogpile.cache

cache = dogpile.cache.make_region()


class FlashMessage(Markup):
    def __new__(cls, message, level=None):
        self = super().__new__(cls, message)
        self.level = level
        return self

    def cssclass(self):
        if self.level == 'alert':
            return ''
        else:
            return 'alert-' + self.level

def _flash(request, message, level):
    request.session.flash(FlashMessage(escape(message), level))

def _make_flash_method(level):
    # partial does not work with methods, and we need an extra method for the closure
    # That's a lot of wasted time just to save 5 lines
    return lambda request, message: _flash(request, message, level)

def flash(config):
    for level in ('success', 'warning', 'error', 'info'):
        config.add_request_method(_make_flash_method(level), 'flash_{}'.format(level))


def _date_json(obj):
    """If obj is a datetime, returns a google-json-enable representation.
    Used as default argument of json.dump"""
    if isinstance(obj, datetime.datetime):
        month = obj.month - 1
        return 'Date({0.year}, {1}, {0.day})'.format(obj, month)

def _escape_if_string(s):
    if isinstance(s, str):
        return escape(s)
    return s

def encode_google_datatable(columns, rows):
    """Creates an ugly google-json datatable"""
    data = {'cols': [{'label': _escape_if_string(label), 'type': t}
                     for label, t in columns],
            'rows': [{'c': [{'v': _escape_if_string(v)} for v in values]}
                     for values in rows]}
    return Markup(json.dumps(data, default=_date_json))


def raw_executions_graph(task):
    executions = task.executions
    executors = set(ex.executor for ex in executions)
    exec_id = {person: i for (i, person) in enumerate(executors)}

    columns = [('Date', 'date')]
    for person in executors:
        columns.append((escape(person or 'Everybody'), 'number'))

    rows = []
    for ex in executions:
        series = [None] * len(exec_id)
        series[exec_id[ex.executor]] = ex.length or 0
        rows.append([ex.time] + series)

    return encode_google_datatable(columns, rows)


class ExecutionTime:
    def __init__(self):
        self.sure = 0  # Recorded time
        self.guessed = 0  # Guessed time
        self.missing = 0  # Executions with not time info

    @property
    def total(self):
        return self.sure + self.guessed

    def add(self, execution):
        if execution.length is not None:
            self.sure += execution.length
        else:
            guess = execution.task.mean_execution
            if guess:
                self.guessed += guess
            else:
                self.missing += 1

    def __html__(self):
        r = '{:.0f}'.format(self.total)
        extra = ''
        if self.guessed:
            extra += ' (~{:.0f})'.format(self.guessed)
        if self.missing:
            extra += ' + {:d} miss'.format(self.missing)
        if extra:
            r += '<span class="text-muted">{}</span>'.format(extra)
        return r


def report_for_range(notebook, begin, end):
    from augias.models import DBSession, Execution, Task
    executions = (DBSession.query(Execution)
                  .filter(Execution.time.between(begin, end))
                  .join('task').filter(Task.notebook==notebook)).all()

    total = ExecutionTime()
    by_person = defaultdict(ExecutionTime)
    by_task = defaultdict(lambda: defaultdict(ExecutionTime))

    for e in executions:
        total.add(e)
        by_person[e.executor].add(e)
        by_task[e.task][e.executor].add(e)
        by_task[e.task]['total'].add(e)
        if not e.executor:
            # Add common executions to everybody
            for person in notebook.users:
                by_person[person].add(e)
                by_task[e.task][person].add(e)


    def sorter(item):
        task, executions = item
        return (-executions['total'].total, task.name)

    by_task = sorted(by_task.items(), key=sorter)

    return {'total': total, 'by_task': by_task, 'by_person': by_person}


def report_for_week(notebook, n=-1):
    today = datetime.date.today()
    begin = today + relativedelta(weekday=MO(n-1))
    end = today + relativedelta(weekday=MO(n))
    # TODO : tester que ça couvre exactement l'intervale que je veux

    # TODO : c'est pas du beau code, du tout
    d = report_for_range(notebook, begin, end)
    d['begin'] = begin
    d['end'] = end
    return d


