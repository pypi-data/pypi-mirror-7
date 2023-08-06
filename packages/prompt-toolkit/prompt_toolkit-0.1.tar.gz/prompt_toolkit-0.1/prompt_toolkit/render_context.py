
class RenderContext(object):
    """
    :param accept: True when the user accepts the input, by pressing enter.
                   (In that case we don't highlight the current line, and
                   set the mouse cursor at the end.)
    :param abort: True after Ctrl-C abort.
    :param highlight_regions: `None` or list of (start,len) tuples of the
                              characters to highlight.
    """
    def __init__(self, prompt, code_obj, accept=False, abort=False, highlight_regions=None):
        assert not (accept and abort)

        self.prompt = prompt
        self.code_obj = code_obj
        self.accept = accept
        self.abort = abort
        self.highlight_regions = highlight_regions
