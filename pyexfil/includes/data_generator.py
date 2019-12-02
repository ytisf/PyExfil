#!/usr/bin/python

import sys
import uuid
import luhn
import names
import datetime

from faker import Faker
from random import Random, choice, randint, sample


class cTypes(object):
	VISA = 'VISA'
	MASTERCARD = 'MasterCard'
	AMEX = 'American Express'
	DISCOVER = 'Discover'
	DINERS = 'Diners'
	JCB = 'JCB'


CardTypes = cTypes()


PREFIX = {
	CardTypes.VISA: [
		['4', '5', '3', '9'],
		['4', '5', '5', '6'],
		['4', '9', '1', '6'],
		['4', '5', '3', '2'],
		['4', '9', '2', '9'],
		['4', '0', '2', '4', '0', '0', '7', '1'],
		['4', '4', '8', '6'],
		['4', '7', '1', '6'],
		['4']],
	CardTypes.MASTERCARD: [['5', '1'],
		['5', '2'],
		['5', '3'],
		['5', '4'],
		['5', '5'],
		['2', '2', '2', '1'],
		['2', '2', '2', '2'],
		['2', '2', '2', '3'],
		['2', '2', '2', '4'],
		['2', '2', '2', '5'],
		['2', '2', '2', '6'],
		['2', '2', '2', '7'],
		['2', '2', '2', '8'],
		['2', '2', '2', '9'],
		['2', '2', '3'],
		['2', '2', '4'],
		['2', '2', '5'],
		['2', '2', '6'],
		['2', '2', '7'],
		['2', '2', '8'],
		['2', '2', '9'],
		['2', '3'],
		['2', '4'],
		['2', '5'],
		['2', '6'],
		['2', '7', '0'],
		['2', '7', '1'],
		['2', '7', '2', '0']],
	CardTypes.AMEX: [['3', '4'], ['3', '7']],
	CardTypes.DISCOVER: [['6', '0', '1', '1']],
	CardTypes.DINERS: [
		['3', '0', '0'],
		['3', '0', '1'],
		['3', '0', '2'],
		['3', '0', '3'],
		['3', '6'],
		['3', '8']],
	CardTypes.JCB: [['3', '5']]
}

EMAIL_PROVIDERS = [
	'gmail.com', 'yahoo.com', 'hotmail.com', 'naver.com',
	'hotmail.co.uk', 'hotmail.fr', 'msn.com', 'orange.fr',
	'comcast.net', 'protonmail.com', 'live.com', 'rediffmail.com',
	'free.fr', 'gmx.de', 'yandex.com', 'yandex.ru', 'ymail.com',
	'libero.it', 'outlook.com', 'uol.com.br', 'bol.com.br',
	'mail.ru', 'cox.net', 'hotmail.it', 'sbcglobal.net',
	'sfr.fr', 'live.fr', 'verizon.net', 'live.co.uk',
	'googlemail.com', 'yahoo.es', 'ig.com.br', 'live.nl',
	'bigpond.com', 'terra.com.br', 'yahoo.it', 'neuf.fr',
	'yahoo.de', 'alice.it', 'rocketmail.com', 'att.net',
	'laposte.net', 'facebook.com', 'bellsouth.net', 'yahoo.in',
	'hotmail.es', 'charter.net', 'yahoo.ca', 'yahoo.com.au',
	'rambler.ru', 'hotmail.de', 'tiscali.it', 'shaw.ca',
	'yahoo.co.jp', 'sky.com', 'earthlink.net', 'optonline.net',
	'freenet.de', 't-online.de', 'aliceadsl.fr', 'virgilio.it',
	'home.nl', 'qq.com', 'telenet.be', 'me.com', 'yahoo.com.ar',
	'tiscali.co.uk', 'yahoo.com.mx', 'voila.fr', 'gmx.net',
	'mail.com', 'planet.nl', 'tin.it', 'live.it', 'ntlworld.com',
	'arcor.de', 'yahoo.co.id', 'frontiernet.net', 'hetnet.nl',
	'live.com.au', 'yahoo.com.sg', 'zonnet.nl', 'club-internet.fr',
	'juno.com', 'optusnet.com.au',
]


def _build_number(prefix, generator, length=16):
	"""
	Generate the actual nubmber and vet Luhn
	:param prefix: list, int, prefix.
	:param generator: random generator
	:param length: length to be returned
	:return: stringed number
	"""
	candidate = prefix

	while len(candidate) < (length - 1):
		digit = str(generator.choice(range(0, 10)))
		candidate.append(digit)

	joined_number = ''.join(candidate)
	joined_number_w_digit = luhn.append(joined_number)
	return joined_number_w_digit


