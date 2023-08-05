import asyncio
from . import spec


class Queue(object):
    """
    A queue is a collection of messages, which new messages can be delivered to via an exchange,
    and messages can be consumed from by an application.

    Attributes:
        queue.name: the name of the queue
        queue.durable: if True, the queue will be re-created when the broker restarts
        queue.exclusive: if True, the queue is only accessible over one channel
        queue.auto_delete: if True, the queue will be deleted when its last consumer is removed

    Methods:
        queue.bind(exchange, routing_key): Bind a queue to an exchange. This method is a coroutine.
    """
    def __init__(self, consumers, synchroniser, loop, sender, name, durable, exclusive, auto_delete):
        self.consumers = consumers
        self.synchroniser = synchroniser
        self.loop = loop
        self.sender = sender
        self.name = name
        self.durable = durable
        self.exclusive = exclusive
        self.auto_delete = auto_delete
        self.deleted = False

    @asyncio.coroutine
    def bind(self, exchange, routing_key):
        """
        Bind a queue to an exchange, with the supplied routing key.
        This action 'subscribes' the queue to the routing key; the precise meaning of this
        varies with the exchange type.
        This method is a coroutine.

        Arguments:
            exchange: the exchange to bind to
            routing_key: the routing key under which to bind

        Return value:
            The newly created binding object
        """
        with (yield from self.synchroniser.sync(spec.QueueBindOK)) as fut:
            self.sender.send_QueueBind(self.name, exchange.name, routing_key)
            yield from fut
            return QueueBinding(self, exchange)

    @asyncio.coroutine
    def consume(self, callback, *, no_local=False, no_ack=False, exclusive=False):
        """
        Start a consumer on the queue. Messages will be delivered asynchronously to the consumer.
        This method is a coroutine.

        Arguments:
            callback: a callback to be called when a message is delivered.
                      The callback must accept a single argument (an instance of asynqp.Message).
            no_local: If true, the server will not deliver messages that were
                      published by this connection. Default: False
            no_ack: If true, messages delivered to the consumer don't require acknowledgement.
                    Default: False
            exclusive: If true, only this consumer can access the queue. Default: False

        Return value:
            The newly created consumer object.
        """
        with (yield from self.synchroniser.sync(spec.BasicConsumeOK)) as fut:
            self.sender.send_BasicConsume(self.name, no_local, no_ack, exclusive)
            tag = yield from fut
            consumer = Consumer(tag, callback)
            self.consumers.add_consumer(consumer)
            return consumer

    @asyncio.coroutine
    def get(self, *, no_ack=False):
        """
        Synchronously get a message from the queue.
        This method is a coroutine.

        Arguments:
            no_ack: if True, the broker does not require acknowledgement of receipt of the message.
                    default: False

        Return value:
            an instance of asynqp.Message, or None if there were no messages on the queue.
        """
        with (yield from self.synchroniser.sync(spec.BasicGetOK, spec.BasicGetEmpty)) as fut:
            self.sender.send_BasicGet(self.name, no_ack)
            result = yield from fut
            return result

    @asyncio.coroutine
    def delete(self, *, if_unused=True, if_empty=True):
        """
        Delete the queue.
        This method is a coroutine.

        Arguments:
            if_unused: If true, the queue will only be deleted
                       if it has no consumers. Default: True
            if_empty: If true, the queue will only be deleted if
                      it has no unacknowledged messages. Default: True
        """
        with (yield from self.synchroniser.sync(spec.QueueDeleteOK)) as fut:
            self.sender.send_QueueDelete(self.name, if_unused, if_empty)
            yield from fut
            self.deleted = True


class QueueBinding(object):
    def __init__(self, queue, exchange):
        self.queue = queue
        self.exchange = exchange


class Consumers(object):
    def __init__(self, loop):
        self.loop = loop
        self.consumers = {}

    def add_consumer(self, consumer):
        self.consumers[consumer.tag] = consumer

    def deliver(self, tag, msg):
        self.loop.call_soon(self.consumers[tag].deliver, msg)


class Consumer(object):
    def __init__(self, tag, callback):
        self.tag = tag
        self.callback = callback

    def deliver(self, msg):
        self.callback(msg)
