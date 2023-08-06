"""
Data structures for the line input.
It holds the text, cursor position, history, etc...
"""
from __future__ import unicode_literals

from functools import wraps

from .code import Code, ValidationError
from .document import Document
from .enums import IncrementalSearchDirection, LineMode
from .prompt import Prompt
from .render_context import RenderContext
from .history import History

import os
import tempfile
import subprocess

__all__ = (
        'Line',

        # Exceptions raised by the Line object.
        'Exit',
        'ReturnInput',
        'Abort',
)

class Exit(Exception):
    def __init__(self, render_context):
        self.render_context = render_context


class ReturnInput(Exception):
    def __init__(self, document, render_context):
        self.document = document
        self.render_context = render_context


class Abort(Exception):
    def __init__(self, render_context):
        self.render_context = render_context


class ClipboardDataType(object):
    """
    Depending on how data has been copied, it can be pasted differently.
    If a whole line is copied, it will always be inserted as a line (below or
    above thu current one). If a word has been copied, it wiss be pasted
    inline. So, if you copy a whole line, it will not be pasted in the middle
    of another line.
    """
    #: Several characters or words have been copied. They are pasted inline.
    CHARACTERS = 'characters'

    #: A whole line that has been copied. This will be pasted below or above
    #: the current line as a new line.
    LINES = 'lines'


class ClipboardData(object):
    """
    Text on the clipboard.

    :param text: string
    :param type: :class:`~.ClipboardDataType`
    """
    def __init__(self, text='', type=ClipboardDataType.CHARACTERS):
        self.text = text
        self.type = type


def _to_mode(*modes):
    """
    When this method of the `Line` object is called. Make sure that we are in
    the correct LineMode.  (Quit reverse search / complete mode when
    necessary.)
    """
    def mode_decorator(func):
        @wraps(func)
        def wrapper(self, *a, **kw):
            if self.mode not in modes:
                if self.mode == LineMode.INCREMENTAL_SEARCH:
                    self.exit_isearch()

                elif self.mode == LineMode.COMPLETE:
                    self.mode = LineMode.NORMAL

            return func(self, *a, **kw)
        return wrapper
    return mode_decorator


class CompletionState(object):
    def __init__(self, original_document, current_completions=None):
        #: Document as it was when the completion started.
        self.original_document = original_document

        #: List of all the current Completion instances which are possible at
        #: this point.
        self.current_completions = current_completions or []

        #: Position in the `current_completions` array.
        #: This can be `None` to indicate "no completion", the original text.
        self.complete_index = 0 # Position in the `_completions` array.

    @property
    def original_cursor_position(self):
        self.original_document.cursor_position

    @property
    def current_completion_text(self):
        if self.complete_index is None:
            return ''
        else:
            return self.current_completions[self.complete_index].suffix

class _IncrementalSearchState(object):
    def __init__(self, original_cursor_position, original_working_index):
        self.isearch_direction = IncrementalSearchDirection.FORWARD
        self.isearch_text = ''

        self.original_working_index = original_working_index
        self.original_cursor_position = original_cursor_position


