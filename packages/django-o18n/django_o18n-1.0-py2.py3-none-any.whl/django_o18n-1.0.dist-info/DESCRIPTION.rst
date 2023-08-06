Use case
--------

Django's [i18n_patterns][] prefixes URLs with a language code which may
contain a variant e.g. `/en`, `/fr`, `/fr-ca`.

o18n_patterns is similar but it prefixes URLs with a country code and a
language code e.g. `/us`, `/ca/en`, `/ca/fr`.

This is useful for websites that are mainly segmented by country rather than
by language.

[i18n_patterns]: https://docs.djangoproject.com/en/stable/topics/i18n/translation/#django.conf.urls.i18n.i18n_patterns

Features
--------

Some countries have a main language. In that case, the URL for the main
language only contains the country e.g. `/us`. URLs for other languages
contain the country and the language e.g. `/us/es`.

Some countries don't have a main language — and it may be a sensitive topic!
In that case, all URLs contain the country and the language e.g. `/ca/en` and
`/ca/fr`.

Unlike i18_patterns, o18n_patterns doesn't attempt to determine the country
and language and automatically redirect the user to the appropriate URL.

If an URL doesn't match a valid country and language combination, it doesn't
resolve with o18n_patterns and no country is activated. Vice-versa, if no
country is active, reversing an URL raises an exception.

