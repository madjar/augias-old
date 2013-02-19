import datetime
import json
from markupsafe import escape, Markup


class FlashMessage(str):
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
    request.session.flash(FlashMessage(message, level))

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


def mean_execution_time_graph(task):
    N = 10
    rows = []
    executions = [t for t in task.executions if t.length]
    executions.sort(key=lambda e: e.time)
    # TODO : replace this with a query
    total = 0
    for i, e in enumerate(executions):
        total += e.length
        if i >= N:
            total -= executions[i-N].length
            rows.append((e.time, total / N))

    columns = (('Date', 'date'), ('Length', 'number'))

    return encode_google_datatable(columns, rows)


def time_spent_for_task_graph(task):
    pass

