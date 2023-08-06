#General

Simplelog tries to get out of your way and just provide a simple logger for you programming needs.
Out of the box, simplelog gives you a comprehensive logger with sane defaults.
Within in the box, simplelog comes with a powerful set of hooks and configurations that make it possible to extend it to cover all your logging needs.

#Quick Start

```
# main.py
from simplelog import log
log('hello world') # [2014-06-01T08:00:00Z][INFO][app.main.py]: hello world
```

So what did the code do? It created the default instance of the simplelog with the name: 'app.module'.
`log` takes a message and an optional level `DEBUG|INFO|WARN|ERROR|FATAL` which defaults to `INFO`.
By default, the output format is [DATE_IN_ISO8601][LOG_LEVEL][MODULE_NAME]: MSG.
simplelog prints messages to STDOUT by default.

More involved example

```
from simplelog import Simplelog

logger = new SimpleLog()
logger.debug("foo")
```

---

#Methods

    log(msg, level=INFO)
        Log message at a particular level

[Shortcuts]

    debug
    info
    warn
    error
    fatal

#Classes

class Simplelog(name, level, ...)

    setLevel(lvl)
        Sets the log level for Simplelog and all handlers attached to simplelog

#Decorators

    dump_func
        Dump parameters passed in and out of function to simplelog

