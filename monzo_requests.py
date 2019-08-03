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

	def find_transaction(self, merchant_name, transaction_date, total_amount):
		# Find single transaction by merchant name, date & total.

		merchant_name_map = {
			'asos orders': 'asos',
			'gymshark uk': 'gymshark',
			'myprotein': 'myprotein'
		}

		# Get transactions
		if not self.transactions:
			self.transactions = self.get_transactions()

		matching_transaction = None
		for transaction in self.transactions:
			if transaction['merchant'] is None:
				continue

			if (
				transaction['merchant']['name'].lower() == merchant_name_map[merchant_name] and
				transaction['amount'] == -total_amount and
				transaction['created'].startswith(transaction_date)
			):
				matching_transaction = transaction
				break

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
