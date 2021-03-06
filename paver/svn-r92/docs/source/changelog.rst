.. _changelog:

Paver Changelog
===============

(unreleased)
------------

* FIXED A command that outputs to stderr containing formatting directives (%s) or something that looks like one would cause an error. Thanks to disturbyte for the patch.

1.0.1 (May 4, 2009)
-------------------

This release was made possible by Adam Lowry who helped improve the code and reviewed
committed many of the patches.

* Fixed sending nonpositional arguments first with consume_args (issue #31).
* Fixed use of setuputils without defining options.setup (issue #24).
* Python 2.4 compatibility fixes (issue #28)
* sh() failures are logged to stderr.
* sh() accepts a cwd keyword argument (issue #29).
* virtualenv bootstrap generation accepts no_site_packages, unzip_setuptools,
  and destination directory arguments in options.
* Distutils config files were being ignored (issue #36) (thanks to Matthew Scott for the patch)
* The exit code was 0 whenever the first task passes, even if later tasks fail (issue #35) (thanks to Matt for the patch)
* Tasks can take normal keyword arguments (issue #33) (thanks to Chris Burroughs for the patch with test!)

1.0 (March 22, 2009)
--------------------
* If there is a task called "default", it is run if Paver is run with no
  tasks listed on the command line.
* The auto task is run, even if no tasks are specified on the command line.
* distutils' log output is now routed through Paver's logging functions, 
  which means that the output is now displayed once more (and is controlled 
  via Paver's command line arguments.)
* The paver.setuputils.setup function will automatically call 
  install_distutils_tasks. This makes it a very convenient way to upgrade 
  from distutils/setuptools to Paver.
* Nicer looking error when you run Paver with an unknown task name.
* fix the md5 deprecation warning in paver.path for real (forgot to delete the
  offending import). Also fixed an import loop when you try to import 
  paver.path.
* Improved docs for 1.0
* Paver now requires Sphinx 0.6 for the docs. In Paver's conf.py for Sphinx,
  there is an autodoc Documenter for handling Paver Tasks properly.

1.0b1 (March 13, 2009)
----------------------
* added call_task to environment and paver.easy, so it should be easy to call
  distutils tasks, for example. (Normally, with Paver 1.0, you just call Paver
  tasks like normal functions.)
* added setup() function to paver.setuputils that is a shortcut for 
  setting options in options.setup. This means that you switch from
  distutils to Paver just by renaming the file and changing the
  import.
* the -h command line argument and "help" task have been unified. You'll
  get the same output regardless of which one you use.
* the auto task is no longer called when you run the help task (issue #21).
  As part of this, a new "no_auto" decorator has been created so that any
  task can be marked as not requiring the auto behavior.
* consume_args and PavementError are now included in paver.easy (thanks to
  Marc Sibson)
* more methods in paver.path now check for existence or lack thereof
  and won't fail as a result. (mkdir and makedirs both check that the
  directory does not exist, rmdir and rmtree check to be sure that
  it does.) This is because the goal is ultimately to create or remove
  something... paver just makes sure that it either exists or doesn't.
* fix md5 deprecation warning in paver.path (issue #22)

1.0a4 (March 6, 2009)
---------------------
* call_pavement would raise an exception if the pavement being called is 
  in the current directory
* the new paver.path25 module was missing from the paver-minilib.zip

1.0a3 (March 6, 2009)
---------------------
* Added automatic running of "auto" task. If there's a task with the name "auto",
  it is run automatically. Using this mechanism, you can write code that sets up
  the options any way you wish, and without using globals at all (because the
  auto task can be given options as a parameter).
* When generating egg_info running "paver", the full path to the Paver script
  was getting included in egg-info/SOURCES.txt. This causes installation problems
  on Windows, at the very least. Paver will now instead place the pavement
  that is being run in there. This likely has the beneficial side effect of
  not requiring a MANIFEST.in file just to include the pavement.
* the options help provided via the cmdopts decorator now appears
* pavements can now refer to __file__ to get their own filename. You can also
  just declare pavement_file as an argument to your task function, if
  you wish.
* call_pavement now switches directories to the location of the pavement and
  then switches back when returning
* if you try to run a function as a task, you'll now get a more appropriate
  and descriptive BuildFailure, rather than an AttributeError
* paver can now again run tasks even when there is no pavement present.
  any task accessible via paver.easy (which now also includes misctasks)
  will work.
* added the pushd context manager (Python 2.5+). This will switch into another
  directory on the way in and then change back to the old directory on 
  the way out. Suggested by Steve Howe, with the additional suggestion from
  Juergen Hermann to return the old directory::
  
        with pushd('newdirectory') as olddirectory:
            ...do something...

1.0a2 (February 26, 2009)
-------------------------
* The bug that caused 1.0a1 to be recalled (distutils command options)
  has been fixed thanks to Greg Thornton.
* If you provide an invalid long task name, you will no longer get an 
  AttributeError. Thanks to Marc Sibson.
* If a task has an uncaught exception, the debug-level output is displayed
  *and* Paver will exit with a return code of 1. No further tasks are
  executed. Thanks to Marc Sibson.
* The version number is no longer displayed, so that you can reasonably 
  pipe the output elsewhere. A new --version option will display the version
  as before.
* Eliminate DeprecationWarnings in paver.ssh and paver.svn. Thanks to Marc
  Sibson.
* The html task will always be defined now when you import paver.doctools
  but will yield a BuildFailure if Sphinx is not installed. Hopefully this
  will lead to clearer errors for people. Thanks to Marc Sibson.
* The Getting Started Guide has been improved for 1.0. Additionally,
  the "newway" sample now has a MANIFEST.in which provides useful knowledge
  for people.

1.0a1 (January 28, 2009)
------------------------
(note: 1.0a1 was recalled because it was unable to properly handle distutils command
line options.)

* COMPATIBILITY BREAK: paver.misctasks is no longer imported by default, even when using paver.easy
* DEPRECATIONS: paver.runtime and paver.defaults have been deprecated. Watch the
  warnings for info on how to change to the new paver.easy module.
* COMPATIBILITY WARNING: By default, the sh() function will now raise a 
  BuildFailure exception if the return code of the process is non-zero.
  Passing ignore_error=True will switch back to the previous behavior.
  Thanks to Marc Sibson.
* There is a new call_pavement function (automatically imported with
  from paver.easy import \*) that can call another pavement file. The
  new pavement gets its own environment/options but runs in the same
  process.
* You can now specify an alternate file to run rather than "pavement.py" using
  the -f or --file global option. Thanks to Marc Sibson.
* Regardless of logging level, output for a task is captured. If there is a BuildFailure,
  then that captured output is displayed.
* The new paver.tasks module encapsulates everything needed for running tasks
  in a file. The distutils ties have been reduced.
* @needs now accepts a list of requirements in the form @needs('task1', 'task2')
  (passing in a list still works as well)
* Added paver.bzr (support for Bazaar-NG related operations), courtesy of
  Bryan Forbes.
* The error() function is now exported, for logging of errors (thanks to Marc Sibson)
* Added handy paver.svn.export function for exporting an svn repository revision 
  (thanks to Marc Sibson)
* The "scripts" directory has been renamed "distutils_scripts" to avoid name collision
  on Windows.

0.8.1 (June 2, 2008)
--------------------
* Fix bug in minilib on Windows (error in rmtree). Also simplifies the minilib
  implementation. Patch from Juergen Hermann.
* Fix bug in virtualenv bootstrap generation (patches from Michael Greene and
  Juergen Hermann. Michael Greene's is the one that was applied.)

0.8 (May 19, 2008)
------------------

* Installation on Windows was broken due to a / at the end of the /paver/tests
  path in MANIFEST.in
* Options can now be set on the command line using the syntax option.name=value.
  Options are set at the point in which they appear on the command line, so
  you can set one value before task1 and then another value before task2.
* Option ordering can now take an explicit dictionary or Bunch added to the
  ordering. This allows you to put in new options without changing the global
  options dictionary and more closely resembles how options would be looked
  up in a buildout.
* call_task now supports an optional "options" argument that allows you to
  pass in a dictionary or Bunch that is added to the front of the option
  search ordering.

0.7.3 (May 16, 2008)
--------------------

* Added include_markers parameter to the paver.doctools.Includer to display a nice
  comment with the name of the file and section. This can look more attractive than
  the raw cog. By default, this is turned off. Set options.cog.include_markers
  to an empty dictionary, and the default include markers will be used.
* Added options.cog.delete_code to remove the generator code when cogging.
  Default: false
* Paver 0.7.2 could not be installed by zc.buildout on the Mac due to a problem
  with the py2app command under that environment.
* cog and tests were missing from shipped distributions (bug 229324, fixed with
  a patch from Krys Wilken.)
* Added svn.checkup function that does a checkout or update. This is like an
  svn:externals that's a bit more readable and easier to control, in my opinion.

0.7.2 (May 8, 2008)
-------------------

* Fixed Python 2.4 compatibility. The paver-minilib.zip file contained 2.5 
  .pyc files. .pyc files are not compatible between major Python versions.
  The new version contains .py files.

0.7.1 (May 8, 2008)
-------------------

* 0.7 had a broken paver-minilib.zip (missing misctasks.py, which is now part of the
  standard minilib)

0.7 (May 7, 2008)
----------------------

Breaking changes:

* "targets" have become "tasks", because that name is a clearer description.
* paver.sphinxdoc has been renamed paver.doctools

New features and changes:

* runtime.OPTIONS is gone now. The old voodoo surrounding the options() function
  has been replaced with a distinctly non-magical __call__ = update in the
  Namespace class.
* distutils.core.setup is now the command line driver
* distutils/setuptools commands can be seamlessly intermingled with Tasks
* tasks can have command line settable options via the cmdopts decorator.
  Additionally, they can use the consume_args decorator to collect up
  all command line arguments that come after the task name.
* Two new tasks: cog and uncog. These run Ned Batchelder's Cog code
  generator (included in the Paver package), by default against your
  Sphinx documentation. The idea is that you can keep your code samples
  in separate files (with unit tests and all) and incorporate them
  into your documentation files. Unlike the Sphinx include directives,
  using Cog lets you work on your documentation with the code samples
  in place.
* paver.doctools.SectionedFile provides a convenient way to mark off sections
  of a file, usually for documentation purposes, so that those sections can
  be included in another documentation file.
* paver.doctools.Includer knows how to look up SectionedFiles underneath
  a directory and to cache their sections.
* options are now a "Namespace" object that will search the sections for
  values. By default, the namespace is searched starting with top-level
  items (preserving current behavior) followed by a section named the same
  as the task, followed by all of the other sections. The order can
  be changed by calling options.order.
* option values that are callable will be called and that value returned.
  This is a simple way to provide lazy evaluation of options.
* Added minilib task that creates a paver-minilib.zip file that can be
  used to distribute programs that use Paver for their builds so that
  setup.py will run even without Paver fully installed.
* Added generate_setup task that creates a setup.py file that will
  actually run Paver. This will detect paver-minilib.zip if it's
  present.
* The "help" task has been greatly improved to provide a clearer picture
  of the tasks, options and commands available.
* Add the ability to create virtualenv bootstrap scripts
* The "help" property on tasks has changed to "description"
* output is now directed through distutils.log
* Ever improving docs, including a new Getting Started guide.
* Changes to Paver's bootstrap setup so that Paver no longer uses
  distutils for its bootstrapping.


There were no versions 0.5 and 0.6.

0.4 (April 22, 2008)
--------------------

* First public release.
* Removes setuptools dependency
* More docs
* Paver can now be run even without a pavement.py file for commands like
  help and paverdocs
