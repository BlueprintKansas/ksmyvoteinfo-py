import re
import dateutil.parser
from robobrowser import RoboBrowser

class KsMyVoteInfoResult(object):
  def __init__(self, soup, ballot_soup=None, district_soup=None, elections_soup=None):
    self.soup = soup
    self.ballot_soup = ballot_soup
    self.district_soup = district_soup
    self.elections_soup = elections_soup

  def norm_whitespace(self, val):
    return ' '.join(val.replace("\xa0", ' ').replace("\n", ' ').replace("\r", ' ').replace("\t", ' ').split())

  def parsed(self):
    els = []
    for el in self.soup:
      p = {}
      p['spans'] = el.find_all('span')
      p['labels'] = el.find_all('span', class_='label')
      p['data'] = el.find_all('span', class_='data')
      tree = {}
      for idx, label in enumerate(p['labels']):
        key = self.norm_whitespace(label.get_text())
        strings = p['data'][idx].stripped_strings
        val = '<br/>'.join(strings)
        tree[key] = self.norm_whitespace(val)
      p['tree'] = tree
      els.append(p)

    if self.ballot_soup: # only if we have one Result
      els[0]['sample_ballots'] = []
      for ballot_link in self.ballot_soup:
        href = ballot_link.get('href')
        text = ballot_link.get_text()
        els[0]['sample_ballots'].append({'href':KsMyVoteInfo.base_url + '/' + href, 'text':text})

    if self.district_soup:
      els[0]['districts'] = []
      for row in self.district_soup:
        if not row.find_all('td'):
          continue
        name = row.find_all('td')[0]
        dtype = row.find_all('td')[1]
        if not dtype:
          continue
        els[0]['districts'].append({'name':name.get_text(), 'type':dtype.get_text()})

    if self.elections_soup:
      els[0]['elections'] = []
      for row in self.elections_soup:
        if not row.find_all('td'):
          continue
        cells = row.find_all('td')
        date = cells[0].get_text()
        name = cells[1].get_text()
        etype = cells[2].get_text()
        how = cells[3].get_text()
        els[0]['elections'].append({'date':date, 'name':name, 'type':etype, 'how':how})

    return els

# end result class

class KsMyVoteInfo(object):

  version = '0.7'
  base_url = 'https://myvoteinfo.voteks.org/VoterView'
  registrant_search_url = base_url + '/RegistrantSearch.do'

  def __init__(self, **kwargs):
    self.url = self.__class__.registrant_search_url
    if 'url' in kwargs:
      self.url = kwargs['url']

  COUNTY_CODES = {
    "Allen": "308700",
    "Anderson": "308800",
    "Atchison": "305500",
    "Barber": "305700",
    "Barton": "301000",
    "Bourbon": "308900",
    "Brown": "305200",
    "Butler": "307200",
    "Chase": "301900",
    "Chautauqua": "307300",
    "Cherokee": "310500",
    "Cheyenne": "302900",
    "Clark": "304100",
    "Clay": "301100",
    "Cloud": "301200",
    "Coffey": "307400",
    "Comanche": "305800",
    "Cowley": "307500",
    "Crawford": "301300",
    "Decatur": "302500",
    "Dickinson": "303900",
    "Doniphan": "308000",
    "Douglas": "301800",
    "Edwards": "308200",
    "Elk": "307600",
    "Ellis": "300100",
    "Ellsworth": "303500",
    "Finney": "310100",
    "Ford": "304200",
    "Franklin": "301600",
    "Geary": "308600",
    "Gove": "309400",
    "Graham": "302800",
    "Grant": "304300",
    "Gray": "304400",
    "Greeley": "310300",
    "Greenwood": "307700",
    "Hamilton": "308400",
    "Harper": "305900",
    "Harvey": "303600",
    "Haskell": "304500",
    "Hodgeman": "308300",
    "Jackson": "305300",
    "Jefferson": "301700",
    "Jewell": "302600",
    "Johnson": "305600",
    "Kearny": "308100",
    "Kingman": "306000",
    "Kiowa": "306100",
    "Labette": "309000",
    "Lane": "309600",
    "Leavenworth": "301500",
    "Lincoln": "303700",
    "Linn": "309100",
    "Logan": "309700",
    "Lyon": "300200",
    "Marion": "303800",
    "Marshall": "305400",
    "McPherson": "304000",
    "Meade": "304600",
    "Miami": "300300",
    "Mitchell": "307100",
    "Montgomery": "309300",
    "Morris": "302000",
    "Morton": "304700",
    "Nemaha": "304900",
    "Neosho": "309200",
    "Ness": "309500",
    "Norton": "303000",
    "Osage": "302100",
    "Osborne": "306700",
    "Ottawa": "306800",
    "Pawnee": "308500",
    "Phillips": "306600",
    "Pottawatomie": "305000",
    "Pratt": "306200",
    "Rawlins": "302300",
    "Reno": "303200",
    "Republic": "306500",
    "Rice": "303300",
    "Riley": "300400",
    "Rooks": "306900",
    "Rush": "310400",
    "Russell": "303400",
    "Saline": "300600",
    "Scott": "309800",
    "Sedgwick": "300500",
    "Seward": "304800",
    "Shawnee": "301400",
    "Sheridan": "302400",
    "Sherman": "300900",
    "Smith": "307000",
    "Stafford": "306300",
    "Stanton": "300700",
    "Stevens": "310200",
    "Sumner": "306400",
    "Thomas": "303100",
    "Trego": "302700",
    "Wabaunsee": "302200",
    "Wallace": "309900",
    "Washington": "305100",
    "Wichita": "310000",
    "Wilson": "307800",
    "Woodson": "307900",
    "Wyandotte": "300800",
  }


  def lookup(self, *, first_name, last_name, dob, county=None):
    if county and county not in self.COUNTY_CODES:
        raise Exception("Invalid county: %s" %(county))

    browser = RoboBrowser(user_agent='ksmyvoteinfo ua', parser='html.parser')
    browser.open(self.url)
    form = browser.get_forms()[0] #(name_='registrantSearchForm')
    date = dateutil.parser.parse(dob)
    form['nameFirst'] = first_name
    form['nameLast'] = last_name
    form['county'] = self.COUNTY_CODES[county] if county else ''
    form['dobMonth'] = date.strftime('%m')
    form['dobYear'] = date.strftime('%Y')
    form['dobDay'] = date.strftime('%d')
    #print(form)
    browser.submit_form(form)

    if browser.select('#registrant'):
      return KsMyVoteInfoResult(
        browser.select('#registrant'),
        browser.select('.sampleBallot'),
        browser.select('#districts table tr'),
        browser.select('#voting-history table table tr')
      )
    elif re.search(u'multiple possible results', str(browser.parsed)):
      return KsMyVoteInfoResult(browser.select('.search-result'))
    else:
      return False

