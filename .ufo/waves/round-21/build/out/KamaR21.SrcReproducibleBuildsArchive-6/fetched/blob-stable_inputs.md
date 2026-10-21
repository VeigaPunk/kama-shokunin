---
title: Stable order for inputs
layout: docs
permalink: /docs/stable-inputs/
---

If some step in the build depends on the order of its inputs,
make sure the order is stable across builds.

A typical example is creating an archive from the content of a
directory. Most filesystems do not guarantee that listing files in a
directory always results in the same order.

When sorting inputs, one must ensure that the sorting order is not affected by
the system locale settings. Different locales have different orders of e.g.
uppercase characters relative to lowercase characters.

Example: Makefile
-----------------

The following `Makefile`, run with GNU Make, can result in unreproducible
builds, as the `wildcard` function sorts according to the current locale:

<div class="wrong">
{% highlight makefile %}
SRCS = $(wildcard *.c)
tool: $(SRCS:.c=.o)
	$(CC) -o $@ $^
{% endhighlight %}
</div>

Solutions:

a) List all inputs explicitly and ensure they will be processed in that order.

<div class="correct">
{% highlight makefile %}
SRCS = util.c helper.c main.c
tool: $(SRCS:.c=.o)
	$(CC) -o $@ $^
{% endhighlight %}
</div>

b) Sort inputs with `sort` function (which does not take locale into account).

<div class="correct">
{% highlight makefile %}
SRCS = $(sort $(wildcard *.c))
tool: $(SRCS:.c=.o)
	$(CC) -o $@ $^
{% endhighlight %}
</div>

Example: tar
------------

Most `tar` implementations by default use the filesystem order when
descending directories:

<div class="wrong">
{% highlight sh %}
$ tar -cf archive.tar src
{% endhighlight %}
</div>

A solution is to use `find` and `sort` but the following might still
have differences when run under different locales:

<div class="wrong">
{% highlight sh %}
$ find src -print0 | sort -z |
    tar --no-recursion --null -T - -cf archive.tar
{% endhighlight %}
</div>

The locale used to sort files must be specified to avoid any surprises:

<div class="correct">
{% highlight sh %}
$ find src -print0 | LC_ALL=C sort -z |
    tar --no-recursion --null -T - -cf archive.tar
{% endhighlight %}
</div>

This might not be the only change required for [Tar and other archive
formats]({{ "/docs/archives/" | relative_url }}) as they
usually embed more metadata problems.
