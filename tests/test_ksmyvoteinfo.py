import os
from pprint import pprint
from ksmyvoteinfo import KsMyVoteInfo


def test_init():
    assert KsMyVoteInfo()


def test_lookup_fail():
    kmvi = KsMyVoteInfo()
    r = kmvi.lookup(first_name="No", last_name="Such", dob="2000-01-01")
    assert r is False


def test_lookup_pass():
    debug = os.environ.get("DEBUG", False)
    kmvi = KsMyVoteInfo(debug=debug)
    r = kmvi.lookup(first_name="Scott", last_name="Schwab", dob="1972-07-09")
    assert r
    if debug:
        pprint(r.parsed())
    assert r.parsed()
    assert r.parsed()[0]
    assert r.parsed()[0]["tree"]["Political Party"] == "Republican"
    assert (
        r.parsed()[0]["tree"]["Address"]
        == "12711 West 160th Terrace, Overland Park, KS 66221"
    )
