'''
scrape_national_counts queries all 51 politico pages and scrapes election data, saving it in nested dictionaries.
write_national_counts saves to flat csv file, one candidate per row.

Requires States.txt, a file with all US states.

Gabe Gaster, November 13, 2012
'''

import httplib2
import BeautifulSoup
from collections import defaultdict

def to_lower(string):
	return string.lower()

def remove_spaces(string):
	return string.replace(" ","-")

def url2soup(url):
	h = httplib2.Http('.cache')
	page = h.request(url, "GET")[1]
	return BeautifulSoup.BeautifulStoneSoup(page)
	
def soup2table_rows(soup):
	tables = soup.findAll('table')
	if len(tables) == 1:
		# there might be only one county in the state!
		return tables[0].findAll('tr')
	elif len(tables)==0:
		return False
	else:
		return tables[1].findAll('tr')

def is_header(soup):
	return bool(soup.findAll(attrs='results-county'))

def is_column(soup):
	return bool(soup.findAll(scope='col'))

def is_row(soup):
	return bool(soup.findAll(scope='row'))

def fetch_county_from_header(soup):
	return soup.findAll(attrs='results-county')[0].contents[0]

def fetch_party(soup):
	out =  soup.findAll(attrs='results-party')[0].contents[0].contents[0]
	if type(out) == BeautifulSoup.Tag:
		return out.contents[0]
	else:
		return out

def fetch_candidate(soup):
	out = soup.findAll(attrs='results-candidate')[0].contents[0]
	if type(out) == BeautifulSoup.Tag:
		return out.contents[0]
	else:
		return out

def fetch_percent(soup):
	out = soup.findAll(attrs='results-percentage')[0].contents[0]
	if type(out) == BeautifulSoup.Tag:
		return out.contents[0]
	else:
		return out

def fetch_num(soup):
	out = soup.findAll(attrs='results-popular')[0].contents[0]
	if type(out) == BeautifulSoup.Tag:
		return out.contents[0]
	else:
		return out

def process_rows(rows):
	counts = defaultdict(dict)
	county_name = ""
	for row in rows:
		if is_column(row):
			continue
		data = {}
		if is_header(row):
			county_name = fetch_county_from_header(row)
			won = True
		else:
			won = False
		data['party'] = fetch_party(row)
		data['candidate'] = fetch_candidate(row)
		data['num'] = fetch_num(row)
		data['won'] = str(won)
		data['percent'] = fetch_percent(row)

		counts[county_name][fetch_party(row)] = data

	return counts

def is_single_county(soup):
	tables = soup.findAll('table')
	return len(tables) == 1

def scrape_national_counts():
	h = httplib2.Http('.cache')
	url = 'http://www.politico.com/2012-election/results/president/'

	text = open("States.txt").read()
	states = text.split("\n")
	states.remove("")
	states = map(to_lower,states)
	states = map(remove_spaces,states)
	
	national_counts = {}
	
	for state in states:
		url_iter = url+state+"/"
		print "querying state %s"%state
		soup = url2soup(url_iter)
		rows = soup2table_rows(soup)
		if rows:
			national_counts[state] = process_rows(rows)

	return national_counts

def write_national_counts(national_dict):
	f = open("elections.csv",'w')
	f.write("State|County|Party|Candidate|Num|Percent|Won\n")
	
	for state,state_dict in national_dict.items():
		for county,county_dict in state_dict.items():
			for party,row in county_dict.items():
				one_line = [state,
					    county,
					    party,
					    row['candidate'],
					    row['num'],
					    row['percent'],
					    row['won'],
					    ]
				stuff = "|".join(one_line)+"\n"
				f.write(stuff)
	f.close()

def __main__():
	data = scrape_national_counts()
	write_national_counts(data)
