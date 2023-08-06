Release Checklist
=================

 * double-check version updated, sadly in a few places:
    * Makefile
    * setup.py
    * txtorcon/__init__.py

 * run all tests, on all configurations
    * "tox"

 * "make pep8" should run cleanly (ideally)

 * update docs/releases.rst to reflect upcoming reality
    * blindly make links to the signatures
    * update heading, date

 * make dist (tries to sign, or can do so manually)
    * creates:
      dist/txtorcon-X.Y.Z.tar.gz.asc
      dist/txtorcon-X.Y.Z-py2-none-any.whl.asc
    * add the signatures to "signatues/"

 * generate sha256sum for each:
      sha256sum dist/txtorcon-X.Y.Z.tar.gz
      sha256sum dist/txtorcon-X.Y.Z-py2-none-any.whl

 * draft email to tor-dev (and probably twisted-python):
    * example: https://lists.torproject.org/pipermail/tor-dev/2014-January/006111.html
    * copy-paste release notes, un-rst-format them
    * include above sha256sum
    * clear-sign the announcement
    * git --armor --clearsign -u meejah@meejah.ca path/to/release-announcement-X-Y-Z

 * create signed tag
    * git tag -s -u meejah@meejah.ca -F path/to/release-announcement-X-Y-Z vX.Y.Z

 * copy dist/* files + signatures to hidden-service machine

 * git pull and build docs there
    * FIXME: why aren't all the dist files copied as part of doc build (only .tar.gz)

 * download both distributions + signatures from hidden-service
    * verify sigs
    * verify sha256sums versus announcement text
    * verify tag (git tag -v v0.9.2) on machine other than signing-machine

 * upload release
    * to PyPI: "make release" (which uses twine so this isn't the same step as "sign the release")
       * note this depends on a ~/.pypirc file with [server-login] section containing "username:" and "password:"
    * to github: use wonky web-upload interface to upload the 4 files (both dists, both signature)

 * make announcement
    * post to tor-dev@ the clear-signed release announcement
    * post to twisted-python@ the clear-signed release announcement
    * tell #tor-dev??

