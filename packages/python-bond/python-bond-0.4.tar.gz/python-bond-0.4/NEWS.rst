python-bond 0.4
---------------

* Serialization exceptions generating from exported functions now correctly
  unwind the remote stack.
* An exception with exported functions returning no values was fixed.
* The size of the serialization buffers was previously limited to 4k; it's now
  bound to the available memory.
* ``bond.interact()`` now can accept multi-line blocks by using a trailing
  backslash at the end of the line.
* Performance was optimized.


python-bond 0.3
---------------

* Local exceptions are now forwarded remotely for exported functions.
* Excluding Python, exceptions are no longer serialized, but are instead
  propagated using their originating error message. See the ``trans_except``
  keyword argument in constructors that allows to tune this behavior.
* The spawned interpreter now uses a copy of the current environment.
* PHP now triggers an exception when attempting to redefine a function.
* JavaScript is now supported through Node.js.


python-bond 0.2
---------------

* Serialization errors are now intercepted by default and generate a local
  exception of type ``bond.SerializationException``.
* PHP can now "call" any callable statement.
* ``eval_block()`` no longer returns the value of the last statement. This
  avoids confusion with Perl code blocks returning unserializable references.
* Standard error is now also redirected.