def _getPrefix(names):
	"""
	Returns a random prefix from the type of card choosen
	:param names: Name as in CardTypes
	:return: list, ints
	"""
	return choice(PREFIX[names])


def GenerateCard(kind):
	"""
	[Wrapper] Generate credit card.
	:param kind: CardTypes Types
	:return: [company, number]
	"""
	now = datetime.datetime.now()
	rndGenerator = Random()
	rndGenerator.seed()
	pref = _getPrefix(kind)
	ccnumber = _build_number(pref, rndGenerator)
	cvv = sample(range(0, 9), 3)
	cvv = ''.join(str(x) for x in cvv)
	exp_year = randint(now.year+2, now.year+10)
	exp_month = str(randint(1,12)).zfill(2)
	return [kind, ccnumber, cvv, "%s/%s" % (exp_year, exp_month)]


def GenerateName():
	"""
	Stupid wrapper.
	:return: Name. Duha!
	"""
	return names.get_full_name()


def AddressWrapper():
	"""
	Again, wrapper to it will be easier for me to remember.
	:return: Address as str
	"""
	fake = Faker()
	return fake.address()


def EmailGenerator(firstname, lastname, domain=""):
	"""
	Generate email address
	:param firstname: ...
	:param lastname: ...
	:param domain: if you want a specific domain -put it in
	:return: string, email address
	"""
	firstname = firstname.lower()
	lastname = lastname.lower()
	g = randint(5, 1000)
	if g % 4 == 0:
		pref = "%s.%s" % (firstname[0], lastname)
	elif g % 3 == 0:
		pref = "%s%s" % (lastname, firstname[0])
	elif g % 5 == 0:
		pref = "%s_%s" % (firstname, lastname)
	elif g % 7 == 0:
		pref = "%s_%s" % (firstname[0:3], lastname)
	elif g % 10 == 0:
		pref = "%s_%s" % (lastname[0:1], firstname[0:2])
	elif g % 6 == 0:
		pref = "%s%s" % (lastname, firstname[0:1])
	else:
		pref = "%s%s" % (lastname, firstname)

	g = randint(1, 100)
	if g % 3 != 0: # should i add numbers? let's toss a coin heavier on one side.
		how_many_random_numbers = randint(2, 6)
		for i in range(0, how_many_random_numbers):
			pref += (str(randint(0,9)))

	if domain == "":
		pref = "%s@%s" % (pref, choice(EMAIL_PROVIDERS))
	else:
		pref = "%s@%s" % (pref, domain)
	return pref


def GenerateRow(delimiter=', '):
	CCvendor, _ = choice(list(PREFIX.items()))
	first, last = GenerateName().split(" ")
	card = GenerateCard(kind=CCvendor)
	addr = AddressWrapper().replace("\n", ", ")
	email = EmailGenerator(first, last)
	uid = uuid.uuid4()

	row_value = str(uid) + delimiter
	row_value += first + delimiter
	row_value += last + delimiter
	row_value += email + delimiter
	row_value += addr + delimiter
	row_value += card[1] + delimiter # PAN
	row_value += card[3] + delimiter # Exp
	row_value += card[0] + delimiter # Company
	row_value += card[2] # CVV
	row_value += "\n"
	return row_value


class CreateTestData:
	def __init__(self, rows=1000, output_location="test_data.csv"):
		"""
		Generate test data.
		:param rows: How many rows
		:param output_location: Where to write to the file to
		"""
		self.rows = rows
		self.file_name = output_location
		self._get_file_handler()

	def _get_file_handler(self):
		try:
			self.fhandler = open(self.file_name, 'w')
		except IOError as e:
			sys.stderr.write("Could not open file '%s'.\n" % self.file_name)
			sys.stderr.write("Reason: '%s'.\n" % e)
			raise Exception

	def Run(self):
		self.fhandler.write("UID, First Name, Last Name, "
		                    "Email Address, Address, CC PAN, "
		                    "CC Expiry, CC Vendor, CVV\n")
		for i in range(0, self.rows):
			self.fhandler.write("%s" % GenerateRow())
		self.fhandler.close()
		sys.stdout.write("%s data points created to '%s'.\n" % (self.rows, self.file_name))
		return True

