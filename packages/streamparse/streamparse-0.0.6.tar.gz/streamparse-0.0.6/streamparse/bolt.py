"""Base Bolt classes."""
from __future__ import print_function

from base import Component
from util import read_handshake, read_tuple, send_message, json, _stdout


_ANCHOR_TUPLE = None


class Bolt(Component):
    """The base class for all streamparse bolts. For more information on bolts,
    consult Storm's `Concepts documentation <http://storm.incubator.apache.org/documentation/Concepts.html>`_.
    """

    def initialize(self, storm_conf, context):
        """Called immediately after the initial handshake with Storm and before
        the main run loop. A good place to initialize connections to data
        sources.

        :param storm_conf: a ``dict`` containing the Storm configuration for
        this spout.  This is the configuration provided to the topology, merged
        in with cluster configuration on the worker node.
        :param context: a ``dict`` containing information about the component's
        place within the topology such as: task IDs, inputs, outputs etc.
        """
        pass

    def process(self, tup):
        """Process a single tuple :class:`base.Tuple` of input, should be
        overridden by subclasses.  :class:`base.Tuple` objects contain metadata
        about which component, stream and task it came from.  The actual values
        of the tuple can be accessed by calling `tup.values`.

        :param tup: a ``Tuple`` object.
        """
        raise NotImplementedError()

    def emit(self, tup, stream=None, anchors=[], direct_task=None):
        """Emit a new tuple to a stream.

        :param tup: a ``list`` representing the tuple to send to Storm, should
        contain only JSON-serializable data.
        :param stream: a ``str`` indicating the ID of the stream to emit this
        tuple to. Specify ``None`` to emit to default stream.
        :param anchors: a ``list`` of IDs of the tuples tuple should be
        anchored to.
        :param direct_task: an ``int`` which indicates the task to send the
        tuple to.
        """
        if not isinstance(tup, list):
            raise TypeError('All tuples must be lists, received {!r} instead'
                            .format(type(tup)))
        if _ANCHOR_TUPLE is not None:
            anchors = [_ANCHOR_TUPLE]
        msg = {'command': 'emit', 'tuple': tup}
        if stream is not None:
            msg['stream'] = stream
        msg['anchors'] = [x.id for x in anchors]
        if direct_task is not None:
            msg['task'] = direct_task

        send_message(msg)

    def emit_many(self, tuples, stream=None, anchors=[], direct_task=None):
        """A more efficient way to send many tuples, dumps out all tuples to
        STDOUT instead of writing one at a time.

        :param tuples: an iterable of ``list``s representing the tuples to send
        to Storm. All tuples should contain only JSON-serializable data.
        :param stream: a ``str`` indicating the ID of the steram to emit these
        tuples to. Specify ``None`` to emit to default stream.
        :param anchors: a `` list`` of IDs the tuples these tuples should be
        anchored to.
        :param direct_task: an ``int`` which indicates the task to send the
        tuple to.
        """
        if _ANCHOR_TUPLE is not None:
            anchors = [_ANCHOR_TUPLE]
        msg = {
            'command': 'emit',
            'anchors': [a.id for a in anchors],
        }
        if stream is not None:
            msg['stream'] = stream
        if direct_task is not None:
            msg['task'] = direct_task

        lines = []
        for tup in tuples:
            msg['tuple'] = tup
            lines.append(json.dumps(msg))
            lines.append('end')
        print('\n'.join(lines), file=_stdout)

    def ack(self, tup):
        """Indicate that processing of a tuple has succeeded.

        :param tup: a :class:`base.Tuple` object.
        """
        send_message({'command': 'ack', 'id': tup.id})

    def fail(self, tup):
        """Indicate that processing of a tuple has failed.

        :param tup: a :class:`base.Tuple` object.
        """
        send_message({'command': 'fail', 'id': tup.id})

    def run(self):
        """Main run loop for all bolts. Performs initial handshake with Storm
        and reads tuples handing them off to subclasses.  Any exceptions are
        caught and logged back to Storm prior to the Python process exits.
        Subclasses should not override this method.
        """
        storm_conf, context = read_handshake()
        tup = None
        try:
            self.initialize(storm_conf, context)
            while True:
                tup = read_tuple()
                self.process(tup)
        except Exception as e:
            self.raise_exception(e, tup)


class BasicBolt(Bolt):
    """A bolt implementation that automatically acknowledges all tuples after
    `self.process(tup)` completes."""

    def run(self):
        global _ANCHOR_TUPLE
        storm_conf, context = read_handshake()
        tup = None
        try:
            self.initialize(storm_conf, context)
            while True:
                tup = read_tuple()
                _ANCHOR_TUPLE = tup
                self.process(tup)
                self.ack(tup)
        except Exception as e:
            self.raise_exception(e, tup)
