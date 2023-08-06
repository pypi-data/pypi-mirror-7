import urllib2
from bs4 import BeautifulSoup
import re



####################################################################
# API
####################################################################

class Horoscope:
  @staticmethod
  def get_todays_horoscope (sunsign):
  	url = "http://www.ganeshaspeaks.com/" + sunsign + "/" + sunsign + "-daily-horoscope.action"
	html_doc = urllib2.urlopen(url)
	soup = BeautifulSoup(html_doc.read())
	raw_data = str (soup.find_all(id="predData"))
	soup = BeautifulSoup (raw_data)
	date = soup.find_all('strong')[0].get_text ()
	soup = BeautifulSoup (raw_data)
	horoscope = soup.find_all(id="predData")[0].get_text ()
	horoscope = re.sub(r'\d+-\d+-\d+', r'', horoscope)
	horoscope = horoscope.replace ("\n", "")
	dict = {
		'date' : date,
		'horoscope' : horoscope,
		'sunsign' : sunsign
	}
	return dict
