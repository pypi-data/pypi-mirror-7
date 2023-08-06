Changelog
=========

1.0b4 - 2014-06-11
------------------

* Added ``playbook`` and ``roles`` config options for instances.
  [fschulze]

* Added ``has_playbook`` and ``configure`` methods to instances.
  [fschulze]

* Added before/after_ansible_configure hooks.
  [fschulze]


1.0b3 - 2014-06-09
------------------

* Use execnet for connections. There is only one ssh connection per host and
  it's reused for all commands.
  [fschulze]

* Make sure the playbook directory is always absolute.
  [fschulze]

* Prevent use of persistent ssh connections, as that easily results in
  connections to wrong jails because of the proxying. This makes ansible a lot
  slower at the moment.
  [fschulze]

* Add support for su and vault (ansible 1.5) as well as ``--force-handlers``
  (ansible 1.6).
  [fschulze]

* Removed ``ansible`` from install requirements. It won't install in a buildout
  so it needs to be installed in a virtualenv or via a system package.
  [fschulze]


1.0b2 - 2014-05-15
------------------

* Add ``configure`` command which is a stripped down variant of the
  ``playbook`` command with assumptions about the location of the yml file.
  [fschulze]

* Warn if a playbook is requested for a host that is not configured in the
  playbook hosts list.
  [fschulze]

* Allow mr.awsome plugins to add ansible variables.
  [fschulze]

* Inject the ansible paths sooner as they may not apply in some cases otherwise.
  [fschulze]

* Moved setuptools-git from setup.py to .travis.yml, it's only needed for
  releases and testing.
  [fschulze]


1.0b1 - 2014-03-24
------------------

* Initial release
  [fschulze]
