import asyncio


class ScriptingCommandsMixin:
    """Set commands mixin.

    For commands details see: http://redis.io/commands#scripting
    """

    @asyncio.coroutine
    def eval(self, script, keys=[], args=[]):
        """Execute a Lua script server side.

        :raises TypeError: if script is None
        :raises TypeError: if keys or args contain None
        """
        if script is None:
            raise TypeError("script argument must not be None")
        if None in set(keys):
            raise TypeError("keys must not contain None")
        if None in set(args):
            raise TypeError("args must not contain None")
        return (yield from self._conn.execute(
            b'EVAL', script, len(keys), *(keys + args)))

    @asyncio.coroutine
    def evalsha(self, digest, keys=[], args=[]):
        """Execute a Lua script server side by its SHA1 digest.

        :raises TypeError: if digest is None
        :raises TypeError: if keys or args contain None
        """
        if digest is None:
            raise TypeError("digest must not be None")
        if None in set(keys):
            raise TypeError("keys list must not contain None")
        if None in set(args):
            raise TypeError("args list must not contain None")
        return (yield from self._conn.execute(
            b'EVALSHA', digest, len(keys), *(keys + args)))

    @asyncio.coroutine
    def script_exists(self, digest, *digests):
        """Check existence of scripts in the script cache.

        :raises TypeError: if None passed in arguments
        """
        if digest is None:
            raise TypeError("digest argument must not be None")
        if None in set(digests):
            raise TypeError("digests must not contain None")
        return (yield from self._conn.execute(
            b'SCRIPT', b'EXISTS', digest, *digests))

    @asyncio.coroutine
    def script_kill(self):
        """Kill the script currently in execution."""
        res = yield from self._conn.execute(b'SCRIPT', b'KILL')
        return res == b'OK'

    @asyncio.coroutine
    def script_flush(self):
        """Remove all the scripts from the script cache."""
        res = yield from self._conn.execute(b"SCRIPT",  b"FLUSH")
        return res == b'OK'

    @asyncio.coroutine
    def script_load(self, script):
        """Load the specified Lua script into the script cache."""
        return (yield from self._conn.execute(b"SCRIPT",  b"LOAD", script))
