# How to contribute

>
> ## About actinia
>
> The cloud based geoprocessing platform actinia is able to ingest and
> analyse large volumes of data already present in the cloud. Due to the
> scalability of the cloud platform insights and tailor made information
> are delivered in near real-time.
>
> ## The name actinia?
>
> We adopted the name "actinia" from [sea anemones](https://en.wikipedia.org/wiki/Sea_anemone)
> which are a group of marine, predatory animals of the order Actiniaria which are named
> after the terrestrial flowering plant anemone with its colourful
> appearance. The idea is that the cloud based geoprocessing engine
> actinia filters information out of the rather unlimited amount of data
> available.
>
> Originally started as "GRaaS" - GRASS GIS as a Service - project, we changed the
> name to actinia in 2017.
>

## How to contribute to the actinia project

Actinia has been mainly developed by open source GIS developers of the GRASS GIS project.
Since the project is open source, all users, regardless of the profession or skill level,
have the ability to contribute to actinia. Here's a few suggestion on how:

- Help actinia users that is less experienced than yourself
- Write a bug report
- Request a new feature
- Write documentation for your favorite actinia usage
- Fix a bug
- Implement a new feature

In the following sections you can find some guidelines on how to contribute.
As actinia is managed on GitHub most contributions require that you have a GitHub
account. Familiarity with [issues](https://guides.github.com/features/issues/) and
the [GitHub Flow](https://guides.github.com/introduction/flow/) is an advantage.

## Help a fellow actinia user

While a mailing list still has to be set up, please *do not* use the GitHub issue tracker
as a support forum. Your question is much more likely to be answered by developers.

## Adding bug reports

Bug reports are handled in the [issue tracker](https://github.com/actinia-org/actinia-core/issues)
on actinia's home on GitHub. Writing a good bug report is not easy. But fixing a poorly
documented bug is not easy either, so please put in the effort it takes to create a
thorough bug report.

A good bug report includes at least:

- A title that quickly explains the problem
- A description of the problem and how it can be reproduced
- Version of actinia being used
- Version numbers of any other relevant software being used, e.g. operating system
- A description of what already has been done to solve the problem

The more information that is given up front, the more likely it is that a developer
will find interest in solving the problem. You will probably get follow-up questions
after submitting a bug report. Please answer them in a timely manner if you have an
interest in getting the issue solved.

Finally, please only submit bug reports that are actually related to actinia. If the
issue materializes in software that uses actinia it is likely a problem with that
particular software. Make sure that it actually is a actinia problem before you submit
an issue. If you can reproduce the problem only by using tools from actinia it is
definitely a problem with actinia.

## Feature requests

Got an idea for a new feature in actinia? Submit a thorough description of the new
feature in the [issue tracker](https://github.com/actinia-org/actinia-core/issues). Please
include any technical documents that can help the developer make the new feature a
reality. An example of this could be a publicly available academic paper that
describes a new geoprocessing method. Also, including a numerical test case will make it
much easier to verify that an implementation of your requested feature actually
works as you expect.

Note that not all feature requests are accepted.

## Write documentation

actinia is in dire need of better documentation. Any contributions of documentation
are greatly appreciated. The actinia documentation is available on
[actinia.mundialis.de](https://actinia.mundialis.de/).
Contributions to the documentation should be made as [Pull Requests](https://github.com/actinia-org/actinia-core/pulls)
on GitHub.

## Code contributions

### Legalese

Committers are the front line gatekeepers to keep the code base clear of improperly contributed code.
It is important to the actinia users, developers and the OSGeo community to avoid contributing any
code to the project without it being clearly licensed under the project license.

Generally speaking the key issues are that those providing code to be included in the repository
understand that the code will be released under the GPLv3 license, and that the person providing
the code has the right to contribute the code. For the committer themselves understanding about
the license is hopefully clear. For other contributors, the committer should verify the understanding
unless the committer is very comfortable that the contributor understands the license (for
instance frequent contributors).

If the contribution was developed on behalf of an employer (on work time, as part of a work project,
etc) then it is important that an appropriate representative of the employer understand that the
code will be contributed under the GPLv3 license. The arrangement should be cleared with an
authorized supervisor/manager, etc.

The code should be developed by the contributor, or the code should be from a source which can be
rightfully contributed such as from the public domain, or from an open source project under a
compatible license.

All unusual situations need to be discussed and/or documented.

Committer should adhere to the following guidelines, and may be personally legally liable for
improperly contributing code to the source repository:

- Make sure the contributor (and possibly employer) is aware of the contribution terms.
- Code coming from a source other than the contributor (such as adapted from another project)
  should be clearly marked as to the original source, copyright holders, license terms and so forth.
  This information can be in the file headers, but should also be added to the project licensing
  file if not exactly matching normal project licensing (LICENSE.txt).
- Existing copyright headers and license text should never be stripped from a file. If a copyright
  holder wishes to give up copyright they must do so in writing to the project steering committee
  before copyright messages are removed. If license terms are changed it has to be by agreement
  (written in email is ok) of the copyright holders.
- When substantial contributions are added to a file (such as substantial patches) the
  author/contributor should be added to the list of copyright holders for the file.
- If there is uncertainty about whether a change is proper to contribute to the code base, please
  seek more information from the project steering committee.

### Git workflow with actinia

This section collects best practices for the use of git in actinia development.

#### Commit message

Indicate a component name (eg a driver name), a short description and when
relevant, a reference to a issue (with 'fixes #' if it actually fixes it)

```bash
COMPONENT_NAME: fix bla bla (fixes #1234)

Details here...
```

### Additional Resources

- [General GitHub documentation](https://help.github.com/)
- [GitHub pull request documentation](https://help.github.com/articles/about-pull-requests/)

## Acknowledgements

This CONTRIBUTING file is mainly inspired by
[PROJ.4's rules](https://github.com/OSGeo/proj.4/blob/master/CONTRIBUTING.md) with some hints taken
from [GDAL's rules](https://github.com/OSGeo/gdal/blob/master/CONTRIBUTING.md) as well as
from [GRASS GIS's "get-involved"](https://grass.osgeo.org/get-involved/) page.
