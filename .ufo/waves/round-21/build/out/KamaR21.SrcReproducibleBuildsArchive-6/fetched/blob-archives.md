---
title: Archive metadata
layout: docs
permalink: /docs/archives/
---

Most archive formats record metadata that will capture details about the
build environment if no care is taken. File last modification time is
obvious, but file ordering, users, groups, numeric ids, and permissions
can also be of concern. Tar will be used as the main example but these tips
apply to other archive formats as well.

File modification times
-----------------------

Most archive formats will, by default, record file last modification
times, while some will also record file creation times.

Tar has a way to specify the modification time that is used for all
archive members:

{% highlight sh %}
$ tar --mtime='2015-10-21 00:00Z' -cf product.tar build
{% endhighlight %}

(Notice how `Z` is used to specify that time is in the UTC
[timezone]({{ "/docs/timezones/" | relative_url }}).)

For other archive formats, it is always possible to use `touch` to reset
the modification times to a [predefined value]({{ "/docs/timestamps/" | relative_url }})
before creating the archive:

{% highlight sh %}
$ find build -print0 |
    xargs -0r touch --no-dereference --date="@${SOURCE_DATE_EPOCH}"
$ zip -r product.zip build
{% endhighlight %}

In some cases, it is preferable to keep the original times for files
that have not been created or modified during the build process:

{% highlight sh %}
$ find build -newermt "@${SOURCE_DATE_EPOCH}" -print0 |
    xargs -0r touch --no-dereference --date="@${SOURCE_DATE_EPOCH}"
$ zip -r product.zip build
{% endhighlight %}

In `tar` >= 1.29, the `--clamp-mtime` flag can be used to only set the
time when the file is more recent than the value specified with `--mtime`:

{% highlight sh %}
$ tar --mtime='2015-10-21 00:00Z' --clamp-mtime -cf product.tar build
{% endhighlight %}

This has the benefit of leaving the original file modification time
untouched.

File ordering
-------------

When asked to record directories, most archive formats will read their
content in the order returned by the filesystem which is [likely to be
different on every run]({{ "/docs/stable-inputs/" | relative_url }}).

With version 1.28, GNU Tar has gained the `--sort=name` option which will
sort filenames in a locale independent manner:

{% highlight sh %}
# Works with GNU Tar 1.28
$ tar --sort=name -cf product.tar build
{% endhighlight %}

For older versions or other archive formats, it is possible to use
`find` and `sort` to achieve the same effect:

{% highlight sh %}
$ find build -print0 | LC_ALL=C sort -z |
    tar --no-recursion --null -T - -cf product.tar
{% endhighlight %}

Care must be taken to ensure that `sort` is called in the context of the
C locale to avoid any surprises related to collation order.

Users, groups and numeric ids
-----------------------------

Depending on the archive format, the user and group owning the file
can be recorded. Sometimes it will be using a string, sometimes using
the associated numeric ids.

When files belong to predefined system groups, this is not a problem,
but builds are often performed with regular users. Recording of the
account name or its associated ids might be a source of reproducibility
issues.

Tar offers a way to specify the user and group owning the file. Using
`0`/`0` and `--numeric-owner` is a safe bet, as it will effectively
record 0 as values:

{% highlight sh %}
$ tar --owner=0 --group=0 --numeric-owner -cf product.tar build
{% endhighlight %}

PAX headers
-----------

If GNU tar outputs the pax format (which is the default on some distributions), it adds files' ctime and atime. If, in addition, `POSIXLY_CORRECT` is set, it adds the PID of the tar process.

