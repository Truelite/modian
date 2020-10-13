# Build directories

`live-wrapper` needs a *work* directory for the various intermediate build
results, and can use a *cache* directory to preserve previous intermediate
results to speed up subsequent runs during development.

By default, the work directory is a temporary directory created using the
Python standard library functions for doing so. On Debian systems, this
typically means that it is created under `/tmp`.

If you want `live-wrapper` to use a temporary work directory but not create it
under `/tmp`, you can change the path that Python will use to create
directories in by using the ``TMP`` environment variable, for example:

```
sudo TMP=/other/path lwr --blah --blah
```

You can otherwise provide a custom work directory using the `--work-dir`
option. `live-wrapper` will remove an existing custom work directory on startup
unless you use `--retry`, but will *not* delete it at the end so you can inspect
its contents.

If you want to use the cache directory feature, you can specify its location
with the `--cache-dir` command line argument.
