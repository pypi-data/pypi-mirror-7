pesky-defaults
==============

pesky-defaults is a small library for querying platform, distribution,
and package defaults using a uniform interface.  

The following default keys are made accessible and their values set
according to the detected platform:

  * PREFIX
  * BIN_DIR
  * SBIN_DIR
  * LIB_DIR
  * LIBEXEC_DIR
  * SYSCONF_DIR
  * LOCALSTATE_DIR
  * RUN_DIR
  * DATA_DIR

A setuptools command is also provided ('pesky_default') so that project
defaults can be specified, potentially overriding platform or distribution
defaults.


Basic Usage
-----------

To use pesky-defaults, simply instantiate a new Defaults object and invoke
the query methods 'get' or 'getorelse':

::

    from pesky.defaults import Defaults
    defaults = Defaults()
    print defaults.get('PREFIX')    # displays /usr on a linux platform

The Defaults class implements the collections.Mapping interface, so you can
use the familiar mapping methods as well:

::

    print defaults['LIB_DIR']       # displays /usr/lib on a linux platform


Project Defaults
----------------

If you specify a project name when instantiating the Defaults object, then
all defaults from the project metadata will be loaded as well:

::

    from pesky.defaults import Defaults
    defaults = Defaults('my-project')   # the project name as given to setuptools

This is all well and good, but how do the project defaults get set in the first
place?  This is where the 'pesky_default' setuptools command comes into play.  By
invoking the 'pesky_default' setuptools command, the .egg-info file called
'pesky_defaults.json' is manipulated.  Once all project defaults are set as
desired, the 'install' setuptools command can be invoked, which will perform the
standard setuptools install routine and copy all egg-info files into place. For
example:

::

    $ cd my-project/
    $ python ./setup.py pesky_default --command set --key foo --value bar
    $ python ./setup.py install

This snippet enters the source tree of the fictional project 'my-project', adds
the project default 'foo', giving it the value 'bar', then installs the project
(with the updated project defaults).  The application code can then retrieve the
'foo' default:

::

    from pesky.defaults import Defaults
    defaults = Defaults('my-project')   # the project name as given to setuptools
    print defaults.get('foo')           # displays bar


