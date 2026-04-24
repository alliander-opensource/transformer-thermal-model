<!--
SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project

SPDX-License-Identifier: MPL-2.0
-->

# How to Contribute

We'd love to accept your patches and contributions to this project. There are
just a few small guidelines you need to follow.

## Ways of contributing

![Schematic view of the 5 levels of contributing, with stars showing increasing amounts of sparkles around them](/.github/assets/levels_of_contribution.png)

Contribution does not necessarily mean committing code to the repository.
We recognize different levels of contributions as shown below in increasing order of dedication:

1. Test and use the project.
2. Give feedback on the user experience or suggest new features. Report bugs or security vulnerabilities.
3. Improve the code quality by checking out our SonarCloud results.
4. Improve the project by developing new features.
5. Improve our calculation core by optimizing the code.

## Filing bugs, security vulnerability or feature requests

You can file bugs against and feature requests for the project via github
issues. Consult [GitHub
Help](https://docs.github.com/en/free-pro-team@latest/github/managing-your-work-on-github/creating-an-issue)
for more information on using github issues.

If you think you've found a potential vulnerability in this project, please
email <transformer-thermal-model@alliander.com> to responsibly disclose it.

## Develop new features

You can help to improve the project with developing new features. Please read
the following for details on how to contribute:

### Set up

1. Make sure you have `poetry` installed
   ([documentation](https://python-poetry.org/docs/))
2. Make sure you are on the correctly supported Python version (check
   `pyproject.toml`).
3. Install dependencies using `poetry install --with dev`.
    - for contributions to the documentation page, make sure you install
      the correct dependencies using `poetry install --with docs`, too.
4. Activate the poetry shell: `poetry shell`.
5. Set up pre-commit hooks: `pre-commit install`. Every time you commit, this
   will run hooks to ensure your code is properly formatted.
6. Make a new branch from `main`
   - If your branch will be related to a Jira ticket (which we recommend), you
     can use the option `Create branch` from there. Make sure that your work is
     small enough so that your branch can be merged within 2 to 3 days.
7. Make a PR for your branch (yes, immediately!) and put it in *Draft*.

### During development

To check if `pre-commit` was properly installed, run `pre-commit run -a`. You
should see the following:

```bash
$ pre-commit run -a
ruff.....................................................................Passed
ruff-format..............................................................Passed
mypy.....................................................................Passed
codespell................................................................Passed
Poetry check.............................................................Passed
markdownlint.............................................................Passed
```

If any of these checks fail, make sure to make a new issue and notify us via
the contact information below.

Make sure to regularly run `pytest` during your work and after your changes.
Also, to prevent annoyances when committing, you can regularly run `ruff check
--fix` and `mypy .` to stay ahead on your typos and typing errors.

#### How we write commit messages

Finally,
after developing, you will commit. Make sure to adhere the [Angular commit
convention](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines),
i.e.

```text
<type>: <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

Where type must be one of the following:

- build: Changes that affect the build system or external dependencies (example
  scopes: gulp, broccoli, npm)
- ci: Changes to our CI configuration files and scripts (example scopes: Travis,
  Circle, BrowserStack, SauceLabs)
- docs: Documentation only changes
- feat: A new feature
- fix: A bug fix
- perf: A code change that improves performance
- refactor: A code change that neither fixes a bug nor adds a feature
- style: Changes that do not affect the meaning of the code (white-space,
  formatting, missing semi-colons, etc)
- test: Adding missing tests or correcting existing tests

If your change is `BREAKING`, add it to the `<body>` of your commit message and
explain what exactly is changing to be `BREAKING`. Also, add an explanation
mark `!` after your `<type>`, e.g.

```text
feat!: let user provide wattage parameter to Transformer object

BREAKING: Beforehand our `Transformer` could be initialised without wattage,
now I've added the parameter `wattage` that is needed for (some feature I am
making in this PR), because ... .
```

#### Working on the documentation

Transformer Thermal Model uses [MkDocs](https://www.mkdocs.org/) for documentation. To install the dependencies with
poetry, run:

```bash
poetry install --with docs
```

Then you can run a local version of our documentation page with:

```bash
mkdocs serve
```

For more information, visit their [user guide](https://www.mkdocs.org/user-guide/writing-your-docs/).

### After development

You should have your pull request ready. If you forgot to draft one, do that
now. Check if all your commits follow our guidelines, and add a description
to your PR. It should describe: 1) your problem that you wanted to solve, 2)
the steps you took to solve it, 3) some decisions you did or did not make, and
why, and maybe 4) some following steps you'd like to take after this has been
merged. If this information is lacking, it's hard for us to do
a proper review. Please provide enough information. Then, merge `main` back
into your development branch to fix any merging conflicts.

After you've done that, it's time to get your PR out of draft, and mark it for
review.  It should automatically pick someone from DALi to review. During this,
it will also run our hooks pre-merge. If any of those fail, you should attend to
those asap. Finally, if your PR is accepted by any of your reviewers, **you**
will merge it via the `Squash and merge` option. If you have a descriptive PR,
and good commit messages, everything is in order. If your reviewer noted some
changes you should have made on your commit messages, you can either take the
difficult way and use `rebase -i` to rename them, then push it, or just make the
changes in the squashed commit, which is also fine.

So, in short:

1. Run `pre-commit run -a` locally.
2. Run `pytest` locally.
3. Check your local commit messages before pushing.
4. `git push`
5. Head to your PR, add a description, answering:
   1. What was the original problem?
   2. How did you solve it, why did you pick this solution?
   3. What decisions did you make and why?
   4. Did you run into issues?
   5. Are there any following steps there should be made after this PR?
6. Remove the "Draft" option, to mark it for review
7. Make the changes from your review, and mark them as "resolved", re-request
   review if needed.
8. Squash and merge.

## Community Guidelines

This project follows the following [Code of Conduct](CODE_OF_CONDUCT.md).

## REUSE Compliance & Source Code Headers

All the files in the repository need to be [REUSE compliant](https://reuse.software/).
We use the pipeline to automatically check this.
If there are files which are not complying, the pipeline will fail the pull request will be blocked.

This means that every file containing source code must include copyright and license
information. This includes any JS/CSS files that you might be serving out to
browsers. (This is to help well-intentioned people avoid accidental copying that
doesn't comply with the license.)

MPL-2.0 header:

```text
    SPDX-FileCopyrightText: 'Copyright Contributors to the Transformer Thermal Model project'
    SPDX-License-Identifier: MPL-2.0
```

## Git branching

This project uses the
[Trunk Based workflow](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development)
and branching model. The `main` branch always contains the most recent code, and
we decide when it is fit for a new release. When a feature is finished it is
merged back into `main`. We rely on automated testing and checks to make sure
the quality of the code on the `main` branch stays consistent.

We have a naming convention of our branches to easily identify the type
of work taking place on that branch. We follow the same naming convention
as our commits, the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
, but instead of the `:` to separate the prefix from the title, we
use `/`. Some examples:

- `feat/allow-user-to-specify-the-tap-changer-capacity`
- `fix/prevent-nan-results-when-dates-missing-in-input`
- `feat!/group-all-seperate-specs-into-one-attribute-in-transformer`

For more details on this naming convention, check out [our section on how to write commits](#how-we-write-commit-messages).

## Signing the Developer Certificate of Origin (DCO)

This project utilize a Developer Certificate of Origin (DCO) to ensure that each
commit was written by the author or that the author has the appropriate rights
necessary to contribute the change.  Specifically, we utilize [Developer
Certificate of Origin, Version 1.1](http://developercertificate.org/), which is
the same mechanism that the Linux® Kernel and many other communities use to
manage code contributions.  The DCO is considered one of the simplest tools for
sign-offs from contributors as the representations are meant to be easy to read
and indicating signoff is done as a part of the commit message.

This means that each commit must include a DCO which looks like this:

`Signed-off-by: Joe Smith <joe.smith@email.com>`

The project requires that the name used is your real name and the e-mail used is
your real e-mail.
Neither anonymous contributors nor those utilizing pseudonyms will be accepted.

There are other great tools out there to manage DCO signoffs for developers to
make it much easier to do signoffs:

* Git makes it easy to add this line to your commit messages. Make sure the
  `user.name` and `user.email` are set in your git configs. Use `-s` or
  `--signoff` to add the Signed-off-by line to the end of the commit message.
* [Github UI automatic signoff
  capabilities](https://github.blog/changelog/2022-06-08-admins-can-require-sign-off-on-web-based-commits/)
  for adding the signoff automatically to commits made with the GitHub browser
  UI. This one can only be activated by the github org or repo admin.
* [GitHub UI automatic signoff capabilities via custom plugin](
  https://github.com/scottrigby/dco-gh-ui ) for adding the signoff automatically
  to commits made with the GitHub browser UI
* Additionally, it is possible to use shell scripting to automatically apply the
  sign-off. For more info, check out
  [an example for bash to be put into a .bashrc file](https://wiki.lfenergy.org/display/HOME/Contribution+and+Compliance+Guidelines+for+LF+Energy+Foundation+hosted+projects).
* Alternatively, you can add `prepare-commit-msg hook` in .git/hooks directory.
  [Check out this example](https://github.com/Samsung/ONE-vscode/wiki/ONE-vscode-Developer's-Certificate-of-Origin)
  for more info.

## Code reviews

All patches and contributions, including patches and contributions by project
members, require review by one of the maintainers of the project. We use GitHub
pull requests for this purpose. Consult [GitHub
Help](https://help.github.com/articles/about-pull-requests/) for more
information on using pull requests.

## Pull Request Process

Contributions should be submitted as Github pull requests. See [Creating a pull
request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request)
if you're unfamiliar with this concept.

The process for a code change and pull request you should follow:

1. Create a topic branch in your local repository, following the naming format
"feature-[description]". For more information see the Git branching guideline.
1. Make changes, compile, and test thoroughly. Ensure any install or build
   dependencies are removed before the end of the layer when doing a build. Code
   style should match existing style and conventions, and changes should be
   focused on the topic the pull request will be addressed. For more information
   see the style guide.
1. Push commits to your fork.
1. Create a Github pull request from your topic branch.
1. Pull requests will be reviewed by one of the maintainers who may discuss,
offer constructive feedback, request changes, or approve the work. For more
information see the Code review guideline.
1. Upon receiving the sign-off of one of the maintainers you may merge your
   changes, or if you do not have permission to do that, you may request a
   maintainer to merge it for you.

## Attribution

This Contributing.md is adapted from Google
available at
<https://github.com/google/new-project/blob/master/docs/contributing.md>
