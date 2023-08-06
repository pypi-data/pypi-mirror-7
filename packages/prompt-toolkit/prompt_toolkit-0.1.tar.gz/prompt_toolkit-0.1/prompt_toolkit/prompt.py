"""
Prompt representation.
"""
from __future__ import unicode_literals

from pygments.token import Token
from .enums import ReverseSearchDirection

__all__ = ('Prompt', )


class PromptBase(object):
    """ Minimal base class for a valid prompt. """
    def __init__(self, line, code):
        self.line = line
        self.code = code

    def get_prompt(self):
        """
        Text shown before the actual input. (The actual prompt.)
        Generator of (Token, text) tuples.
        """
        yield (Token.Prompt, '>')

    def get_second_line_prefix(self):
        """
        When the renderer has to render the command line over several lines
        because the input contains newline characters. This prefix will be
        inserted before each line.

        This is a generator of (Token, text) tuples.
        """
        # Take the length of the default prompt.
        prompt_text = ''.join(p[1] for p in self.get_prompt())
        length = len(prompt_text.rstrip())
        spaces = len(prompt_text) - length

        yield (Token.Prompt.SecondLinePrefix, '.' * length)
        yield (Token.Prompt.SecondLinePrefix, ' ' * spaces)

    def get_help_tokens(self):
        """
        Return a list of (Token, text) tuples for the help text.
        (This will be shown by the renderer after the text input, and can be
        used to create a help text or a status line.)
        """
        return []


class Prompt(PromptBase):
    """
    Default Prompt class
    """
    def get_prompt(self):
        if self.line._in_isearch:
            return self.get_isearch_prompt()
        elif self.line._arg_prompt_text:
            return self.get_arg_prompt(self.line._arg_prompt_text)
        else:
            return self.get_default_prompt()

    def get_default_prompt(self):
        """
        Yield the tokens for the default prompt.
        """
        yield (Token.Prompt, '> ')

    def get_arg_prompt(self, text):
        """
        Yield the tokens for the arg-prompt.
        """
        yield (Token.Prompt.Arg, '(arg: ')
        yield (Token.Prompt.ArgText, str(text))
        yield (Token.Prompt.Arg, ') ')

    def get_isearch_prompt(self):
        """
        Yield the tokens for the prompt when we go in reverse-i-search mode.
        """
        yield (Token.Prompt.ISearch.Bracket, '(')

        if self.line._isearch_direction == ReverseSearchDirection.BACKWARD:
            yield (Token.Prompt.ISearch, 'reverse-i-search')
        else:
            yield (Token.Prompt.ISearch, 'i-search')

        yield (Token.Prompt.ISearch.Bracket, ')')

        yield (Token.Prompt.ISearch.Backtick, '`')
        yield (Token.Prompt.ISearch.Text, self.line._isearch_text)
        yield (Token.Prompt.ISearch.Backtick, '`')
        yield (Token.Prompt.ISearch.Backtick, ': ')
