import pytest
from ksmyvoteinfo import KsMyVoteInfo

def test_init():
  assert KsMyVoteInfo()

def test_lookup():
  kmvi = KsMyVoteInfo()
  r = kmvi.lookup(first_name='No', last_name='Such', dob='2000-01-01', county='Douglas')
  print(r)
  assert r
