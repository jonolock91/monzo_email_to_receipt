import re


class RegexFormat():

	def __init__(self, merchant_name):

		# Create underscore maerchant name we can map to a method
		merchant_name = merchant_name.lower()
		merchant_name = merchant_name.replace(' ', '_')
		merchant_name = merchant_name.replace('.co.uk', '')
		merchant_name = merchant_name.replace('.com', '')

		self.regex_fmt = getattr(self, merchant_name, False)
		if not self.regex_fmt:
			raise Exception('Regex format not found for ', merchant_name)
		else:
			self.regex_fmt()
			print('Using ', merchant_name, ' regex format expression...')

	def asos_orders(self):
		self.re_total = r'^Total.*\n([\d,]+(?:\.\d+)?)'
		self.re_line_item = r'(?P<line_item>.*)\n(?P<amount>[\d,]+(?:\.\d+)?)\nQTY: (?P<qty>[0-9]{1})'

		self.re_discounts = [
			(r'^Discount.*\n(?P<amount>[\d,]+(?:\.\d+)?)', 'Discount'),
			(r'^Gift Voucher.*\n(?P<amount>[-\d,]+(?:\.\d+)?)', 'Gift voucher')
		]

	def get_discount(self, email_body):
		discounts = []

		for re_discount in self.re_discounts:
			match = re.search(re_discount[0], email_body, re.M)
			if match:
				discounts.append({
					'name': re_discount[1],
					'amount': match.group('amount')
				})

		return discounts
