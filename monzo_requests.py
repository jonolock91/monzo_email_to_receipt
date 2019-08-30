from datetime import datetime, timedelta
import json
import requests


class MonzoRequest():

	def __init__(self, access_token, account_id):
		self.access_token = access_token
		self.account_id = account_id
		self.monzo_api = 'https://api.monzo.com'
		self.transactions = None

	def get_transactions(self, limit=500):
		two_weeks_ago = datetime.now() - timedelta(days=90)
		two_weeks_ago_str = two_weeks_ago.strftime('%Y-%m-%d') + 'T00:00:00Z'

		r = requests.get(
			'{0}/transactions?expand[]=merchant&account_id={1}&limit={2}&since={3}'.format(
				self.monzo_api,
				self.account_id,
				limit,
				two_weeks_ago_str
			),
			headers={'Authorization': 'Bearer {}'.format(self.access_token)}
		)

		r_json = r.json()
		return r_json['transactions']

	def find_transaction(self, email_merchant_name, transaction_date, total_amount):
		# Find single transaction by merchant name, date & total.

		# Get transactions
		if not self.transactions:
			self.transactions = self.get_transactions()

		matching_transaction = None
		possible_matches_count = 0

		for transaction in self.transactions:
			if transaction['merchant'] is None:
				continue

			# First try to match the transaction to the email using the total
			if transaction['amount'] == -total_amount:

				# Check the email date and transaction date are the same, as
				# well as the merchant name.
				if (
					transaction['created'].startswith(transaction_date) and
					transaction['merchant']['name'].lower() in \
					email_merchant_name.lower()
				):
						matching_transaction = transaction
						break

				# If the merchant name doesn't match (e.g. eBay transactions
				# aren't marked up as eBay on Monzo)
				# -
				# OR
				# -
				# If the transaction date doesn't match the email date as it
				# could have been sent days apart
				# -
				# Then as long as the total amount matches and only one match is
				# found then we'll use it as a match.
				else:
					matching_transaction = transaction
					possible_matches_count += 1

			# More than 1 possible match found
			if possible_matches_count > 1:
				raise Exception(
					possible_matches_count,
					'possible matches found, can\'t confirm which one is an \
					exact match'
				)

		# Push to Monzo
		if matching_transaction:
			return matching_transaction
		raise Exception('No transaction found')

	def create_receipt_for_transaction(self, transaction, receipt):
		r = requests.put(
			'{0}/transaction-receipts'.format(self.monzo_api),
			headers={'Authorization': 'Bearer {}'.format(self.access_token)},
			data=json.dumps(receipt)
		)

		if r.status_code == 200:
			print()
			print('RECEIPT CREATED ------'),
			print(receipt['merchant_name'])
			print(receipt['total'])
			print(receipt['created'])
			print('----------------------')
			print()
		else:
			raise Exception('Creating receipt failed', r.status_code)
