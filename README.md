KsMyVoteInfo
=========================

[![Build Status](https://travis-ci.org/BlueprintKansas/ksmyvoteinfo-py.svg?branch=master)](https://travis-ci.org/BlueprintKansas/ksmyvoteinfo-py)

KsMyVoteInfo Python module makes it easy to search the Kansas SOS voter registration site
for the registrant details. You supply first/last name, dob and county, this gem looks
it up and return the HTML snippet from the site.

Scrapes the https://myvoteinfo.voteks.org/voterview site.

# Example

```python
import ksmyvoteinfo
kmvi = ksmyvoteinfo.KsMyVoteInfo()
r = kmvi.lookup(first_name='No', last_name='Suchperson', dob='1966-03-26')
if r:
  print(r.parsed()[0]['tree'])
else:
  print("Sorry, No Suchperson is not registered")

```

# Development

```
% make deps
% make build
% make test
% make distcheck
% make dist
% make install
```

# Copyright and License

MIT license.

Copyright 2018 Blueprint Kansas
