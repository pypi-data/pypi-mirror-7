# verify_version_spec

Verify that a version specification matches a version string.

This is mainly used to check that a version returned from a command line
program is within a version specification like: ">=0.9,<0.10".  It uses the
[semantic_version](https://pypi.python.org/pypi/semantic_version/2.3.0) library
which implements the [SemVer scheme](http://semver.org/).


## Usage

To verify that the target version "1.2.3" is within the specification ">=1.2". ::

  $ verify_version_spec --spec=">=1.2" 1.2.3

