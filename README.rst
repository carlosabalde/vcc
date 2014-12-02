**Varnish Custom Counters** (VCC) allows aggregation of custom log entries extracted from `Varnish shared memory log (VSL) <https://www.varnish-cache.org/docs/trunk/reference/vsm.html>`_.

VCC is a simple PoC Python script (Python >= 2.6 & < 3 required) showing how to access to VSL data (only Varnish 3.x is supported at the moment) using libvarnishapi.so and `ctypes <https://docs.python.org/2/library/ctypes.html>`_. Fetched items are locally aggregated using some user selected operator (currently count, `hll <http://en.wikipedia.org/wiki/HyperLogLog>`_, min, max, avg, last & first are supported) and periodically rendered in an ugly `curses <https://docs.python.org/2/library/curses.html>`_ UI.

Remember this is just a PoC. Don't expect updates or fixes here. Anyway, comments, improvements and contributions are welcome!

VCC is sponsored by `Allenta Consulting <http://www.allenta.com>`_, the Varnish Software `integration partner for Spain and Portugal <https://www.varnish-software.com/partner/allenta-consulting>`_.

Example
=======

The following VCL::

    sub vcl_deliver {
        std.log("vcc:Sample counter #1 (COUNT):count:");
        std.log("vcc:Sample counter #2 (HLL):hll,5,234:" + req.http.X-Whatever);
        std.log("vcc:Sample counter #3 (MIN):min:" + req.http.X-Whatever);
        std.log("vcc:Sample counter #4 (MAX):max:" + req.http.X-Whatever);
        std.log("vcc:Sample counter #5 (AVG):avg:" + req.http.X-Whatever);
        std.log("vcc:Sample counter #6 (FIRST):first:" + req.http.X-Whatever);
        std.log("vcc:Sample counter #7 (LAST):last:" + req.http.X-Whatever);
    }

After processing some requests you will get something like:

.. image:: https://github.com/carlosabalde/vcc/raw/master/extras/screenshot.png

QuickStart
==========

1. Install VCC and all its dependencies::

    ~$ sudo pip install VCC

2. Add some logging statement to your VCL. Format of logged messages is::

    vcc:<counter name>:<aggregation function + configuration>:<value>

   Only the ``hll`` aggregation function requires configuration parameters: ``k`` (integer value in the range [2, 16]) and ``seed`` (integer value). Please, refer to https://github.com/ascv/HyperLogLog for extra information.

3. Execute VCC while Varnish is processing requests (use ``--help`` for extra options)::

    ~$ vcc --version 3 --nwindows=10 --wsize=60
