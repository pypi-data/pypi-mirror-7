
# This file helps to compute a version number in source trees obtained from
# git-archive tarball (such as those provided by githubs download-from-tag
# feature). Distribution tarballs (build by setup.py sdist) and build
# directories (produced by setup.py build) will contain a much shorter file
# that just contains the computed version number.

# This file is released into the public domain. Generated by
# versioneer-0.10+ (https://github.com/warner/python-versioneer)

"""This text is put at the top of _version.py, and can be keyword-replaced with 
version information by the VCS.
"""

# these strings will be replaced by git during git-archive
git_refnames = "$Format:%d$"
git_full_revisionid = "$Format:%H$"
git_short_revisionid = "$Format:%h$"

# these strings are filled in when 'setup.py versioneer' creates _version.py
tag_prefix = ""
parentdir_prefix = "svn-"
versionfile_source = "svn/_version.py"
version_string_template = "%(default)s"


import subprocess
import sys
import errno


def run_command(commands, args, cwd=None, verbose=False, hide_stderr=False):
    assert isinstance(commands, list)
    p = None
    for c in commands:
        try:
            # remember shell=False, so use git.cmd on windows, not just git
            p = subprocess.Popen([c] + args, cwd=cwd, stdout=subprocess.PIPE,
                                 stderr=(subprocess.PIPE if hide_stderr
                                         else None))
            break
        except EnvironmentError:
            e = sys.exc_info()[1]
            if e.errno == errno.ENOENT:
                continue
            if verbose:
                print("unable to run %s" % args[0])
                print(e)
            return None
    else:
        if verbose:
            print("unable to find command, tried %s" % (commands,))
        return None
    stdout = p.communicate()[0].strip()
    if sys.version >= '3':
        stdout = stdout.decode()
    if p.returncode != 0:
# TODO(dustin): Maybe we should contemplate raising a SystemError here, rather 
# then returning a None. It's almost always preferable that it would default to 
# being a terminal error unles specifically caught (rather than vice versa).
        if verbose:
            print("unable to run %s (error)" % args[0])
        return None
    return stdout


def versions_from_parentdir(parentdir_prefix, root, verbose=False):
    """Return a dictionary of values derived from the name of our parent 
    directory (useful when a thoughtfully-named directory is created from an 
    archive). This is the fourth attempt to find information by get_versions().
    """

    # Source tarballs conventionally unpack into a directory that includes
    # both the project name and a version string.
    dirname = os.path.basename(root)
    if not dirname.startswith(parentdir_prefix):
        if verbose:
            print("guessing rootdir is '%s', but '%s' doesn't start with prefix '%s'" %
                  (root, dirname, parentdir_prefix))
        return None
    version = dirname[len(parentdir_prefix):]
    return { "describe": version,
             "long": version,
             "pep440": version,
             }

import re

def git_get_keywords(versionfile_abs):
    """Return a dictionary of values replaced by the VCS, automatically. This 
    is the first attempt to find information by get_versions().
    """

    # the code embedded in _version.py can just fetch the value of these
    # keywords. When used from setup.py, we don't want to import _version.py,
    # so we do it with a regexp instead. This function is not used from
    # _version.py.
    keywords = {}
    try:
        with open(versionfile_abs) as f:
            for line in f.readlines():
                if line.strip().startswith("git_refnames ="):
                    mo = re.search(r'=\s*"(.*)"', line)
                    if mo:
                        keywords["refnames"] = mo.group(1)
                if line.strip().startswith("git_full_revisionid ="):
                    mo = re.search(r'=\s*"(.*)"', line)
                    if mo:
                        keywords["full_revisionid"] = mo.group(1)
                if line.strip().startswith("git_short_revisionid ="):
                    mo = re.search(r'=\s*"(.*)"', line)
                    if mo:
                        keywords["short_revisionid"] = mo.group(1)
    except EnvironmentError:
        pass
    return keywords

def git_versions_from_keywords(keywords, tag_prefix, verbose=False):
    if not keywords:
        return {} # keyword-finding function failed to find keywords
    refnames = keywords["refnames"].strip()
    if refnames.startswith("$Format"):
        if verbose:
            print("keywords are unexpanded, not using")
        return {} # unexpanded, so not in an unpacked git-archive tarball
    refs = set([r.strip() for r in refnames.strip("()").split(",")])
    # starting in git-1.8.3, tags are listed as "tag: foo-1.0" instead of
    # just "foo-1.0". If we see a "tag: " prefix, prefer those.
    TAG = "tag: "
    tags = set([r[len(TAG):] for r in refs if r.startswith(TAG)])
    if not tags:
        # Either we're using git < 1.8.3, or there really are no tags. We use
        # a heuristic: assume all version tags have a digit. The old git %d
        # expansion behaves like git log --decorate=short and strips out the
        # refs/heads/ and refs/tags/ prefixes that would let us distinguish
        # between branches and tags. By ignoring refnames without digits, we
        # filter out many common branch names like "release" and
        # "stabilization", as well as "HEAD" and "master".
        tags = set([r for r in refs if re.search(r'\d', r)])
        if verbose:
            print("discarding '%s', no digits" % ",".join(refs-tags))
    if verbose:
        print("likely tags: %s" % ",".join(sorted(tags)))
    shortest_tag = None
    for ref in sorted(tags):
        # sorting will prefer e.g. "2.0" over "2.0rc1"
        if ref.startswith(tag_prefix):
            shortest_tag = ref[len(tag_prefix):]
            if verbose:
                print("picking %s" % shortest_tag)
            break
    versions = {
        "full_revisionid": keywords["full_revisionid"].strip(),
        "short_revisionid": keywords["short_revisionid"].strip(),
        "dirty": False, "dash_dirty": "",
        "closest_tag": shortest_tag,
        "closest_tag_or_zero": shortest_tag or "0",
        # "distance" is not provided: cannot deduce from keyword expansion
        }
    if not shortest_tag and verbose:
        print("no suitable tags, using full revision id")
    composite = shortest_tag or versions["full_revisionid"]
    versions["describe"] = composite
    versions["long"] = composite
    versions["default"] = composite
    versions["pep440"] = composite
    return versions

