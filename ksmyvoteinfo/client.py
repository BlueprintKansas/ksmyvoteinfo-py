import os
import re
import dateutil.parser
import http.client as http_client
import logging
import requests
from bs4 import BeautifulSoup

MOCK_REGISTRANT = [
    {
        "spans": [],
        "labels": [
            "<label class='control-label-important'>Political Party</label>",
            "<label class='control-label-important'>Precinct</label>",
        ],
        "data": [
            "<label class='control-data-important'>Democratic</label>",
            "<label class='control-data-important'>\n03 <br/>\n003                            </label>",
        ],
        "tree": {
            "Political Party": "Democratic",
            "Precinct": "03<br/>003",
            "Address": "123 Sunrise Drive Lawrence, KS 66044-9999",
            "County": "Douglas",
            "Name": "No Such Person",
        },
        "elections": [
            {
                "date": "11/02/2021",
                "name": "CG2021 City/School General",
                "type": "City General",
                "how": "Polling Place",
            },
            {
                "date": "08/03/2021",
                "name": "CP2021 City/School Primary",
                "type": "City Primary",
                "how": "Early",
            },
            {
                "date": "11/03/2020",
                "name": "2020 General Election",
                "type": "General",
                "how": "Advance",
            },
            {
                "date": "08/04/2020",
                "name": "2020 Primary Election",
                "type": "Primary",
                "how": "Advance",
            },
            {
                "date": "11/05/2019",
                "name": "2019 City/School General",
                "type": "City General",
                "how": "Polling Place",
            },
            {
                "date": "11/06/2018",
                "name": "2018 General Election",
                "type": "General",
                "how": "Polling Place",
            },
            {
                "date": "08/07/2018",
                "name": "2018 Primary Election",
                "type": "Primary",
                "how": "Polling Place",
            },
            {
                "date": "05/15/2018",
                "name": "Douglas Co Mail Ballot",
                "type": "Mail Ballot",
                "how": "Advance",
            },
            {
                "date": "11/07/2017",
                "name": "2017 City/School General",
                "type": "City General",
                "how": "Polling Place",
            },
            {
                "date": "08/01/2017",
                "name": "2017 City/School Primary",
                "type": "City Primary",
                "how": "Polling Place",
            },
            {
                "date": "05/02/2017",
                "name": "USD497 Mail Ballot",
                "type": "Mail Ballot",
                "how": "Advance",
            },
            {
                "date": "11/08/2016",
                "name": "2016 General Election",
                "type": "General",
                "how": "Polling Place",
            },
            {
                "date": "04/07/2015",
                "name": "2015 City/School General",
                "type": "City General",
                "how": "Polling Place",
            },
            {
                "date": "03/03/2015",
                "name": "2015 City Primary",
                "type": "City Primary",
                "how": "Polling Place",
            },
            {
                "date": "01/27/2015",
                "name": "USD497 Mail Ballot",
                "type": "Mail Ballot",
                "how": "Advance",
            },
            {
                "date": "11/04/2014",
                "name": "2014 General Election",
                "type": "General",
                "how": "Polling Place",
            },
        ],
        "polling": [
            {
                "name": "200 W 9th St Lawrence, KS 66044",
                "href": "https://maps.google.com/maps?q=200+W+9th+St,+Lawrence,+KS+66044 &oe=UTF-8&ie=UTF8&z=14",
            }
        ],
    }
]


class KsMyVoteInfoResult(object):
    def __init__(self, registrants):
        self.registrants = registrants

    def parsed(self):
        return self.registrants


class KsMyVoteInfoResultParser(object):
    def __init__(
        self,
        registrant_name,
        registrant_address,
        registrant_details,
        ballot_soup=None,
        district_soup=None,
        elections_soup=None,
        polling_soup=None,
    ):
        self.registrant_name = registrant_name
        self.registrant_address = registrant_address
        self.registrant_details = registrant_details
        self.ballot_soup = ballot_soup
        self.district_soup = district_soup
        self.elections_soup = elections_soup
        self.polling_soup = polling_soup

    def norm_whitespace(self, val):
        return " ".join(
            val.replace("\xa0", " ")
            .replace("\n", " ")
            .replace("\r", " ")
            .replace("\t", " ")
            .split()
        )

    def parsed(self):
        registrant = {}
        from ksmyvoteinfo.counties import KsMyVoteInfoCounties

        counties = KsMyVoteInfoCounties().names()

        for el in self.registrant_details:
            registrant["spans"] = el.find_all("span")
            registrant["labels"] = el.find_all(
                "label", class_="control-label-important"
            )
            registrant["data"] = el.find_all("label", class_="control-data-important")
            tree = {}
            for idx, label in enumerate(registrant["labels"]):
                key = self.norm_whitespace(label.get_text())
                strings = registrant["data"][idx].stripped_strings
                val = "<br/>".join(strings)
                tree[key] = self.norm_whitespace(val)
            registrant["tree"] = tree

        address_with_county = self.norm_whitespace(
            self.registrant_address[0].get_text()
        )
        address_matches = re.fullmatch(r"(.+) - ([a-z\ ]+)", address_with_county, re.I)
        address = address_matches.group(1)
        county = address_matches.group(2)
        if county not in counties:
            county = ""

        registrant["tree"]["Address"] = address
        registrant["tree"]["County"] = county
        registrant["tree"]["Name"] = self.norm_whitespace(
            self.registrant_name.get_text()
        )

        if self.ballot_soup:  # only if we have one Result
            registrant["sample_ballots"] = []
            for ballot_link in self.ballot_soup:
                href = ballot_link.get("href")
                text = ballot_link.get_text()
                registrant["sample_ballots"].append(
                    {"href": KsMyVoteInfo.base_url + "/" + href, "text": text}
                )

        if self.district_soup:
            registrant["districts"] = []
            for row in self.district_soup:
                if not row.find_all("td"):
                    continue
                name = row.find_all("td")[0]
                dtype = row.find_all("td")[1]
                if not dtype:
                    continue
                registrant["districts"].append(
                    {"name": name.get_text(), "type": dtype.get_text()}
                )

        if self.elections_soup:
            registrant["elections"] = []
            for row in self.elections_soup:
                if not row.find_all("td"):
                    continue
                cells = row.find_all("td")
                date = self.norm_whitespace(cells[0].get_text())
                name = self.norm_whitespace(cells[1].get_text())
                etype = self.norm_whitespace(cells[2].get_text())
                how = self.norm_whitespace(cells[3].get_text())
                registrant["elections"].append(
                    {"date": date, "name": name, "type": etype, "how": how}
                )

        if self.polling_soup:
            registrant["polling"] = []
            for location in self.polling_soup.select("a"):
                registrant["polling"].append(
                    {
                        "name": self.norm_whitespace(location.get_text()),
                        "href": location.get("href"),
                    }
                )

        # for backwards compat, return list of one
        return [registrant]