To avoid this, add to the tar call `--pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime` or `--format=gnu` (both only available in GNU tar),
or use `--format=ustar` if the limitations in that format are not a problem. Use the latter if possible and [portability](https://mgorny.pl/articles/portability-of-tar-features.html) is a concern.

File permissions
----------------

Permissions on build artifacts may vary, for example due to differing `umask` settings. The resulting permission differences may be reflected when archive files containing them are created.

When possible, it is preferable to create build artifacts using deterministic permissions so that variance does not arise.  However, sometimes it may be easier or more practical to configure static permissions later in the build, when the archive files are created.

To configure file permissions when creating a `tar` archive, you can use the `--mode` argument.  For example, to request that, by default, unpacked files should be readable by everyone by default, writable only by their owner, and to allow everyone to list directory/folder contents, add: `--mode=a=rX,u+w`

Full example
------------

The recommended way to create a Tar archive is thus:

<div class="correct">
{% highlight sh %}
# requires GNU Tar 1.28+
$ tar --sort=name \
      --mtime="@${SOURCE_DATE_EPOCH}" \
      --owner=0 --group=0 --numeric-owner \
      --pax-option=exthdr.name=%d/PaxHeaders/%f,delete=atime,delete=ctime \
      -cf product.tar build
{% endhighlight %}
</div>

Zip files
---------

Zip files can additionally store metadata in "extra file attributes". We believe these were intended as a cross-platform means of storing, say,  Extended Attributes on OS/2 as well as user/group information. Crucially, it can store multiple file timestamps on Unix, including creation, modification *and* access time. (NB. You may not see access time changes under Linux system is your filesystems are mounted with `noatime` or `norelatime`).

When creating `.zip` files, it is [recommended to use the `--no-extra` / `-X`](https://lists.reproducible-builds.org/pipermail/rb-general/2024-March/003283.html) argument to not save these fields. It is also recommended that [developers unzip archives with `TZ=UTC`](https://lists.reproducible-builds.org/pipermail/rb-general/2023-April/002927.html).

`git archive`
-------------

[`git archive`](https://git-scm.com/docs/git-archive) does
[not guarantee](https://lists.reproducible-builds.org/pipermail/rb-general/2022-October/002712.html)
deterministic output. It uses the commit time as recorded in the
referenced commit object when used with a commit ID or tag ID (but
not when given a tree ID). In practice, the `tar` output is typically
stable, but the internal `gzip` implementation is not. Using
`git archive --format=tar TAG | gzip -6 -n` is more reliable.

Post-processing
---------------

If tools do not support options to create reproducible archives, it is
always possible to perform post-processing.

[strip-nondeterminism](https://packages.debian.org/sid/strip-nondeterminism)
already has support to normalize Zip and Jar archives (with [limitations](https://bugs.debian.org/859103)). Custom scripts
like Tor Browser's
[re-dzip.sh](https://gitweb.torproject.org/builders/tor-browser-bundle.git/tree/gitian/build-helpers/re-dzip.sh)
might also be an option.

Static libraries
----------------

Static libraries (`.a`) on Unix-like systems are *ar* archives. Like
other archive formats, they contain metadata, namely timestamps, UIDs,
GIDs, and permissions. None are actually required for using them as
libraries.

GNU `ar` and other tools from
[binutils](https://www.gnu.org/software/binutils/) have a *deterministic
mode* which will use zero for UIDs, GIDs, timestamps, and use consistent
file modes for all files. It can be made the default by passing the
`--enable-deterministic-archives` option to `./configure`. It is already
enabled by default for some distributions[^distros-with-default] and so
far it seems to be pretty safe [except for
Makefiles](https://bugs.debian.org/798804) using targets like
`archive.a(foo.o)`.

When binutils is not built with deterministic archives by default, build
systems have to be changed to pass the right options to `ar` and
friends. `ARFLAGS` can be set to `Dcvr` with many build systems to turn on the
deterministic mode. Care must also be taken to pass `-D` if `ranlib` is
used to create the function index.

Another option is post-processing with
[strip-nondeterminism](https://packages.debian.org/sid/strip-nondeterminism)
or `objcopy`:

    objcopy --enable-deterministic-archives libfoo.a

The above does not fix [file ordering]({{ "/docs/stable-inputs/" | relative_url }}).

[^distros-with-default]: Debian since [version 2.25-6](https://tracker.debian.org/news/675691)/stretch, Ubuntu since version 2.25-8ubuntu1/artful 17.10.

Initramfs images
----------------

*cpio* archives are commonly used for initramfs images. The *cpio* header
format (see `man 5 cpio`) can contain device and inode numbers, which whilst
deterministic, can vary from system to system.

One way to filter these is by piping through bsdtar.

Example of non-deterministic code:
```
echo ucode.bin |
    bsdcpio -o -H newc -R 0:0 > ucode.img
```

Example of deterministic code:
```
echo ucode.bin |
    bsdtar --uid 0 --gid 0 -cnf - -T - |
    bsdtar --null -cf - --format=newc @- > ucode.img
```

Note that other issues such as timestamps may still require rectification prior
to archival.

## GNU Libtool

[GNU Libtool](https://www.gnu.org/software/libtool/) prior to `74c8993c` (first
included in version 2.2.7b) did not sort the find output. It appears that many
packages are bootstrapped with a version prior to this.

Confusingly, although [GNU GCC](https://gcc.gnu.org/)'s `ltmain.sh` claims to
have been generated by libtool 2.2.7a, GNU GCC actually maintains their own
version of `libtool.m4` and `ltmain.sh`, which fixed this issue independently
in `d41cd173e23`. This aforementioned change was first included in version
9.1.0, meaning that the reproducibility issue remains in GCC versions below
that.

## Gradle

See [Gradle reproducible archives](../jvm/#gradle) for more information.
