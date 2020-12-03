import unittest
from amazon_url_utils import shorten_amazon_url


class TestAmazonUrlUtils(unittest.TestCase):

    def test_gp(self):
        testCase = 'https://www.amazon.com/gp/product/B08CGGRZ3M/ref=ppx_yo_dt_b_asin_title_o01_s00?ie=UTF8&psc=1'
        self.assertEqual(shorten_amazon_url(testCase), 'https://smile.amazon.com/gp/product/B08CGGRZ3M/')

    def test_dp(self):
        testCase = 'https://www.amazon.com/dp/B08CGGRZ3M/'
        self.assertEqual(shorten_amazon_url(testCase), 'https://smile.amazon.com/dp/B08CGGRZ3M/')

    def test_dp_product(self):
        # these links don't occur naturally in the wild
        testCase = 'https://www.amazon.com/dp/product/B08CGGRZ3M/1'
        self.assertEqual(shorten_amazon_url(testCase), 'https://smile.amazon.com/dp/B08CGGRZ3M/')

    def test_smile_unsupported(self):
        testCase = 'https://www.amazon.ca/dp/product/B08CGGRZ3M/1'
        self.assertEqual(shorten_amazon_url(testCase), 'https://www.amazon.ca/dp/B08CGGRZ3M/')

if __name__ == '__main__':
    unittest.main()