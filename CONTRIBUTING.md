Contributing to ori-shared-platform
=====================================

Code contributions to ori-shared-platform are always welcome. Please review this document 
to get a briefing on our process.


Communication
-------------

The [ASWF Slack](https://slack.aswf.io/) has an `open-review-initiative` channel. Sign up
for the Slack on your own, then under "channels", select "browse channels" and
you should see the open-review-initiative channel (among those of the other projects and
working groups).


How to Ask for Help
-------------------

If you have trouble installing, building, or using ori-shared-platform, but there's
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

**Contribution sign off**

This project requires the use of the [Developer's Certificate of Origin 1.1
(DCO)](https://developercertificate.org/), which is the same mechanism that
the [Linux® Kernel](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/Documentation/process/submitting-patches.rst#n416)
and many other communities use to manage code contributions. The DCO is
considered one of the simplest tools for sign offs from contributors as the
representations are meant to be easy to read and indicating signoff is done
as a part of the commit message.

Here is an example Signed-off-by line, which indicates that the submitter
accepts the DCO:

    Signed-off-by: John Doe <john.doe@example.com>

You can include this automatically when you commit a change to your local
git repository using `git commit -s`.


Commit messages
---------------

Look at the commit history of the project to get a sense of the style and
level of detail that is expected in commit messages.

The first line of the commit message should be a short (less than 80
characters) summary of the change. The rest should explain why the change is
necessary, describe any user- or developer-facing behaviour changes, and note
any non-obvious implementation decisions.


Pull Requests and Code Review
-----------------------------

The best way to submit changes is via GitHub Pull Request. GitHub has a
[Pull Request Howto](https://help.github.com/articles/using-pull-requests/).

All code must be formally reviewed before being merged into the official
repository. The protocol is like this:

1. Fork AcademySoftwareFoundation/ori-shared-platform to create your own
repository on GitHub, then clone it to get a repository on your local machine.

1. Edit, compile, and test your changes.

1. Push your changes to your fork (each unrelated pull request to a separate
"topic branch", please).

1. Make a "pull request" on GitHub for your patch.

1. All pull requests automatically launch CI jobs on GitHub Actions to
ensure that the build completes and that the test suite runs correctly.
We will not accept PRs that don't build cleanly or pass the existing test suite.

1. The reviewer will look over the code and leave comments. Reviewers may ask
for changes or clarifications. Until somebody approves the PR, the code should
not be committed.

1. After approval, a committer will merge your changes into the main branch.


Plugin Registry Submissions
----------------------------

To add your plugin to the Open Review Plugin Registry, see the
[Acceptance Criteria](./ACCEPTANCE-CRITERIA.md) for eligibility requirements,
then follow the step-by-step [submission guide](https://academysoftwarefoundation.github.io/ori-shared-platform-website/contributing/).

Plugin listing questions: [plugins@openreviewinitiative.org](mailto:plugins@openreviewinitiative.org)
