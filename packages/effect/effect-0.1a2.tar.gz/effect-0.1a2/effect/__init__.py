"""
A system for helping you separate your IO and state-manipulation code
(hereafter referred to as "effects") from everything else, thus allowing
the majority of your code to be trivially testable and composable (that is,
have the general benefits of purely functional code).

Keywords: monad, IO, stateless.

The core behavior is as follows:
- Effectful operations should be represented as plain Python objects which
  we will call the *intent* of an effect. These objects should be wrapped
  in an instance of :class:`Effect`.
- Intent objects can implement a 'perform_effect' method to actually perform
  the effect. This method should _not_ be called directly.
- In most cases where you'd perform effects in your code, you should instead
  return an Effect wrapping the effect intent.
- To represent work to be done *after* an effect, use Effect.on_success,
  .on_error, etc.
- Near the top level of your code, invoke Effect.perform on the Effect you
  have produced. This will invoke the effect-performing handler specific to
  the wrapped object, and invoke callbacks as necessary.
- If the callbacks return another instance of Effect, that Effect will be
  performed before continuing back down the callback chain.

On top of the implemented behaviors, there are some conventions that these
behaviors synergize with:

- Don't perform actual IO or manipulate state in functions that return an
  Effect. This kinda goes without saying. However, there are a few cases
  where you may decide to compromise:
  - most commonly, logging.
  - generation of random numbers.
- Effect-wrapped objects should be *inert* and *transparent*. That is, they
  should be unchanging data structures that fully describe the behavior to be
  performed with public members. This serves two purposes:
  - First, and most importantly, it makes unit-testing your code trivial.
    The tests will simply invoke the function, inspect the Effect-wrapped
    object for correctness, and manually resolve the effect to execute any
    callbacks in order to test the post-Effect behavior. No more need to mock
    out effects in your unit tests!
  - This allows the effect-code to be *small* and *replaceable*. Using these
    conventions, it's trivial to switch out the implementation of e.g. your
    HTTP client, using a blocking or non-blocking network library, or
    configure a threading policy. This is only possible if effect intents
    expose everything necessary via a public API to alternative
    implementation.
- To spell it out clearly: do not call Effect.perform() on Effects produced by
  your code under test: there's no point. Just grab the 'intent'
  attribute and look at its public attributes to determine if your code
  is producing the correct kind of effect intents. Separate unit tests for
  your effect *handlers* are the only tests that need concern themselves with
  true effects.
- When testing, use the utilities in the effect.testing module: they will help
  a lot.

Twisted's Deferreds are supported directly; any effect handler that returns
a Deferred will seamlessly integrate with on_success, on_error etc callbacks.

Support for AsyncIO tasks, and other callback-oriented frameworks, is to be
done, but should be trivial.

UNFORTUNATE:

- In general, callbacks should not need to care about the implementation
  of the effect handlers. However, currently error conditions are passed to
  error handlers in an implementation-bound way: when Deferreds are involved,
  Failures are passed, whereas when synchronous exceptions are raised, a
  sys.exc_info() tuple is passed. This should be fixed somehow, maybe by
  relying on a split-out version of Twisted's Failures.

"""

from __future__ import print_function

import sys

import six


class NoEffectHandlerError(Exception):
    """
    No Effect handler could be found for the given Effect-wrapped object.
    """


def _iter_conses(seq):
    """
    Generate (head, tail) tuples so you can iterate in a way that feels like
    a typical recursive function over a linked list.
    """
    for i in range(len(seq)):
        yield seq[i], seq[i + 1:]


def default_effect_perform(intent):
    """
    If the intent has a 'perform_effect' method, invoke it with this
    function as an argument. Otherwise raise NoEffectHandlerError.
    """
    if hasattr(intent, 'perform_effect'):
        return intent.perform_effect(default_effect_perform)
    raise NoEffectHandlerError(intent)


