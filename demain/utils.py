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