class Line(object):
    """
    The core data structure that holds the text and cursor position of the
    current input line and implements all text manupulations on top of it. It
    also implements the history, undo stack, reverse search and the completion
    state.

    :attr code_cls: :class:`~prompt_toolkit.code.CodeBase` class.
    :attr prompt_cls: :class:`~prompt_toolkit.prompt.PromptBase` class.
    :attr history: :class:`~prompt_toolkit.history.History` instance.
    """
    #: Boolean to indicate whether we should consider this line a multiline input.
    #: If so, the `InputStreamHandler` can decide to insert newlines when pressing [Enter].
    #: (Instead of accepting the input.)
    is_multiline = False

    def __init__(self, renderer=None, code_cls=Code, prompt_cls=Prompt, history_cls=History):
        self.renderer = renderer
        self.code_cls = code_cls
        self.prompt_cls = prompt_cls

        #: The command line history.
        self._history = history_cls()

        self._clipboard = ClipboardData()

        self.__cursor_position = 0

        #: Readline argument text (for displaying in the prompt.)
        #: https://www.gnu.org/software/bash/manual/html_node/Readline-Arguments.html
        self._arg_prompt_text = ''

        self.reset()

    def reset(self, initial_value=''):
        self.mode = LineMode.NORMAL
        self.cursor_position = len(initial_value)

        # `ValidationError` instance. (Will be set when the input is wrong.)
        self.validation_error = None

        # State of Incremental-search
        self.isearch_state = None

        # State of complete browser
        self.complete_state = None

        # Undo stack
        self._undo_stack = [] # Stack of (text, cursor_position)

        #: The working lines. Similar to history, except that this can be
        #: modified. The user can press arrow_up and edit previous entries.
        #: Ctrl-C should reset this, and copy the whole history back in here.
        #: Enter should process the current command and append to the real
        #: history.
        self._working_lines = self._history.strings[:]
        self._working_lines.append(initial_value)
        self.__working_index = len(self._working_lines) - 1

    ### <getters/setters>

    @property
    def text(self):
        return self._working_lines[self._working_index]

    @text.setter
    def text(self, value):
        self._working_lines[self._working_index] = value

        # Always quit autocomplete mode when the text changes.
        if self.mode == LineMode.COMPLETE:
            self.mode = LineMode.NORMAL

        # Remove any validation errors.
        self.validation_error = None

        self._text_changed()

    @property
    def cursor_position(self):
        return self.__cursor_position

    @cursor_position.setter
    def cursor_position(self, value):
        self.__cursor_position = max(0, value)

        # Always quit autocomplete mode when the cursor position changes.
        if self.mode == LineMode.COMPLETE:
            self.mode = LineMode.NORMAL

        # Remove any validation errors.
        self.validation_error = None

    @property
    def _working_index(self):
        return self.__working_index

    @_working_index.setter
    def _working_index(self, value):
        # Always quit autocomplete mode when the working index changes.
        if self.mode == LineMode.COMPLETE:
            self.mode = LineMode.NORMAL

        self.__working_index = value
        self._text_changed()

    ### End of <getters/setters>

    def _text_changed(self):
        """
        Not implemented. Override to capture when the current visible text
        changes.
        """
        pass

    def save_to_undo_stack(self):
        """
        Safe current state (input text and cursor position), so that we can
        restore it by calling undo.
        """
        state = (self.text, self.cursor_position)

        # Safe if the text is different from the text at the top of the stack
        # is different.
        if not self._undo_stack or self._undo_stack[-1][0] != state[0]:
            self._undo_stack.append(state)

    def set_current_line(self, value):
        """
        Replace current line (Does not touch other lines in multi-line input.)
        """
        # Move cursor to start of line.
        self.cursor_to_start_of_line(after_whitespace=False)

        # Replace text
        self.delete_until_end_of_line()
        self.insert_text(value, move_cursor=False)

    def transform_lines(self, line_index_iterator, transform_callback):
        """
        Transforms the text on a range of lines.
        When the iterator yield an index not in the range of lines that the
        document contains, it skips them silently.

        To uppercase some lines::

            transform_lines(range(5,10), lambda text: text.upper())

        :param line_index_iterator: Iterator of line numbers (int)
        :param transform_callback: callable that takes the original text of a
                                   line, and return the new text for this line.
        """
        # Split lines
        lines = self.text.split('\n')

        # Apply transformation
        for index in line_index_iterator:
            try:
                lines[index] = transform_callback(lines[index])
            except IndexError:
                pass

        self.text = '\n'.join(lines)

    @property
    def document(self):
        """
        Return :class:`.Document` instance from the current text and cursor
        position.
        """
        # TODO: this can be cached as long self.text does not change.
        return Document(self.text, self.cursor_position)

    def set_arg_prompt(self, arg):
        """
        Called from the `InputStreamHandler` to set a "(arg: x)"-like prompt.
        (Both in Vi and Emacs-mode we have a way to repeat line operations.
        Settings this attribute to the `Line` object allows the prompt/renderer
        to visualise it.)
        """
        self._arg_prompt_text = arg

    @_to_mode(LineMode.NORMAL)
    def home(self):
        self.cursor_position = 0

    @_to_mode(LineMode.NORMAL)
    def end(self):
        self.cursor_position = len(self.text)

    @_to_mode(LineMode.NORMAL)
    def cursor_left(self):
        if self.document.cursor_position_col > 0:
            self.cursor_position -= 1

    @_to_mode(LineMode.NORMAL)
    def cursor_right(self):
        if not self.document.cursor_at_the_end_of_line:
            self.cursor_position += 1

    @_to_mode(LineMode.NORMAL)
    def cursor_up(self):
        """
        (for multiline edit). Move cursor to the previous line.
        """
        new_pos = self.document.cursor_up_position
        if new_pos is not None:
            self.cursor_position = new_pos

    @_to_mode(LineMode.NORMAL)
    def cursor_down(self):
        """
        (for multiline edit). Move cursor to the next line.
        """
        new_pos = self.document.cursor_down_position
        if new_pos is not None:
            self.cursor_position = new_pos

    @_to_mode(LineMode.NORMAL, LineMode.COMPLETE)
    def auto_up(self):
        """
        If we're not on the first line (of a multiline input) go a line up,
        otherwise go back in history.
        """
        if self.mode == LineMode.COMPLETE:
            self.complete_previous()
        elif self.document.cursor_position_row > 0:
            self.cursor_up()
        else:
            self.history_backward()

    @_to_mode(LineMode.NORMAL, LineMode.COMPLETE)
    def auto_down(self):
        """
        If we're not on the last line (of a multiline input) go a line down,
        otherwise go forward in history.
        """
        if self.mode == LineMode.COMPLETE:
            self.complete_next()
        elif self.document.cursor_position_row < self.document.line_count - 1:
            self.cursor_down()
        else:
            old_index = self._working_index
            self.history_forward()

            # If we moved to the next line, place the cursor at the beginning.
            if old_index != self._working_index:
                self.cursor_position = 0

    @_to_mode(LineMode.NORMAL)
    def cursor_word_back(self):
        """ Move the cursor to the start of the previous word. """
        # Move at least one character to the left.
        self.cursor_position += (self.document.find_start_of_previous_word() or 0)

    @_to_mode(LineMode.NORMAL)
    def cursor_word_forward(self):
        """ Move the cursor to the start of the following word. """
        self.cursor_position += (self.document.find_next_word_beginning() or 0)

    @_to_mode(LineMode.NORMAL)
    def cursor_to_end_of_word(self):
        """
        Move the cursor right before the last character of the next word
        ending.
        """
        end = self.document.find_next_word_ending(include_current_position=False)
        if end > 1:
            self.cursor_position += end - 1

    @_to_mode(LineMode.NORMAL)
    def cursor_to_end_of_line(self):
        """
        Move cursor to the end of the current line.
        """
        self.cursor_position += len(self.document.current_line_after_cursor)

    @_to_mode(LineMode.NORMAL)
    def cursor_to_start_of_line(self, after_whitespace=False):
        """ Move the cursor to the first character of the current line. """
        self.cursor_position -= len(self.document.current_line_before_cursor)

        if after_whitespace:
            text_after_cursor = self.document.current_line_after_cursor
            self.cursor_position += len(text_after_cursor) - len(text_after_cursor.lstrip())

    # NOTE: We can delete in i-search!
    @_to_mode(LineMode.NORMAL, LineMode.INCREMENTAL_SEARCH)
    def delete_character_before_cursor(self, count=1): # TODO: unittest return type
        """ Delete character before cursor, return deleted character. """
        assert count > 0
        deleted = ''

        if self.mode == LineMode.INCREMENTAL_SEARCH:
            self.isearch_state.isearch_text = self.isearch_state.isearch_text[:-count]
        else:
            if self.cursor_position > 0:
                deleted = self.text[self.cursor_position - count:self.cursor_position]
                self.text = self.text[:self.cursor_position - count] + self.text[self.cursor_position:]
                self.cursor_position -= len(deleted)

        return deleted

    @_to_mode(LineMode.NORMAL)
    def delete(self, count=1): # TODO: unittest `count`
        """ Delete one character. Return deleted character. """
        if self.cursor_position < len(self.text):
            deleted = self.document.text_after_cursor[:count]
            self.text = self.text[:self.cursor_position] + \
                    self.text[self.cursor_position + len(deleted):]
            return deleted
        else:
            return ''

    @_to_mode(LineMode.NORMAL)
    def delete_word(self):
        """ Delete one word. Return deleted word. """
        to_delete = self.document.find_next_word_beginning()
        return self.delete(count=to_delete)

    @_to_mode(LineMode.NORMAL)
    def delete_word_before_cursor(self): # TODO: unittest
        """ Delete one word before cursor. Return deleted word. """
        to_delete = - (self.document.find_start_of_previous_word() or 0)
        return self.delete_character_before_cursor(to_delete)

    @_to_mode(LineMode.NORMAL)
    def delete_until_end(self):
        """ Delete all input until the end. Return deleted text. """
        deleted = self.text[self.cursor_position:]
        self.text = self.text[:self.cursor_position]
        return deleted

    @_to_mode(LineMode.NORMAL)
    def delete_until_end_of_line(self): # TODO: unittest.
        """
        Delete all input until the end of this line. Return deleted text.
        """
        to_delete = len(self.document.current_line_after_cursor)
        return self.delete(count=to_delete)

    @_to_mode(LineMode.NORMAL)
    def delete_from_start_of_line(self): # TODO: unittest.
        """
        Delete all input from the start of the line until the current
        character. Return deleted text.
        (Actually, this is the same as pressing backspace until the start of
        the line.)
        """
        to_delete = len(self.document.current_line_before_cursor)
        return self.delete_character_before_cursor(to_delete)

    @_to_mode(LineMode.NORMAL)
    def delete_current_line(self):
        """
        Delete current line. Return deleted text.
        """
        document = self.document

        # Remember deleted text.
        deleted = document.current_line

        # Cut line.
        lines = document.lines
        pos = document.cursor_position_row
        self.text = '\n'.join(lines[:pos] + lines[pos+1:])

        # Move cursor.
        before_cursor = document.current_line_before_cursor
        self.cursor_position -= len(before_cursor)
        self.cursor_to_start_of_line(after_whitespace=True)

        return deleted

    @_to_mode(LineMode.NORMAL)
    def join_next_line(self):
        """
        Join the next line to the current one by deleting the line ending after
        the current line.
        """
        self.cursor_to_end_of_line()
        self.delete()

    @_to_mode(LineMode.NORMAL)
    def swap_characters_before_cursor(self):
        """
        Swap the last two characters before the cursor.
        """
        pos = self.cursor_position

        if pos >= 2:
            a = self.text[pos - 2]
            b = self.text[pos - 1]

            self.text = self.text[:pos-2] + b + a + self.text[pos:]

    @_to_mode(LineMode.NORMAL)
    def go_to_matching_bracket(self):
        """ Go to matching [, (, { or < bracket. """
        stack = 1

        for A, B in '()', '[]', '{}', '<>':
            if self.document.current_char == A:
                for i, c in enumerate(self.document.text_after_cursor[1:]):
                    if c == A: stack += 1
                    elif c == B: stack -= 1

                    if stack == 0:
                        self.cursor_position += (i + 1)
                        break

            elif self.document.current_char == B:
                for i, c in enumerate(reversed(self.document.text_before_cursor)):
                    if c == B: stack += 1
                    elif c == A: stack -= 1

                    if stack == 0:
                        self.cursor_position -= (i + 1)
                        break

    @_to_mode(LineMode.NORMAL)
    def go_to_substring(self, sub, in_current_line=False, backwards=False):
        """
        Find next occurence of this substring, and move cursor position there.
        """
        if backwards:
            index = self.document.find_backwards(sub, in_current_line=in_current_line)
        else:
            index = self.document.find(sub, in_current_line=in_current_line)

        if index:
            self.cursor_position += index

    @_to_mode(LineMode.NORMAL)
    def go_to_column(self, column):
        """
        Go to this column on the current line. (Go to the end column > length
        of the line.)
        """
        line_length = len(self.document.current_line)
        current_column = self.document.cursor_position_col
        column = max(0, min(line_length, column))

        self.cursor_position += column - current_column

    def create_code_obj(self):
        """
        Create `Code` instance from the current input.
        """
        return self.code_cls(self.document)

    @_to_mode(LineMode.NORMAL)
    def list_completions(self):
        """
        Get and show all completions
        """
        results = list(self.create_code_obj().get_completions())

        if results and self.renderer:
            self.renderer.render_completions(results)

    @_to_mode(LineMode.NORMAL)
    def complete(self): # TODO: rename to complete_common
        """ Autocomplete.
        Returns true if there was a completion. """
        # On the first tab press, try to find one completion and complete.
        result = self.create_code_obj().complete() # XXX: rename to get_common_completion()
        if result:
            self.text = self.text[:self.cursor_position] + result + self.text[self.cursor_position:]
            self.cursor_position += len(result)
            return True
        else:
            return False

    @_to_mode(LineMode.NORMAL, LineMode.COMPLETE)
    def complete_next(self, count=1):
        """
        Enter complete mode and browse through the completions.
        """
        if not self.mode == LineMode.COMPLETE:
            self._start_complete()
        else:
            completions_count = len(self.complete_state.current_completions)

            if self.complete_state.complete_index is None:
                index = 0
            elif self.complete_state.complete_index == completions_count - 1:
                index = None
            else:
                index = min(completions_count-1, self.complete_state.complete_index + count)
            self._go_to_completion(index)

    @_to_mode(LineMode.NORMAL, LineMode.COMPLETE)
    def complete_previous(self, count=1):
        """
        Enter complete mode and browse through the completions.
        """
        if not self.mode == LineMode.COMPLETE:
            self._start_complete()

        if self.complete_state:
            if self.complete_state.complete_index == 0:
                index = None
            elif self.complete_state.complete_index is None:
                index = len(self.complete_state.current_completions) - 1
            else:
                index = max(0, self.complete_state.complete_index - count)

            self._go_to_completion(index)

    def _start_complete(self):
        """
        Start completions. (Generate list of completions and initialize.)
        """
        # Generate list of all completions.
        current_completions = list(self.create_code_obj().get_completions())

        if current_completions:
            self.complete_state = CompletionState(
                        original_document=self.document,
                        current_completions=current_completions)
            self.insert_text(self.complete_state.current_completion_text)
            self.mode = LineMode.COMPLETE

        else:
            self.mode = LineMode.NORMAL
            self.complete_state = None

    def _go_to_completion(self, index):
        """
        Select a completion from the list of current completions.
        """
        assert self.mode == LineMode.COMPLETE

        # Undo previous completion
        count = len(self.complete_state.current_completion_text)
        if count:
            self.delete_character_before_cursor(count=len(self.complete_state.current_completion_text))

        # Set new completion
        self.complete_state.complete_index = index
        self.insert_text(self.complete_state.current_completion_text)

        self.mode = LineMode.COMPLETE

    def get_render_context(self, _abort=False, _accept=False):
        """
        Return a `RenderContext` object, to pass the current state to the renderer.
        """
        if self.mode == LineMode.INCREMENTAL_SEARCH:
            # In case of reverse search, render reverse search prompt.
            code = self.code_cls(self.document)

            if self.document.has_match_at_current_position(self.isearch_state.isearch_text):
                highlight_regions = [
                        (self.document.translate_index_to_position(self.cursor_position),
                        self.document.translate_index_to_position(self.cursor_position + len(self.isearch_state.isearch_text))) ]
            else:
                highlight_regions = [ ]

        else:
            code = self.create_code_obj()
            highlight_regions = [ ]

        # Complete state
        prompt = self.prompt_cls(self, code)
        if self.mode == LineMode.COMPLETE and not _abort and not _accept:
            complete_state = self.complete_state
        else:
            complete_state = None

        # Create prompt instance.
        return RenderContext(prompt, code, highlight_regions=highlight_regions,
                        complete_state=complete_state,
                        abort=_abort, accept=_accept,
                        validation_error=self.validation_error)

    @_to_mode(LineMode.NORMAL)
    def history_forward(self):
        if self._working_index < len(self._working_lines) - 1:
            # Go forward in history, and update cursor_position.
            self._working_index += 1
            self.cursor_position = len(self.text)

    @_to_mode(LineMode.NORMAL)
    def history_backward(self):
        if self._working_index > 0:
            # Go back in history, and update cursor_position.
            self._working_index -= 1
            self.cursor_position = len(self.text)

    @_to_mode(LineMode.NORMAL)
    def newline(self):
        self.insert_text('\n')

    def insert_line_above(self, copy_margin=True):
        """
        Insert a new line above the current one.
        """
        if copy_margin:
            insert = self.document.leading_whitespace_in_current_line + '\n'
        else:
            insert = '\n'

        self.cursor_to_start_of_line()
        self.insert_text(insert)
        self.cursor_position -= 1

    def insert_line_below(self, copy_margin=True):
        """
        Insert a new line below the current one.
        """
        if copy_margin:
            insert = '\n' + self.document.leading_whitespace_in_current_line
        else:
            insert = '\n'

        self.cursor_to_end_of_line()
        self.insert_text(insert)

    def insert_text(self, data, overwrite=False, move_cursor=True):
        """
        Insert characters at cursor position.
        """
        if self.mode == LineMode.INCREMENTAL_SEARCH:
            self.isearch_state.isearch_text += data

            if not self.document.has_match_at_current_position(self.isearch_state.isearch_text):
                self.search_next(self.isearch_state.isearch_direction)
        else:
            # In insert/text mode.
            if overwrite:
                # Don't overwrite the newline itself. Just before the line ending, it should act like insert mode.
                overwritten_text = self.text[self.cursor_position:self.cursor_position+len(data)]
                if '\n' in overwritten_text:
                    overwritten_text = overwritten_text[:overwritten_text.find('\n')]

                self.text = self.text[:self.cursor_position] + data + self.text[self.cursor_position+len(overwritten_text):]
            else:
                self.text = self.text[:self.cursor_position] + data + self.text[self.cursor_position:]

            if move_cursor:
                self.cursor_position += len(data)

    def set_clipboard(self, clipboard_data):
        """
        Set data to the clipboard.

        :param clipboard_data: :class:`~.ClipboardData` instance.
        """
        self._clipboard = clipboard_data

    @_to_mode(LineMode.NORMAL)
    def paste_from_clipboard(self, before=False):
        """
        Insert the data from the clipboard.
        """
        if self._clipboard and self._clipboard.text:
            if self._clipboard.type == ClipboardDataType.CHARACTERS:
                if before:
                    self.insert_text(self._clipboard.text)
                else:
                    self.cursor_right()
                    self.insert_text(self._clipboard.text)
                    self.cursor_left()

            elif self._clipboard.type == ClipboardDataType.LINES:
                if before:
                    self.cursor_to_start_of_line()
                    self.insert_text(self._clipboard.text + '\n', move_cursor=False)
                else:
                    self.cursor_to_end_of_line()
                    self.insert_text('\n')
                    self.insert_text(self._clipboard.text, move_cursor=False)

    @_to_mode(LineMode.NORMAL)
    def undo(self):
        if self._undo_stack:
            text, pos = self._undo_stack.pop()

            self.text = text
            self.cursor_position = pos

    @_to_mode(LineMode.NORMAL)
    def abort(self):
        """
        Abort input. (Probably Ctrl-C press)
        """
        render_context = self.get_render_context(_abort=True)
        raise Abort(render_context)

    @_to_mode(LineMode.NORMAL)
    def exit(self):
        """
        Quit command line. (Probably Ctrl-D press.)
        """
        render_context = self.get_render_context(_abort=True)
        raise Exit(render_context)

    @_to_mode(LineMode.NORMAL)
    def return_input(self):
        """
        Return the current line to the `CommandLine.read_input` call.
        """
        code = self.create_code_obj()
        text = self.text

        # Validate first. If not valid, set validation exception.
        try:
            code.validate()
            self.validation_error = None
        except ValidationError as e:
            # Set cursor position (don't allow invalid values.)
            cursor_position = self.document.translate_row_col_to_index(e.line, e.column)
            self.cursor_position = min(max(0, cursor_position), len(self.text))

            self.validation_error = e
            return

        # Save at the tail of the history. (But don't if the last entry the
        # history is already the same.)
        if not len(self._history) or self._history[-1] != text:
            if text:
                self._history.append(text)

        render_context = self.get_render_context(_accept=True)

        self.reset()
        raise ReturnInput(code, render_context)

    @_to_mode(LineMode.NORMAL, LineMode.INCREMENTAL_SEARCH)
    def reverse_search(self):
        """
        Enter i-search mode, or if already entered, go to the previous match.
        """
        direction = IncrementalSearchDirection.BACKWARD

        if self.mode == LineMode.INCREMENTAL_SEARCH:
            self.search_next(direction)
        else:
            self._start_isearch(direction)

    @_to_mode(LineMode.NORMAL, LineMode.INCREMENTAL_SEARCH)
    def forward_search(self):
        """
        Enter i-search mode, or if already entered, go to the following match.
        """
        direction = IncrementalSearchDirection.FORWARD

        if self.mode == LineMode.INCREMENTAL_SEARCH:
            self.search_next(direction)
        else:
            self._start_isearch(direction)

    def _start_isearch(self, direction):
        self.mode = LineMode.INCREMENTAL_SEARCH
        self.isearch_state = _IncrementalSearchState(
                original_cursor_position = self.cursor_position,
                original_working_index = self._working_index)
        self.isearch_state.isearch_direction = direction

    @_to_mode(LineMode.NORMAL, LineMode.INCREMENTAL_SEARCH)
    def search_next(self, direction):
        if not (self.mode == LineMode.INCREMENTAL_SEARCH and self.isearch_state.isearch_text):
            return

        self.isearch_state.isearch_direction = direction

        isearch_text = self.isearch_state.isearch_text

        if direction == IncrementalSearchDirection.BACKWARD:
            # Try find at the current input.
            new_index = self.document.find_backwards(isearch_text)

            if new_index is not None:
                self.cursor_position += new_index
            else:
                # No match, go back in the history.
                for i in range(self._working_index - 1, -1, -1):
                    document = Document(self._working_lines[i], len(self._working_lines[i]))
                    new_index = document.find_backwards(isearch_text)
                    if new_index is not None:
                        self._working_index = i
                        self.cursor_position = len(self._working_lines[i]) + new_index
                        break
        else:
            # Try find at the current input.
            new_index = self.document.find(isearch_text)

            if new_index is not None:
                self.cursor_position += new_index
            else:
                # No match, go forward in the history.
                for i in range(self._working_index + 1, len(self._working_lines)):
                    document = Document(self._working_lines[i], 0)
                    new_index = document.find(isearch_text, include_current_position=True)
                    if new_index is not None:
                        self._working_index = i
                        self.cursor_position = new_index
                        break

    def exit_isearch(self, restore_original_line=False):
        """
        Exit i-search mode.
        """
        if self.mode == LineMode.INCREMENTAL_SEARCH:
            if restore_original_line:
                self._working_index = self.isearch_state.original_working_index
                self.cursor_position = self.isearch_state.original_cursor_position

            self.mode = LineMode.NORMAL

    @_to_mode(LineMode.NORMAL)
    def clear(self):
        """
        Clear renderer screen, usually as a result of Ctrl-L.
        """
        if self.renderer:
            self.renderer.clear()

    @_to_mode(LineMode.NORMAL)
    def open_in_editor(self):
        """ Open code in editor. """
        # Write to temporary file
        descriptor, filename = tempfile.mkstemp()
        os.write(descriptor, self.text.encode('utf-8'))
        os.close(descriptor)

        # Open in editor
        self._open_file_in_editor(filename)

        # Read content again.
        with open(filename, 'rb') as f:
            self.text = f.read().decode('utf-8')
        self.cursor_position = len(self.text)

        # Clean up temp file.
        os.remove(filename)

    def _open_file_in_editor(self, filename):
        """ Call editor executable. """
        # If the 'EDITOR' environment variable has been set, use that one.
        # Otherwise, fall back to the first available editor that we can find.
        editor = os.environ.get('EDITOR')

        editors = [
                editor,

                # Order of preference.
                '/usr/bin/editor',
                '/usr/bin/nano',
                '/usr/bin/pico',
                '/usr/bin/vi',
                '/usr/bin/emacs',
        ]

        for e in editors:
            if e:
                if os.path.exists(e):
                    subprocess.call([e, filename])
                    return
