import datetime
from markupsafe import Markup


def nice_date(time):
    date = time.date()
    today = datetime.date.today()
    if date == today:
        return 'Today'
    if date - datetime.timedelta(days=1) == today:
        return 'Yesterday'
    result = date.strftime('%A %d %B')
    if date.year != today.year:
        result += date.strftime(' %Y')
    return result


def csrf_token(request):
    return Markup('<input type="hidden" name="csrf_token" value="{}"/>'
        .format(request.session.get_csrf_token()))
