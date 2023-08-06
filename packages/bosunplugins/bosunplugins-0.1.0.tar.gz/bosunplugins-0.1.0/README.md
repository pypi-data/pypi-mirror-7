# Bosun Plugins

Guidelines for making plugins

- Don't alter the concurrency model.

    If you don't know what this means, then you can skip this whole bullet.

    I/O is patched with gevent *most* of the time (FTP handlers are currently an exception).
    If you some special concurrent processing, use gevent's Pool or Group, if possible.
- Keep to builtin or standard packages.

    This helps to keep the total number of installed packages down, and, in turn, the number
    of packages that are loaded into memory.

    Recommended packages:

    - JSON: builtin `json`
    - YAML: `pyyaml`
    - XML: `xmltodict`
    - HTTP: builtin `urllib`, builtin `urllib2`, and `requests`
- Use `YourDeviceSubclass.test_subclass()` to check your work.

    It's strongly recommended that your subclass pass this method. It performs basic checks
    and can alert you if you subclass seems to be doing something strange or is missing
    anything. This doesn't check your implementation, but instead checks that you're
    adhering to the contract set out by being a Device subclass.

[See the full documentation](docs/index.rst)
