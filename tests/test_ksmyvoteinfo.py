import pytest
import re
from pprint import pprint
from ksmyvoteinfo import KsMyVoteInfo

def test_init():
  assert KsMyVoteInfo()

def test_lookup_fail():
  kmvi = KsMyVoteInfo()
  r = kmvi.lookup(first_name='No', last_name='Such', dob='2000-01-01')
  assert r == False

def test_lookup_pass():
  kmvi = KsMyVoteInfo()
  r = kmvi.lookup(first_name='Kris', last_name='Kobach', dob='1966-03-26')
  pprint(r.parsed())
  assert r.parsed()[0]['tree']['Political Party'] == 'Republican'
  assert r.parsed()[0]['tree']['Address'] == '2150 East 300 Road, Lecompton, KS 66050'