import re
import sys
import os.path

def git_versions_from_vcs(tag_prefix, root, verbose=False):
    """Return a dictionary of values derived directly from the VCS. This is the
    third attempt to find information by get_versions().
    """

    # this runs 'git' from the root of the source tree. This only gets called
    # if the git-archive 'subst' keywords were *not* expanded, and
    # _version.py hasn't already been rewritten with a short version string,
    # meaning we're inside a checked out source tree.

    if not os.path.exists(os.path.join(root, ".git")):
        if verbose:
            print("no .git in %s" % root)
        return {}

    GITS = ["git"]
    if sys.platform == "win32":
        GITS = ["git.cmd", "git.exe"]

    versions = {}

    full_revisionid = run_command(GITS, ["rev-parse", "HEAD"], cwd=root)
    if full_revisionid is None:
        return {}
    versions["full_revisionid"] = full_revisionid.strip()

    d = run_command(GITS,
                    ["describe", "--tags", "--dirty", "--always", "--long"],
                    cwd=root)
    if d is None:
        return {}
    d = d.strip()
    # "TAG-DIST-gHASH[-dirty]" , where DIST might be "0"
    # or just "HASH[-dirty]" if there are no ancestor tags

    versions["long"] = d

    mo1 = re.search(r"^(.*)-(\d+)-g([0-9a-f]+)(-dirty)?$", d)
    mo2 = re.search(r"^([0-9a-f]+)(-dirty)?$", d)
    if mo1:
        rawtag = mo1.group(1)
        if not rawtag.startswith(tag_prefix):
            if verbose:
                print("tag '%s' doesn't start with prefix '%s'" % (rawtag, tag_prefix))
            return {}
        tag = rawtag[len(tag_prefix):]
        versions["closest_tag"] = tag
        versions["distance"] = int(mo1.group(2))
        versions["short_revisionid"] = mo1.group(3)
        versions["dirty"] = bool(mo1.group(4))
        versions["pep440"] = tag
        if versions["distance"]:
            versions["describe"] = d
            versions["pep440"] += ".post%d" % versions["distance"]
        else:
            versions["describe"] = tag
            if versions["dirty"]:
                versions["describe"] += "-dirty"
        if versions["dirty"]:
            # not strictly correct, as X.dev0 sorts "earlier" than X, but we
            # need some way to distinguish the two. You shouldn't be shipping
            # -dirty code anyways.
            versions["pep440"] += ".dev0"
        versions["default"] = versions["describe"]

    elif mo2: # no ancestor tags
        versions["closest_tag"] = None
        versions["short_revisionid"] = mo2.group(1)
        versions["dirty"] = bool(mo2.group(2))
        # count revisions to compute ["distance"]
        commits = run_command(GITS, ["rev-list", "--count", "HEAD"], cwd=root)
        if commits is None:
            return {}
        versions["distance"] = int(commits.strip())
        versions["pep440"] = "0"
        if versions["distance"]:
            versions["pep440"] += ".post%d" % versions["distance"]
        if versions["dirty"]:
            versions["pep440"] += ".dev0" # same concern as above
        versions["describe"] = d
        versions["default"] = "0-%d-g%s" % (versions["distance"], d)
    else:
        return {}
    versions["dash_dirty"] = "-dirty" if versions["dirty"] else ""
    versions["closest_tag_or_zero"] = versions["closest_tag"] or "0"
    if versions["distance"] == 0:
        versions["dash_distance"] = ""
    else:
        versions["dash_distance"] = "-%d" % versions["distance"]

    return versions

import os

def get_versions(default={"version": "unknown", "full": ""}, verbose=False):
    """This variation of get_versions() will be used in _version.py ."""

    # I am in _version.py, which lives at ROOT/VERSIONFILE_SOURCE. If we have
    # __file__, we can work backwards from there to the root. Some
    # py2exe/bbfreeze/non-CPython implementations don't do __file__, in which
    # case we can only use expanded keywords.

    keywords = { "refnames": git_refnames,
                 "full_revisionid": git_full_revisionid,
                 "short_revisionid": git_short_revisionid }
    ver = git_versions_from_keywords(keywords, tag_prefix, verbose)
    if ver:
        return ver

    try:
        root = os.path.abspath(__file__)
        # versionfile_source is the relative path from the top of the source
        # tree (where the .git directory might live) to this file. Invert
        # this to find the root from __file__.
# TODO(dustin): Shouldn't this always loop until it fails?
        for i in range(len(versionfile_source.split(os.sep))):
            root = os.path.dirname(root)
    except NameError:
        return default

    return (git_versions_from_vcs(tag_prefix, root, verbose)
            or versions_from_parentdir(parentdir_prefix, root, verbose)
            or default)