# end result class


class KsMyVoteInfo(object):
    version = "1.4"
    base_url = "https://myvoteinfo.voteks.org/voterview"
    registrant_search_url = base_url

    def __init__(self, **kwargs):
        self.url = self.__class__.registrant_search_url
        if "url" in kwargs:
            self.url = kwargs["url"]

        self.debug = "debug" in kwargs
        self.form_url = self.__class__.registrant_search_url + "/registrant/search"
        self.mock = os.environ.get("KSMYVOTEINFO_ENV", "prod") == "mock"

    def get_auth_token(self, body):
        startstr = b'<input name="__RequestVerificationToken" type="hidden" value="'
        tag_len = len(startstr)
        start_ind = body.find(startstr) + tag_len
        end_ind = body.find(b'"', start_ind)
        auth_token = body[start_ind:end_ind]
        return auth_token

    def get_search_key(self, body):
        key_string = b'var key = "'
        start_key_idx = body.find(key_string) + len(key_string)
        end_key_idx = body.find(b'"', start_key_idx)
        search_key = body[start_key_idx:end_key_idx]
        return search_key.decode(encoding="UTF-8")

    def lookup(self, *, first_name, last_name, dob):
        if self.mock:
            return KsMyVoteInfoResult(MOCK_REGISTRANT)

        if self.debug:
            http_client.HTTPConnection.debuglevel = 1
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True
        else:
            http_client.HTTPConnection.debuglevel = False

        date = dateutil.parser.parse(dob)

        session = requests.Session()
        form_page = session.get(self.url)  # cache session cookie
        form_page_text = form_page.content
        # pprint(form_page_text)

        auth_token = self.get_auth_token(form_page_text)
        # pprint(auth_token)

        payload = {
            "FirstName": first_name,
            "LastName": last_name,
            "DateOfBirth": date.strftime("%m/%d/%Y"),
            "DateOfBirth_[month]": date.strftime("%m"),
            "DateOfBirth_[day]": date.strftime("%d"),
            "DateOfBirth_[year]": date.strftime("%Y"),
            "__RequestVerificationToken": auth_token,
        }
        resp = session.post(self.form_url, data=payload)

        # print(resp.content)

        # if there are multiple/ambiguous results, look for signal string
        if b"ShowBusyIndicator" in resp.content:
            search_ids = re.findall(r'data-search-result-id="(\w+)"', str(resp.content))
            registrants = []
            for search_id in search_ids:
                registrant = self.fetch_registrant(session, search_id).parsed()
                registrants.append(registrant[0])

            return KsMyVoteInfoResult(registrants)

        else:
            # search result key
            search_key = self.get_search_key(resp.content)
            if search_key == "\r":
                return False

            # print("search_key:%s" %(search_key))

            return KsMyVoteInfoResult([self.fetch_registrant(session, search_key)])

    def fetch_registrant(self, session, search_key):
        # registrant
        registrant_url = self.url + "/registrant/searchresult/" + search_key
        registrant_page = BeautifulSoup(
            session.get(registrant_url).content, "html.parser"
        )
        # print(registrant_page.prettify())

        if registrant_page.select("h1"):
            elections = registrant_page.find("select", {"id": "cmboElection"})
            election_key = elections.find_all("option", selected=True)[0].get("value")
            # print('election_key={}'.format(election_key))
            precinct_key = registrant_page.find("input", {"id": "PrecinctPartKey"}).get(
                "value"
            )
            # print('precinct_key={}'.format(precinct_key))
            polling_url = (
                self.url
                + "/votingplace/getpollingplaceorvotecenters?KeyPrecinctPart={}&ElectionKey={}".format(
                    precinct_key, election_key
                )
            )
            polling_response = session.post(polling_url).content

            return KsMyVoteInfoResultParser(
                registrant_page.find("h1"),
                registrant_page.select("#labelResidenceAddress"),
                registrant_page.select("#reg-detail-header-row"),
                registrant_page.select(".divSampleBallots"),
                registrant_page.select("container body-content accordion"),
                registrant_page.select("#tableVotingHistory tbody tr"),
                BeautifulSoup(polling_response, "html.parser"),
            )
        # TODO check browser response code for 5xx
        else:
            return False
