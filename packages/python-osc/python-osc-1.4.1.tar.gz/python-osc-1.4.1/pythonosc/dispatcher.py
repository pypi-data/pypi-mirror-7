"""Class that maps OSC addresses to handlers."""
import collections
import logging
import re

Handler = collections.namedtuple(
    typename='Handler',
    field_names=('callback', 'args'))


class Dispatcher(object):
  """Register addresses to handlers and can match vice-versa."""

  def __init__(self):
    self._map = {}
    self._default_handler = None

  def map(self, address, handler, *args):
    """Map a given address to a handler.

    Args:
      - address: An explicit endpoint.
      - handler: A function that will be run when the address matches with
                 the OscMessage passed as parameter.
      - args: Any additional arguments that will be always passed to the
              handlers after the osc messages arguments if any.
    """
    # TODO: Check if we need to use a multimap instead, spec is a bit fuzzy
    # about it...
    self._map[address] = Handler(handler, list(args))

  def handlers_for_address(self, address_pattern):
    """Return a tuple of Handler namedtuple matching the given OSC pattern."""
    # First convert the address_pattern into a matchable regexp.
    # '?' in the OSC Address Pattern matches any single character.
    # Let's consider numbers and _ "characters" too here, it's not said
    # explicitly in the specification but it sounds good.
    address_pattern = re.escape(address_pattern)
    pattern = address_pattern.replace('\\?', '\\w?')
    # '*' in the OSC Address Pattern matches any sequence of zero or more
    # characters.
    pattern = pattern.replace('\\*', '[\w|\+]*')
    # The rest of the syntax in the specification is like the re module so
    # we're fine.
    pattern = pattern + '$'
    pattern = re.compile(pattern)
    matched = [
        handler for addr, handler in self._map.items() if pattern.match(addr)]
    if not matched and self._default_handler:
      matched.append(Handler(self._default_handler, []))
      logging.debug('No handler matched but default handler present, added it.')
    return matched

  def set_default_handler(self, handler):
    """Sets the default handler.

    Must be a function with the same constaints as with the self.map method
    or None to unset the default handler.
    """
    self._default_handler = handler
