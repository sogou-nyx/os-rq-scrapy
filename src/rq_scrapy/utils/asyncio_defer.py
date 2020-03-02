import asyncio

from twisted.internet import defer


def as_future(d):
    return d.asFuture(asyncio.get_event_loop())


def as_deferred(f):
    return defer.Deferred.fromFuture(asyncio.ensure_future(f))
