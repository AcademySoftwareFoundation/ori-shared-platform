# Open Review Plugin Registry - Review Process and Acceptance Criteria

This document describes the requirements a plugin must meet to be listed in the
Open Review Plugin Registry and the policies that govern how listings are maintained
over time.

The registry is a **discovery index** — it links to community-hosted plugins, it does
not host source code. Acceptance into the registry does not constitute endorsement by
the Academy Software Foundation (ASWF) or the Open Review Initiative (ORI).

Key Words: "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" are defined in accordance with [BCP 14](https://www.rfc-editor.org/info/bcp14)

This document may be updated at any time. Significant changes will be announced in
the repository and on the ASWF Slack `#open-review-initiative` channel. The git
history of this file is the authoritative record of changes.

## Eligibility

To be considered for listing, a plugin must:

- **Target a supported host application.** Currently [OpenRV](https://github.com/AcademySoftwareFoundation/OpenRV) or [xStudio](https://github.com/AcademySoftwareFoundation/xstudio) (support for additional hosts may be added in future). The plugin MUST specify which version(s) of a supported host application is supported.
- **Be free and open source.** The plugin's source code MUST be released under an [OSI-approved open-source licence](https://opensource.org/licenses) declared in a `LICENSE` file at the repository root. The plugin must not ship proprietary third-party libraries or assets that prohibit redistribution ( see note on [Commercial Restrictions](#commercial-restrictions) below ).
- **Be hosted in a public GitHub repository** owned or maintained by the submitter.
- **Be functional at the time of submission.** The repository MUST contain an installable, working plugin — not a placeholder or work-in-progress stub. A `README.md` or equivalent MUST exist that explains how to install the plugin.

Regardless of licence or quality, any plugins which violate any of the conditions below SHALL NOT be listed:

- Plugins that contain malware, spyware, or any code intended to cause harm
- Plugins that infringe third-party intellectual property rights
- Plugins whose primary purpose is to circumvent security, licensing, or access controls
- Submissions that violate the [ASWF Code of Conduct](./CODE_OF_CONDUCT.md)
- Duplicate listings for the same plugin (e.g. a submitter opening multiple entries for the same repository)

### Commercial Restrictions

**The registry does not currently accept commercial plugins** — plugins that require
payment, a paid subscription, or a proprietary licence to install or use in any form.

This restriction applies to the plugin itself. Plugins that integrate with commercial
third-party services (e.g. a pipeline connector that requires a subscription to that
service) may still be listed, provided the plugin code itself is free and open source.

Open Review Initiative anticipates revisiting this policy in the future as the registry matures. Any change
will be announced in the repository and on the ASWF Slack `#open-review-initiative`
channel before taking effect.

## Proposal Process

Interested plugin maintainers MUST complete the plugin proposal application by submitting a PR at https://github.com/AcademySoftwareFoundation/ori-shared-platform. The following information MUST be provided.

- Plugin name
- Description that reflects what the project does.
- Link the project repo.
- Host application(s) and version(s) of the host application(s) supported.
- Suggested tags.
- Location of LICENSE and installation requirements.

Plugin proposals are reviewed on a regular basis by the Open Review Initiative TSC or a designated sub-committee. Reviewers will leave comments on the PR created if changes are required before a listing can be accepted. Below are the submission statuses.

- **Approved** — will be added to the registry.
- **Request Changes** — the submitter must address the requested changes before it can be added to the registry.
- **Closed** — if the plugin does not meet these criteria, the submitter will receive an explanation and may resubmit once the issue is resolved

## Review and removal

The Open Review Initiative TSC or designated sub-committee will review all registry entries on a regular basis. Plugins no longer meeting the [Eligibility](#eligibility) requirements may be removed from the registry, with or without prior notice.

Common reasons for removal include, but are not limited to:

- The plugin no longer functions with current versions of the host application and the repository shows no sign of active maintenance
- The repository has been deleted, made private, or moved without the registry entry being updated
- The plugin or its repository is found to violate these criteria after listing
- The listing is found to be inaccurate or misleading
- A Code of Conduct violation by the plugin author in the context of this registry

Where possible, maintainers will open an issue or leave a comment before removing a
listing, giving the plugin owner an opportunity to address the concern. This is a
courtesy, not a commitment.

## Contact

For questions about these criteria, a submitted or rejected PR, or a concern about
an existing listing:

- **ORI Plug-in's Email** — [plugins@openreviewinitiative.org](mailto:plugins@openreviewinitiative.org)
- **ASWF Slack** — join at [slack.aswf.io](https://slack.aswf.io/) and find the `#open-review-initiative` channel
- **GitHub Issues** — [AcademySoftwareFoundation/ori-shared-platform/issues](https://github.com/AcademySoftwareFoundation/ori-shared-platform/issues)

Please do not open a GitHub Issue to appeal a rejected submission — use Slack first
so the conversation can happen in the open without creating noise in the issue tracker.
