# Hairball

Hairball is a plugin-able framework useful for static analysis of Scratch
projects.

The paper and presentation slides for Hairball can be found at:
http://cs.ucsb.edu/~bboe/p/cv#sigcse13

A Hairball demo web service is running and available at:
http://hairball.herokuapp.com


## Hairball installation

With a proper python environment (one which has `pip` available), installation
is as simple as `pip install hairball`. `easy_install` can also be used via
`easy_install hairball`.

To install from source, first checkout this project and then navigate your
command-line interface to the outer hairball directory that contains
`setup.py`. Then run `python setup.py install`.

## Running Hairball

Once installed, to see how to use hairball run `hairball --help`. That will
produce output similar to the following:

```
Usage: hairball -p PLUGIN_NAME [options] PATH...

PATH can be either the path to a scratch file, or a directory containing
scratch files. Multiple PATH arguments can be provided.

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -d DIR, --plugin-dir=DIR
                        Specify the path to a directory containing plugins.
                        Plugins in this directory take precedence over
                        similarly named plugins included with Hairball.
  -p PLUGIN, --plugin=PLUGIN
                        Use the named plugin to perform analysis. This option
                        can be provided multiple times.
  -k KURT_PLUGIN, --kurt-plugin=KURT_PLUGIN
                        Provide either a python import path (e.g, kelp.octopi)
                        to a package/module, or the path to a python file,
                        which will be loaded as a Kurt plugin. This option can
                        be provided multiple times.
```

## Available Plugins

Below are a list of available plugins that can be used as the `-p PLUGIN_NAME`
option:

* blocks.BlockCounts
* blocks.DeadCode
* checks.Animation (not fully tested)
* checks.BroadcastReceive
* checks.SaySoundSync (not fully tested)
* duplicate.DuplicateScripts
* initialization.AttributeInitialization
* initialization.VariableInitialization (not fully tested)

Note: The output for each plugin is not yet completely standardized. Please
feel free to file any issues or make improvements and send pull requests.

## Caching Support

The python Kurt package unfortunately is pretty slow to parse Scratch 1.4 (and
similar) files. To remedy this situation, Hairball has built-in support for
caching a serialized version of the Kurt object. On subsequent passes through
the same data you should notice a TREMENDOUS speed improvement.

__Note__: At the moment the cache is unbounded, so keep an eye on your disk
space. The cache location can be discovered by running:

    python -c "import appdirs; print appdirs.user_cache_dir('Hairball', 'bboe')"
