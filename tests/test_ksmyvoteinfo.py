import pytest
import re
from ksmyvoteinfo import KsMyVoteInfo

def test_init():
  assert KsMyVoteInfo()

def test_lookup_fail():
  kmvi = KsMyVoteInfo()
  r = kmvi.lookup(first_name='No', last_name='Such', dob='2000-01-01', county='Douglas')
  assert r == False

def test_lookup_pass():
  kmvi = KsMyVoteInfo()
  r = kmvi.lookup(first_name='Kris', last_name='Kobach', dob='1966-03-26', county='Douglas')
  regex = re.compile(r'Republican')
  matches = regex.search(r)
  assert matches is not None
