---
title: Stable order for outputs
layout: docs
permalink: /docs/stable-outputs/
---

Data structures such as [Perl
hashes](http://perldoc.perl.org/functions/keys.html), [Python
dictionaries](https://docs.python.org/library/stdtypes.html#mapping-types-dict)
and [sets](https://docs.python.org/library/stdtypes.html#set-types-set-frozenset),
[Rust std::collections::HashMap and
std::collections::Hashset](https://doc.rust-lang.org/stable/std/collections/index.html#iterators),
or [Ruby Hash objects](https://ruby-doc.org/core/Hash.html) will list their keys
in a different order on every run to limit [algorithmic complexity
attacks](http://perldoc.perl.org/perlsec.html#Algorithmic-Complexity-Attacks).

Perl
----

The following Perl code will output the list in a different order on every run:

<div class="wrong">
{% highlight perl %}
foreach my $package (keys %deps) {
    print MANIFEST, "$package: $deps[$packages]";
}
{% endhighlight %}
</div>

To get a deterministic output, the easiest way is to explicitly sort the keys:

<div class="correct">
{% highlight perl %}
foreach my $package (sort keys %deps) {
    print MANIFEST, "$package: $deps[$packages]";
}
{% endhighlight %}
</div>

For Perl, it is possible to set `PERL_HASH_SEED=0` in the environment. This
will result in hash keys always being in the same order. See
[perlrun(1)](http://perldoc.perl.org/perlrun.html) for more information.

Python
------

Python users can similarly set the environment variable
[PYTHONHASHSEED](https://docs.python.org/using/cmdline.html#envvar-PYTHONHASHSEED).
When set to a given integer value, orders in dictionaries and sets will be the
same on every run.

Rust
----

When iterating over the keys or entries of a `HashMap`, the order is [explicitly
undefined](https://doc.rust-lang.org/stable/std/collections/struct.HashMap.html)
and depends on a random seed:

> By default, HashMap uses a hashing algorithm selected to provide resistance
> against HashDoS attacks. The algorithm is randomly seeded, and a reasonable
> best-effort is made to generate this seed from a high quality, secure source
> of randomness provided by the host without blocking the program.

Iterating over a HashMap can cause reproducible builds issue when:

- done inside a `build.rs` file
- done in a function that's directly or indirectly called from a `build.rs` file

This can often be fixed by replacing `HashMap` with
[`BTreeMap`](https://doc.rust-lang.org/stable/std/collections/index.html#use-a-btreemap-when).
There's a [real-world example](https://github.com/gtk-rs/gtk-rs-core/pull/1840)
of how this was fixed.

General
-------
Beware that the [locale settings]({{ "/docs/locales/" | relative_url }})
might affect the output of some sorting functions or the `sort` command.
