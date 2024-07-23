Contributing to review_plugin_api
=================================

Code contributions to review_plugin_api are always welcome.  Please review this document 
to get a briefing on our process.


Communication
-------------

The [ASWF Slack](https://slack.aswf.io/) has an `open-review-initiative` channel. Sign up
for the Slack on your own, then under "channels", select "browse channels" and
you should see the open-review-initiative channel (among those of the other projects and
working groups).


How to Ask for Help
-------------------

If you have trouble installing, building, or using review_plugin_api, but there's
not yet a solid reason to suspect you've encountered a genuine bug, start by
posting a question at the slack channel above.


Bug Reports and Issue Tracking
------------------------------

We use GitHub's issue tracking system for reporting bugs and requesting
enhancements: https://github.com/AcademySoftwareFoundation/ori-shared-platform/issues

If you are submitting a bug report, please give a specific, as-detailed-as-possible 
account of

* what you tried (command line, source code example)
* what you expected to happen
* what actually happened (crash? error message? ran but didn't give the
  correct result?)

with enough detail that others can easily reproduce the problem just by
following your instructions. Please quote the exact error message you
received.

Suspected security vulnerabilities should be reported by the same process.

Contributor License Agreement (CLA) and Intellectual Property
-------------------------------------------------------------

To protect the project -- and the contributors! -- we do require a Contributor
License Agreement (CLA) for anybody submitting changes. This is for your own
safety, as it prevents any possible future disputes between code authors and
their employers or anyone else who might think they might own the IP output of
the author.

* [Corporate CLA](https://github.com/AcademySoftwareFoundation/OpenImageIO/blob/master/ASWF/CLA-corporate.md) :
  If you are writing the code as part of your job, or if there is any
  possibility that your employers might think they own any intellectual
  property you create. This needs to be executed by someone who has
  signatory power for the company.

* [Individual CLA](https://github.com/AcademySoftwareFoundation/OpenImageIO/blob/master/ASWF/CLA-individual.md) :
  If you are an individual writing the code on your own time, using your own
  equipment, and you're SURE you are the sole owner of any intellectual
  property you contribute.

Please note that it is extremely common (nearly ubiquitous in the US and
Canada, and maybe other places) for full-time employees of technology and
entertainment companies to have IP clauses in their employment agreement (in
that pile of paperwork you sign on your first day of work and then promptly
forget about) that give the company rights to any code you write, even on your
own time. The OpenImageIO project expects you to know and follow the rules of
your employer and to have them sign a corporate CLA if necessary.

The easiest way to sign CLAs is digitally [using
EasyCLA](https://corporate.v1.easycla.lfx.linuxfoundation.org). There are
detailed step-by-step instructions about using the EasyCLA system for
[corporate CLAs](https://docs.linuxfoundation.org/lfx/easycla/v2-current/contributors/corporate-contributor)
and [individual CLAs](https://docs.linuxfoundation.org/lfx/easycla/v2-current/contributors/individual-contributor#github).

Companies who prefer not to use the online tools may sign, scan, and email
the executed copy to manager@lfprojects.org.

The corporate CLA allows a company to name a "CLA Manager" (who does not need
signatory power) who has the ability to use the online system to add or delete
individual employees of the company who are authorized to submit pull
requests, without needing to get an executive to amend and sign the agreement
each time.

Please note that these CLAs are based on the Apache 2.0 CLAs, and differ
minimally, only as much as was required to correctly describe the EasyCLA
process and our use of a CLA manager.

**Contribution sign off**

This project requires the use of the [Developer’s Certificate of Origin 1.1
(DCO)](https://developercertificate.org/), which is the same mechanism that
the [Linux®
Kernel](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/Documentation/process/submitting-patches.rst#n416)
and many other communities use to manage code contributions. The DCO is
considered one of the simplest tools for sign offs from contributors as the
representations are meant to be easy to read and indicating signoff is done
as a part of the commit message.

Here is an example Signed-off-by line, which indicates that the submitter
accepts the DCO:

    Signed-off-by: John Doe <john.doe@example.com>

You can include this automatically when you commit a change to your local
git repository using `git commit -s`. You might also want to
leverage this [command line tool](https://github.com/coderanger/dco) for
automatically adding the signoff message on commits.


Commit messages
---------------

### Summary heuristic

Look at the commit history of the project to get a sense of the style and
level of detail that is expected in commit messages.

### General guidelines and expectations

The first line of the commit message should be a short (less than 80
characters) summary of the change, prefixed with the general nature of the
change (see below).

The rest of the commit message should be a more detailed explanation of the
changes. Some commits are self-explanatory and don't need more than the
summary line. Others may need a more detailed explanation. Hallmarks of
a good commit message include:

* An explanation of why the change is necessary and what you hope to
  accomplish with it.
* A description of any major user- or developer-facing changes that people
  should be aware of: changes in APIs or behaviors, new features, etc.
* An explanation of any tricky implementation details or design decisions that
  might not be immediately obvious to someone reading the code.
* Guideposts for somebody reviewing the code to understand the rationale and
  have any supporting background information to fully understanding the code
  changes.

Remember that at some point in the future, a developer unfamiliar with your
change (maybe you, long after you've forgotten the details) might need to
understand or fix your patch. Keep that person in mind as your audience and
strive to write a commit message that explains the context in a way that saves
them time and effort. Be the hero in the story of their future debugging
effort!

Pull Requests and Code Review
-----------------------------

The best way to submit changes is via GitHub Pull Request. GitHub has a
[Pull Request Howto](https://help.github.com/articles/using-pull-requests/).

All code must be formally reviewed before being merged into the official
repository. The protocol is like this:

1. Get a GitHub account, fork AcademySoftwareFoundation/OpenImageIO to create
your own repository on GitHub, and then clone it to get a repository on your
local machine.

1. Edit, compile, and test your changes. Run clang-format (see the
instructions on coding style below).

1. Push your changes to your fork (each unrelated pull request to a separate
"topic branch", please).

1. Make a "pull request" on GitHub for your patch.

2. If your patch will induce a major compatibility break, or has a design
component that deserves extended discussion or debate among the wider OIIO
community, then it may be prudent to email oiio-dev pointing everybody to
the pull request URL and discussing any issues you think are important.

1. All pull requests automatically launch CI jobs on GitHub Actions to
ensure that the build completes and that the tests suite runs correctly, for
a variety of platform, compiler, library, and flag combinations. The status
of the CI tests for your PR will be displayed on the GitHub PR page. We will
not accept PRs that don't build cleanly or pass the existing testsuite.

1. The reviewer will look over the code and critique on the "comments" area.
Reviewers may ask for changes, explain problems they found, congratulate the
author on a clever solution, etc. But until somebody says "LGTM" (looks good
to me), the code should not be committed. Sometimes this takes a few rounds
of give and take. Please don't take it hard if your first try is not
accepted. It happens to all of us.

1. After approval, one of the senior developers (with commit approval to the
official main repository) will merge your fixes into the master branch.
