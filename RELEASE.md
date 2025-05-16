<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->

# Release

## General

We follow [Semantic Versioning 2.0.0](https://semver.org/) for new versions of
the Transformer Thermal Model. In short, this means we follow a structure of

```text
MAJOR.MINOR.PATCH
```

In order to not repeat what SemVer already neatly describes, we will just
highlight the parts we think is of most interest for the reader of this
document. Notably:

- MAJOR version when you make incompatible API/package changes (so not backwards compatible)
- MINOR version when you add functionality in a backward compatible manner
- PATCH version when you make backward compatible bug fixes

## Pre-releases

Whenever we work on a bigger release, e.g. a big major release for one of our
packages, we may use pre-releases. In this case, SemVer 2.0.0 says:

> A pre-release version MAY be denoted by appending a hyphen and a series of dot
> separated identifiers immediately following the patch version. (…)
>
> Examples: 1.0.0-alpha, 1.0.0-alpha.1, 1.0.0-0.3.7, 1.0.0-x.7.z.92,
> 1.0.0-x-y-z.--.

We choose to follow the alpha-beta structure, where we use the definition from
The wikipedia page of the
[Software release life cycle](https://en.wikipedia.org/wiki/Software_release_life_cycle).
Typically, this means that you follow the structure of:

1. alpha, to (e.g. 2.0.0-alpha)
1. beta, to (e.g. 2.0.0-beta)
1. release candidate (rc), to (e.g. 2.0.0-rc)
1. final version (e.g. 2.0.0)

We also use [Poetry](https://python-poetry.org/), and
there is a built-in command to update the version of your package, called poetry
version. We use this to update our versions, and also follow the structure that
Poetry provides to increment our versions using premajor, preminor, etc. Check
out the [documentation](https://python-poetry.org/docs/cli#version) for more info.

Here follow which parts we mainly focus on using the definitions from the
Wikipedia article.

### Alpha

e.g. `1.4.5-a2`

Alpha software is not thoroughly tested by the developer before it is released
to customers.

Alpha software may not contain all of the features that are planned for the
final version

### Beta

e.g. `1.4.5-b1`

A beta phase generally begins when the software is feature-complete but likely
to contain several known or unknown bugs.

The focus of beta testing is reducing impacts on users, often incorporating
[usability testing](https://en.wikipedia.org/wiki/Usability_testing).

### Release candidate

e.g. `1.4.5-rc`

We choose to not use the release candidate version, as we feel our software will
not benefit from this extra layer of release structure.Hence, a beta release
will be followed by a full release, and skip the release candidate step.
