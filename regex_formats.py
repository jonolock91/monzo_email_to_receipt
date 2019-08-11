import re


class RegexFormat():

	def __init__(self, merchant_name):

		# Normalize merchant name
		merchant_name = merchant_name.lower()
		merchant_name = merchant_name.replace(' ', '_')
		merchant_name = merchant_name.replace('.co.uk', '')
		merchant_name = merchant_name.replace('.com', '')

		# Defaults
		self.re_discounts = []
		self.re_delivery = None

		# Map merchant name to method
		self.regex_fmt = getattr(self, merchant_name, False)
		if self.regex_fmt:
			self.regex_fmt()
			print('Using ', merchant_name, ' regex format expression...')
		else:
			raise Exception('Regex format not found for ', merchant_name)

	def example_merchant(self):
		"""
		Each method should map to the merchant name we extract from the email
		"From: xyz" string.
		"""
		self.re_total = 'regex' # Order total
		self.re_line_item = 'regex' # Each line item: description, amount, qty
		self.re_delivery = 'regex' # Delivery cost

		# Represents each line item which reduces the order total, such as:
		# free delivery, discount code, sale.
		self.re_discounts = ['regex']

	def asos_orders(self):
		self.re_total = r'^Total.*\n([\d,]+(?:\.\d+)?)'
		self.re_line_item = r'(?P<description>.*)\n(?P<amount>[\d,]+(?:\.\d+)?)\nQTY: (?P<qty>[0-9]{1})'

		self.re_discounts = [
			(r'^Discount.*\n(?P<amount>[\d,]+(?:\.\d+)?)', 'Discount'),
			(r'^Gift Voucher.*\n(?P<amount>[-\d,]+(?:\.\d+)?)', 'Gift voucher')
		]

	def ebay(self):
		self.re_total = r'^Total.*\n£([\d,]+(?:\.\d+)?)'
		self.re_line_item = r'(?P<description>.*)\n*Total: £(?P<amount>[\d,]+(?:\.\d+)?)'

	def myprotein(self):
		self.re_total = r'^Total.*\n£([\d,]+(?:\.\d+)?)'
		self.re_line_item = r'(?P<description>.*)\nQuantity: (?P<qty>[0-9]{1}).*Price: £(?P<amount>[\d,]+(?:\.\d+)?)'
		self.re_delivery = r'^Delivery:.*\n£([\d,]+(?:\.\d+)?)'

	def gymshark_uk(self):
		self.re_total = r'^Total.*\n£([\d,]+(?:\.\d+)?)'
		self.re_line_item = r'(?P<description>.*)\nQuantity: (?P<qty>[0-9]{1}).*\n(?P<size>.*)\n£(?P<amount>[\d,]+(?:\.\d+)?)'
		self.re_delivery = r'^Shipping:.*\n£([\d,]+(?:\.\d+)?)'

	def get_discounts(self, email_body):
		discounts = []

		for re_discount in self.re_discounts:
			match = re.search(re_discount[0], email_body, re.M)

			if match:
				discounts.append({
					'description': match.group('description') if \
						match.group('description') else re_discount[1],
					'amount': match.group('amount')
				})

		return discounts
