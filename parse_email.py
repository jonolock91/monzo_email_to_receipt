from datetime import datetime, timedelta, timezone
import os
import re
import json
import copy
from decimal import Decimal

import requests

from monzo_auth import MonzoAuth
from monzo_requests import MonzoRequest
from receipt_format import receipt_format, line_item_format
from regex_formats import RegexFormat

month_abbr_to_int = {
	'January': '01',
	'Feburary': '02',
	'March': '03',
	'April': '04',
	'May': '05',
	'June': '06',
	'July': '07',
	'August': '08',
	'September': '09',
	'October': '10',
	'November': '11',
	'December': '12'
}


class Parse():

	def __init__(self):
		self.emails_dir = os.path.join(os.getcwd(), 'emails')
		self.emails = [
			os.path.join(self.emails_dir, e) \
				for e in os.listdir(self.emails_dir) if '.txt' in e
			]

		self.re_flags = re.M | re.I

		if not os.path.exists('old_emails'):
			os.makedirs('old_emails')

	def get_email_body(self, email):
		with open(email, 'r') as f:
			body = f.read()

		# Remove spaced characters
		updated_body = []
		for line in body.split('\n'):
			updated_body.append(line.strip())

		return '\n'.join(updated_body)

	def assemble_receipt(self, email_body, line_items, total_price):
		"""Return a dictionary for a receipt which we will PUT to Monzo"""

		receipt = receipt_format.copy()
		receipt['items'] = line_items
		receipt['total'] = total_price

		# Check total matches line items, ensure negative line items negate
		# the price.
		line_items_sum = 0
		for line_item in line_items:
			amount = line_item['amount'] * line_item.get('quantity', 1)
			line_items_sum += amount
		line_items_sum = line_items_sum

		if receipt['total'] != line_items_sum:
			raise Exception(
				'Line items: {0} dont match total price: {1}'.format(
					line_items_sum, receipt['total']
				)
			)

		# Extract merchant name and date from email so we can find the matching
		# Monzo transaction.
		merchant_name = self.get_merchant_name_from_email(email_body)

		if not merchant_name:
			raise Exception('No merchant name found')
		receipt['merchant_name'] = merchant_name

		day, month, year = re.search(
			r'Date: ([0-9]*) (.*) ([0-9]{4})',
			email_body
		).groups()

		# Sense check day so that it starts with a '0', e.g. '07'.
		if len(day) == 1:
			day = '0' + day

		email_date = '{y}-{m}-{d}'.format(y=year, m=month_abbr_to_int[month], d=day)
		receipt['email_received'] = email_date

		return receipt

	def get_total(self, email_body):
		amount = re.search(self.re_fmt.re_total, email_body, self.re_flags).group(1)
		return int(float(amount) * 100)

	def get_line_items(self, email_body, total_price):
		line_items = []

		for match in re.finditer(self.re_fmt.re_line_item, email_body, self.re_flags):
			line_item = copy.deepcopy(line_item_format)
			line_item['description'] = match.group('description')
			line_item['amount'] = round(float(match.group('amount')) * 100)

			# If we're aware a transaction cannot be the full amount of a
			# transaction then we can skip it if flagged.
			if (
				self.re_fmt.ignore_line_items_full_amount and
				line_item['amount'] == total_price
			):
				continue

			try:
				line_item['quantity'] = int(match.group('qty'))
			except IndexError as e:
				line_item['quantity'] = 1

			line_items.append(line_item)

		# Attempt to get discount if applicable
		for discount in self.re_fmt.get_discounts(email_body):
			line_item = copy.deepcopy(line_item_format)
			line_item['description'] = discount['description']
			line_item['amount'] = round(float(discount['amount']) * 100)

			line_item['amount'] = abs(line_item['amount']) * -1
			line_item['quantity'] = 1

			line_items.append(line_item)

		return line_items

	def get_delivery(self, email_body):
		if self.re_fmt.re_delivery:
			amount = re.search(self.re_fmt.re_delivery, email_body, re.M).group(1)
			line_item = copy.deepcopy(line_item_format)
			line_item['description'] = 'Delivery'
			line_item['amount'] = round(float(amount) * 100)
			return line_item
		return None

	def get_merchant_name_from_email(self, email_body):
		"""Return the merchant name from an email"""
		return re.search(
			r'From: (?P<from>.*)(,|<)', email_body
		).group('from').replace('"', '').strip()
	
	def run(self):

		# Auth Monzo
		monzo_auth = MonzoAuth()
		monzo_auth.get_access()

		# Create connection to monzo requests where we can hit Monzo API
		monzo_requests = MonzoRequest(
			monzo_auth.access_token,
			monzo_auth.account_id
		)

		# Parse txt emails looking for total price and line items

		for email in self.emails:
			print()
			print('PARSE EMAIL ---------')
			print(email)
			print('---------------------')
			print()

			# Get email body
			email_body = self.get_email_body(email)

			# Get merchant name from email so we know which regex expression
			# to use to parse email.
			merchant_name = self.get_merchant_name_from_email(email_body)

			if not merchant_name:
				raise Exception('No merchant name found')

			self.re_fmt = RegexFormat(merchant_name)

			# Get total price, line items and delivery
			total_price = self.get_total(email_body)
			line_items = self.get_line_items(email_body, total_price)

			delivery = self.get_delivery(email_body)
			if delivery:
				line_items.append(delivery)

			# Create Monzo receipt
			receipt = self.assemble_receipt(email_body, line_items, total_price)

			# Find the transaction from Monzo which matches the date we have
			# in our receipt, based on merchant name, date and total price.
			transaction = monzo_requests.find_transaction(
				receipt['merchant_name'],
				receipt['email_received'],
				receipt['total']
			)

			receipt['transaction_id'] = transaction['id']
			receipt['external_id'] = transaction['id']

			# Meta data for my transaction
			receipt['merchant_name'] = transaction['merchant']['name']
			receipt['created'] = transaction['created']

			# Create Monzo receipt
			monzo_requests.create_receipt_for_transaction(transaction, receipt)

		# Move parsed emails to another dir
		for email in self.emails:
			file_name = email.split('/')[-1]
			os.rename(email, '{}/old_emails/{}'.format(os.getcwd(), file_name))


if __name__ == '__main__':
	parse = Parse()
	parse.run()