class Effect(object):
    """
    Wrap an object that describes how to perform some effect (called an
    "effect intent"), and offer a way to actually perform that effect.

    (You're an object-oriented programmer.
     You probably want to subclass this.
     Don't.)
    """
    def __init__(self, intent):
        """
        :param intent: An object that describes an effect to be
            performed. Optionally has a perform_effect(dispatcher) method.
        """
        self.intent = intent
        self.callbacks = []

    @classmethod
    def with_callbacks(klass, intent, callbacks):
        eff = klass(intent)
        eff.callbacks = callbacks
        return eff

    def perform(self, dispatcher=default_effect_perform):
        """
        Perform an effect by running the dispatcher, and then passing the
        result through all the callbacks.

        If the dispatcher returns another :class:`Effect` instance, that
        effect will be performed immediately before returning.

        :param dispatcher: A function that accepts an intent and performs it.
            This must raise NoEffectHandlerError if no strategy for performing
            the intent can be found.
        :raise NoEffectHandlerError: When no handler was found for the effect
            intent.
        """
        return self._dispatch_callback_chain(
            [(dispatcher, None)] + self.callbacks, self.intent, dispatcher)

    def _dispatch_callback_chain(self, chain, init_arg, dispatcher,
                                 is_error=False):
        """
        Run a series of callbacks in sequence, passing the result of each
        callback as an argument to the next one.

        If any callback returns an effect, that effect will be recursively
        performed.

        If any callback returns a Deferred, the remaining callbacks will be
        run when that Deferred's result is available.
        """
        result = init_arg
        for (success, error), remaining in _iter_conses(chain):
            cb = success if not is_error else error
            if cb is None:
                continue
            is_error, result = self._dispatch_callback(cb, result)
            if not is_error:
                is_error, result = self._dispatch_callback(
                    lambda result: self._maybe_recurse_effect(result,
                                                              dispatcher),
                    result)

            # Not happy about this Twisted knowledge being in Effect...
            if hasattr(result, 'addCallbacks'):
                # short circuit all the rest of the callbacks; they become
                # callbacks on the Deferred instead of the effect.
                return self._chain_deferred(result, remaining, dispatcher)
        if is_error:
            six.reraise(*result)
        return result

    def _chain_deferred(self, deferred, callbacks, dispatcher):
        """Attach the remaining callbacks to the Deferred."""
        deferred.addCallback(self._maybe_recurse_effect, dispatcher)
        return deferred.addCallbacks(
            lambda r: self._dispatch_callback_chain(callbacks, r, dispatcher),
            lambda f: self._dispatch_callback_chain(callbacks, f, dispatcher,
                                                    is_error=True))

    def _maybe_recurse_effect(self, result, dispatcher):
        """If the result is an effect, recursively perform it."""
        if type(result) is Effect:
            return result.perform(dispatcher)
        return result

    def _dispatch_callback(self, callback, argument):
        """
        Invoke a function and return a two-tuple of (bool success, result).
        Result will be an exc_info if the function raised an exception.
        """
        try:
            return (False, callback(argument))
        except:
            return (True, sys.exc_info())

    def on_success(self, callback):
        """
        Return a new Effect that will invoke the associated callback when this
        Effect completes succesfully.
        """
        return self.on(success=callback, error=None)

    def on_error(self, callback):
        """
        Return a new Effect that will invoke the associated callback when this
        Effect fails.

        The callback will be invoked with the sys.exc_info() exception tuple
        as its only argument.
        """
        return self.on(success=None, error=callback)

    def after(self, callback):
        """
        Return a new Effect that will invoke the associated callback when this
        Effect completes, whether successfully or in error.
        """
        return self.on(success=callback, error=callback)

    def on(self, success, error):
        """
        Return a new Effect that will invoke either the success or error
        callbacks provided based on whether this Effect completes sucessfully
        or in error.
        """
        return Effect.with_callbacks(self.intent,
                                     self.callbacks + [(success, error)])

    def __repr__(self):
        return "Effect.with_callbacks(%r, %s)" % (self.intent, self.callbacks)

    def serialize(self):
        """
        A simple debugging tool that serializes a tree of effects into basic
        Python data structures that are useful for pretty-printing.

        If the effect intent has a "serialize" method, it will be invoked to
        represent itself in the resulting structure.
        """
        if hasattr(self.intent, 'serialize'):
            intent = self.intent.serialize()
        else:
            intent = self.intent
        return {"type": type(self), "intent": intent,
                "callbacks": self.callbacks}


class ParallelEffects(object):
    """
    An effect intent that asks for a number of effects to be run in parallel,
    and for their results to be gathered up into a sequence.

    The default implementation of this effect relies on Twisted's Deferreds.
    An alternative implementation can run the child effects in threads, for
    example. Of course, the implementation strategy for this effect will need
    to cooperate with the effects being parallelized -- there's not much use
    running a Deferred-returning effect in a thread.
    """
    def __init__(self, effects):
        self.effects = effects

    def __repr__(self):
        return "ParallelEffects(%r)" % (self.effects,)

    def serialize(self):
        return {"type": type(self),
                "effects": [e.serialize() for e in self.effects]}

    def perform_effect(self, dispatcher):
        from twisted.internet.defer import gatherResults, maybeDeferred
        return gatherResults(
            [maybeDeferred(e.perform, dispatcher) for e in self.effects])


def parallel(effects):
    """
    Given multiple Effects, return one Effect that represents the aggregate of
    all of their effects.
    The result of the aggregate Effect will be a list of their results, in
    the same order as the input to this function.
    """
    return Effect(ParallelEffects(list(effects)))
