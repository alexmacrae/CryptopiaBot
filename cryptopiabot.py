from modules.cryptopia_api import Api
import time
import random
import json
import os
import smtplib
import subprocess
import platform
from modules import network
import configparser

IS_DEBIAN = platform.linux_distribution()[0].lower() == 'debian'  # Determine if running on RPi (True / False)

if IS_DEBIAN:

    w = network.Wifi()

    CONFIG_FILE_PATH = '/boot/setup.ini'
    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str  # allows case sensitivity

    def get_option_by_name(option_name):
        if config.read(CONFIG_FILE_PATH):
            for section in config.sections():
                for name, value in config.items(section):
                    if name == option_name:
                        return value

    ssid = get_option_by_name('ssid')
    psk = get_option_by_name('psk')

    if ssid != '' and psk != '':
        if w.exists(ssid) == False:
            print 'Found wireless network credentials in %s' % CONFIG_FILE_PATH
            w.save(ssid, psk)
            subprocess.call(['reboot'])

# TODO LIST:
# > Web GUI:
#       > Webserver + website [IN PROGRESS]
#       > Update blacklist and wishlist JSON files [DONE]
#       > View running status
#       > View BTC balance[DONE]
#       > View all coins balances [DONE]
#       > REBOOT
# > Manage settings:
#       > Wait time between loops
#       >
#
# > Manage held coins:
#       > To hodl or to flip (default)
#       > If hodl is set, an optional coin number target can also be set. All new BTC will go towards topping this coin up
#       >
#

DIR = os.path.dirname(__file__)

json_obj = json.load(open(os.path.join(DIR, 'json/settings.json')))
settings = json_obj['settings']
secrets = json_obj['secrets']

print "Loaded settings from JSON:\r\n"
print json.dumps(settings, indent=2)

#############
# Constants #
#############

VERBOSE_MODE = True

WAIT_TIME = 60.0 * float(settings['WAIT_TIME'])  # time to wait between loops

MINIMUM_PURCHASE_CRYPTOPIA = float(settings['MINIMUM_PURCHASE_CRYPTOPIA'])  # minimum required by Cryptopia to make a trade.
MINIMUM_PURCHASE = float(settings['MINIMUM_PURCHASE'])  # minimum required to invest in a coin. 0.0005 is the minimum for Cryptopia - but let's use double that.
MINIMUM_PURCHASE = MINIMUM_PURCHASE * 1.003  # Cryptopia has a 0.2% trading fee. Let's make it 0.3% just in case.

DEFAULT_BUY_PRICE = settings['DEFAULT_BUY_PRICE']  # Either market price or lowest price

FIRST_SELL_TARGET_PERC = float(settings['FIRST_SELL_TARGET_PERC'])  # percentage increase target to trigger sell
SECOND_SELL_TARGET_PERC = float(settings['SECOND_SELL_TARGET_PERC'])  # percentage increase target to trigger sell - this is in case of a big spike
THIRD_SELL_TARGET_PERC = float(settings['THIRD_SELL_TARGET_PERC'])  # percentage increase target to trigger sell - this is in case of a big spike

FIRST_SELL_AMOUNT = float(settings['FIRST_SELL_AMOUNT'])  # When FIRST_TARGET is hit, how much do we sell of this coin
SECOND_SELL_AMOUNT = float(settings['SECOND_SELL_AMOUNT'])  # When SECOND_TARGET is hit, how much do we sell of this coin
THIRD_SELL_AMOUNT = float(settings['THIRD_SELL_AMOUNT'])  # When THIRD_TARGET is hit, how much do we sell of this coin

JSON_FILE_PATH = os.path.join(DIR, 'json/ownedcoins.json')
JSON_DUMP_FILE_PATH = JSON_FILE_PATH
SECRETS_PATH = os.path.join(DIR, 'json/secrets.json')
WISHLIST_PATH = os.path.join(DIR, 'json/wishlist.json')
BLACKLIST_PATH = os.path.join(DIR, 'json/blacklist.json')

EMAIL_TO = settings['EMAIL_TO']
EMAIL_FROM = secrets['email']['username']
EMAIL_FROM_NAME = settings['EMAIL_FROM_NAME']
GMAIL_USER = EMAIL_FROM
GMAIL_PASSWORD = secrets['email']['password']

KEY = secrets['cryptopia']['key']
SECRET = secrets['cryptopia']['secret']

error_starting_up = False
error_message = ''


class CryptopiaBot:
    def __init__(self):

        self.api_wrapper = Api(KEY, SECRET)

        self.coins_owned = {}

        self.coins_owned_and_ordered = {}

        self.coins_in_openorders = []

    def run(self):

        """Run bot, run!"""

        global error_message, error_starting_up

        try:

            wishlist_json = json.load(open(WISHLIST_PATH))
            self.wishlist = {}
            for wl_key, wl_value in wishlist_json.iteritems():
                self.wishlist.update({wl_key: wl_value})

            print "Wishlist: ", self.wishlist

            blacklist_json = json.load(open(BLACKLIST_PATH))
            self.blacklist = []
            for bl_coin in blacklist_json.iteritems():
                self.blacklist.append(bl_coin[0])

            print "Blacklist: ", self.blacklist

            self.coins_owned = self.rebuild_dict(self.get_coinsjson())

            self.coins_owned_and_ordered = self.get_and_join_owned_and_openorders()

            self.sell_available_coins()  # see if any currencies have coins that are not in sell trades. If not, set sell orders.

            btc_balance = self.get_btc_balance()  # if some coins have been sold, maybe we will have enough to buy a new random coin...

            if btc_balance >= MINIMUM_PURCHASE:

                is_searching = True

                new_coin = None

                hodl = False

                print "\r\n============================================= FIND NEW COIN TO BUY ============================================="

                print "  Checking the wishlist [%s] for a user-selected coin..." % WISHLIST_PATH

                if len(self.wishlist) > 0:
                    key, value_dict = self.wishlist.items()[0]

                    wl_coin_name = value_dict.get('Symbol')

                    for owned_coin_name in self.coins_owned_and_ordered.iterkeys():

                        if owned_coin_name == wl_coin_name:
                            print "  [%s] is already owned. Skipping.." % wl_coin_name

                    # Select first coin from wishlist

                    new_coin = wl_coin_name

                    hodl = value_dict.get('hodl')

                    self.wishlist.pop(wl_coin_name)  # remove coin from wishlist json

                    with open(WISHLIST_PATH, mode='w') as f:
                        f.write(json.dumps(self.wishlist, indent=2))

                else:

                    print "  No coins in wishlist - randomly selecting a coin from the market..."

                    while is_searching:
                        new_coin = self.get_new_random_coin()

                        is_searching = self.check_new_coin(new_coin, self.coins_owned_and_ordered)

                print "Successfully chosen %s as new coin to invest in" % new_coin

                print "================================================================================================================="

                buy_message = self.set_buy_trade(new_coin, self.get_buy_price(new_coin))

                if buy_message == None:

                    print 'ERROR: couldn\'t buy [%s]' % new_coin

                else:

                    self.add_coin_to_json(new_coin, str(hodl))

                    coin_message = "Successfully chosen %s as new coin to invest in" % new_coin

                    self.sendemail("Buy", coin_message + "\r\n" + buy_message, new_coin)


            else:

                print "\r\n------------------------------------------------------------------\r\n" \
                      "Need %.8fBTC to buy something. Currently have %.8fBTC.\r\n" \
                      "------------------------------------------------------------------\r\n" % (MINIMUM_PURCHASE, btc_balance)
            error_starting_up = False

        except Exception as e:

            # error_message =  e
            error_message = 'ERROR IN run():'

            error_starting_up = True
            print 'ERROR IN run():'
            # print e

    def get_coins_in_openorders(self):

        """Returns a list of coins in trades as ['DOT', 'ETH', 'DOGE', ...] """

        openorders, error = self.api_wrapper.get_openorders('')

        coins_array = []

        if error != None:

            print error

        else:

            for order in openorders:

                coin = order['Market'].split('/')[0]

                if coin not in coins_array:
                    coins_array.append(coin)

            self.coins_in_openorders = coins_array

        return coins_array

    def rebuild_dict(self, d, is_marketdata=False):

        """Rebuild the json dict with coin symbols as an item's index eg "DOGE": {"SellVolume": 18063.10, ...}"""

        new_dict = {}

        if is_marketdata:

            for item in d:
                symbol = item['Label'].split('/')[0]

                new_dict.update({symbol: item})

        else:

            if type(d) is dict:
                if d.has_key('coins'):
                    d = d['coins']

            for key, value in d.iteritems():
                new_dict.update({key: value})

        return new_dict

    def get_and_join_owned_and_openorders(self):

        """Get list of owned coins and join it with any new coins in open buy orders"""
        coins_owned = self.rebuild_dict(self.get_coinsjson())  # get the list of currently owned currencies from the json

        coins_in_openorders = self.get_coins_in_openorders()  # list of coins ['BTC', 'DOT', ...]

        if len(coins_in_openorders) > 0:

            for coin_openorder in coins_in_openorders:

                coin_exists = False

                if coins_owned.has_key(coin_openorder):
                    coin_exists = True

                if coin_exists == False:
                    coins_owned.update({coin_openorder: {'Symbol': coin_openorder, 'hodl': 'False'}})

        return coins_owned

    def get_coinsjson(self):

        """JSON"""

        data = json.load(open(JSON_FILE_PATH))

        return data

    def add_coin_to_json(self, coin, hodl='False'):

        coin_item = {coin: {u'Symbol': coin, u'hodl': hodl}}

        self.coins_owned_and_ordered.update(coin_item)

        with open(JSON_DUMP_FILE_PATH, mode='w') as f:
            f.write(json.dumps(self.coins_owned_and_ordered, indent=2))

        print self.coins_owned_and_ordered

    def remove_coin_from_json(self, coin):
        """Removes coin from JSON if they have been completely sold."""
        # TODO: can be improved. eg if we try to delete every coin, the nature of pop() will cause an issue
        # - but not a major one since the wait time between loops is quite small

        is_removed = False

        if coin in self.coins_owned_and_ordered:

            if coin not in self.coins_in_openorders:
                # if coin is NOT in any open trades. Safe to remove from json

                self.coins_owned_and_ordered.pop(coin)

                is_removed = True

        if is_removed:
            with open(JSON_DUMP_FILE_PATH, mode='w') as f:
                f.write(json.dumps(self.coins_owned_and_ordered, indent=2))

        return is_removed

    def get_btc_balance(self):
        """Available BTC to spend"""
        btc_data, error = self.api_wrapper.get_balance('BTC')

        available_btc = btc_data[0]['Total'] - btc_data[0]['HeldForTrades']

        return available_btc

    # def get_coin_balance(self, coin):
    #     """Get the balance of a selected coin"""
    #
    #     print '=== BALANCE FOR %s ===' % coin
    #
    #     balance, error = self.api_wrapper.get_balance(coin)
    #
    #     if error is not None:
    #         print 'ERROR: %s' % error
    #     else:
    #         print 'Held for trades: %.8f %s' % (balance['HeldForTrades'], coin)
    #         print 'Total balance  : %.8f %s \r' % (balance['Total'], coin)
    #         return balance['Total'] - balance['HeldForTrades']

    def get_buy_price(self, coin):
        """Get the buy price we want to use in the buy order. In this case we'll use the lowest, so it probably won't fill immediately"""

        coindata = self.api_wrapper.get_market(coin + '_BTC')[0]

        if DEFAULT_BUY_PRICE == 'low':

            return coindata['Low']  # Buy at the lowest

        elif DEFAULT_BUY_PRICE == 'market':

            return coindata['AskPrice']  # Buy immediately at market price

    def get_original_buy_price(self, coin):
        """Get the price the coin was originally bought at. This will determine what prices to set sell trades at."""

        trade_history = self.api_wrapper.get_tradehistory(coin + '_BTC')

        trade_history[0].sort(key=lambda x: x['TimeStamp'])

        for trade in trade_history[0]:
            if trade['Type'] == 'Buy':
                return trade['Rate']

    def print_marketdata(self, coin_name, marketdata):

        print '  LastPrice = %.8f' % marketdata[coin_name]['LastPrice']
        print '  AskPrice  = %.8f' % marketdata[coin_name]['AskPrice']
        print '  BidPrice  = %.8f' % marketdata[coin_name]['BidPrice']
        print '  High      = %.8f' % marketdata[coin_name]['High']
        print '  Low       = %.8f' % marketdata[coin_name]['Low']

    def sell_available_coins(self):

        """Check to see if any currencies have any coins NOT in trades, and set sell orders"""

        print 'Getting entire market data...'

        api_marketdata, marketdata_error = self.api_wrapper.get_markets('')

        marketdata = {}

        if marketdata_error != None:

            print marketdata_error

        else:

            marketdata = api_marketdata

            marketdata = self.rebuild_dict(marketdata, is_marketdata=True)

            # print marketdata

        api_all_balances, balances_error = self.api_wrapper.get_balance('')

        coins_owned_and_ordered = self.coins_owned_and_ordered

        coins_owned = self.coins_owned


        if balances_error != None:
            print balances_error
        else:

            for api_coin_balance in api_all_balances:

                coin_name = api_coin_balance['Symbol']

                if api_coin_balance['Total'] < 0.000001 and coin_name not in self.coins_in_openorders:

                    # print 'WARNING: Balance for [%s] is (pretty much) zero. Seeing if it\'s in any trades...' % coin_name
                    #
                    is_removed = self.remove_coin_from_json(coin_name)

                    if is_removed:
                        print ' * REMOVED [%s] FROM OWNEDCOINS.JSON *' % coin_name

                elif coin_name in self.coins_in_openorders and coin_name not in coins_owned_and_ordered:

                    print ' * %s IS IN A TRADE. ADDING TO OWNEDCOINS.JSON. *' % coin_name

                    self.add_coin_to_json(coin_name)

                elif coin_name != 'BTC' and coin_name not in self.blacklist:

                    print '\r\n=== CHECKING [%s] FOR AVAILABLE COINS TO SELL ===' % coin_name

                    if api_coin_balance['Symbol'] in coins_owned_and_ordered:

                        print ' - BALANCE FOR [%s]' % coin_name

                        if coins_owned_and_ordered[coin_name]['hodl'].lower() == "true":
                            print " ~~ WE MUST HODL THE [%s] ~~" % coin_name
                            continue  # ignore the rest of this iteration

                        print '     Held for trades: %.8f %s' % (api_coin_balance['HeldForTrades'], coin_name)
                        print '     Total balance  : %.8f %s\r' % (api_coin_balance['Total'], coin_name)

                        if api_coin_balance['Total'] < 0.000001:  # coin amount might not be exactly zero

                            self.remove_coin_from_json(coin_name)

                            print ' * REMOVING %s FROM JSON *' % coin_name

                        elif api_coin_balance['HeldForTrades'] == 0:

                            coin_message = " * %s HAS SELLABLE COINS *" % coin_name

                            print coin_message

                            self.print_marketdata(coin_name, marketdata)  # print marketdata

                            coin_btc_value = self.get_original_buy_price(coin_name) * api_coin_balance['Total']

                            if coin_btc_value >= MINIMUM_PURCHASE:

                                print api_coin_balance['Total'] * FIRST_SELL_AMOUNT / 100.0
                                print api_coin_balance['Total'] * SECOND_SELL_AMOUNT / 100.0
                                print api_coin_balance['Total'] * THIRD_SELL_AMOUNT / 100.0

                                sell_message = str(self.set_sell_trade(coin_name, api_coin_balance['Total'] * FIRST_SELL_AMOUNT / 100.0, FIRST_SELL_TARGET_PERC)) + "\r\n"
                                sell_message += str(self.set_sell_trade(coin_name, api_coin_balance['Total'] * SECOND_SELL_AMOUNT / 100.0, SECOND_SELL_TARGET_PERC)) + "\r\n"
                                sell_message += str(self.set_sell_trade(coin_name, api_coin_balance['Total'] * THIRD_SELL_AMOUNT / 100.0, THIRD_SELL_TARGET_PERC))

                            else:

                                sell_message = str(self.set_sell_trade(coin_name, api_coin_balance['Total'], FIRST_SELL_TARGET_PERC))

                            self.sendemail("Sell", coin_message + "\r\n" + sell_message, coin_name)

                        elif api_coin_balance['Total'] - api_coin_balance['HeldForTrades'] > 0.0001:  # and marketdata['LastPrice'] > self.get_original_buy_price(coin_name):

                            # If some coins are in trades already, this makes things tricky. Let's just sell the rest

                            coin_message = " * %s HAS SELLABLE COINS - BUT SOME COINS ARE IN TRADES * " \
                                           " *** TRADE THE REST AT A PRICE THAT RETURNS A PROFIT  ***" % coin_name

                            self.print_marketdata(coin_name, marketdata)  # print marketdata

                            orig_price = self.get_original_buy_price(coin_name)

                            coins_available = api_coin_balance['Total'] - api_coin_balance['HeldForTrades']

                            target_price_perc = FIRST_SELL_TARGET_PERC  # use original buy price as benchmark

                            if (orig_price * coins_available) * (target_price_perc / 100. + 1) < MINIMUM_PURCHASE_CRYPTOPIA:
                                # if benchmark doesn't meet cryptopia's minimum trade requirement 0.0005btc, find the price that will get us there

                                target_price_perc = ((((MINIMUM_PURCHASE_CRYPTOPIA + 0.000001) / coins_available) / orig_price) - 1) * 100.

                            sell_message = str(self.set_sell_trade(coin_name, coins_available, target_price_perc))

                            self.sendemail("Sell", coin_message + "\r\n" + sell_message, coin_name)

                        else:
                            print " * %s HAS NO SELLABLE COINS - SKIPPING *" % coin_name

                        if coins_owned.has_key(coin_name) == False:
                            print '[%s] IS NOT IN OWNEDCOINS.JSON -> ADDING IT...' % coin_name
                            self.add_coin_to_json(coin_name)

    def get_new_random_coin(self):
        """Retrieves a new random coin from the market"""
        all_coins = self.api_wrapper.get_markets('BTC')[0]

        if VERBOSE_MODE:
            # print all_coins
            for coin in all_coins:
                name = coin['Label'].split('/')[0]  # separate coin from /BTC in the string
                name = name + (' ' * (6 - len(name)))  # append spaces to short coin names for readability

                print '%s >> LastPrice = %.8f | AskPrice = %.8f | BidPrice = %.8f | High = %.8f | Low = %.8f | Change = %.2f%% | BaseVolume = %.2f %s' % \
                      (name, coin['LastPrice'], coin['AskPrice'], coin['BidPrice'], coin['High'], coin['Low'], coin['Change'], coin['BaseVolume'], 'BTC')

        rand = (random.randint(0, len(all_coins))) - 1
        selected_coin = all_coins[rand]

        print selected_coin['Label']
        print '    LastPrice   = %.8f' % selected_coin['LastPrice']
        print '    AskPrice    = %.8f' % selected_coin['AskPrice']
        print '    BidPrice    = %.8f' % selected_coin['BidPrice']
        print '    High        = %.8f' % selected_coin['High']
        print '    Low         = %.8f' % selected_coin['Low']
        print '    Change      = %.2f%%' % selected_coin['Change']
        print '    BaseVolume  = %.2f %s' % (selected_coin['BaseVolume'], 'BTC')

        return selected_coin['Label'].split('/')[0]  # remove the /BTC

        # not in json already
        # cant have 0 volume
        # change must be between -10% and 10%

    def check_new_coin(self, coin, jsondata):
        """Check that the randomly selected coin fits some criteria"""
        print " Checking to see if %s satisfies requirements" % coin


        if jsondata.has_key(coin):

            print '   %s exists in JSON >> Find a new coin...' % coin
            return True

        print '   - Does not exist in JSON >> Proceed...'

        coindata = self.api_wrapper.get_market(coin + '_BTC')[0]

        blacklist = json.load(open(BLACKLIST_PATH))

        if blacklist.has_key(coin):
            print '   %s is blacklisted >> Find a new coin...' % coin

            return True

        print '   - Does not exist in blacklist >> Proceed...'

        if coindata['BaseVolume'] == 0:
            print "   - Base volume (BTC) is 0 >> Find a new random coin..."
            return True  # will search for another random coin
        else:
            print '   - Base volume (BTC) is acceptable >> Proceed...'

        if coindata['Change'] < -20 or coindata['Change'] > 30:
            print "   - 24hr change (%.2f) does not fit criteria >> Find a new random coin..." % coindata['Change']
            return True  # will search for another random coin
        else:
            print "   - 24hr change (%.2f) fits criteria >> Proceed..."

        print " %s is good to use!" % coin

        return False

    def set_sell_trade(self, coin, amount_to_sell, sell_target):
        """Sell"""
        price = self.get_original_buy_price(coin) * (sell_target / 100.0 + 1)

        sellorder, error = self.api_wrapper.submit_trade(coin + "_BTC", 'Sell', price, amount_to_sell)

        if error != None:
            message = error
        else:
            message = "  SELL ORDER PLACED: %.2f %s @ %.8fBTC. TOTAL: %.8fBTC" % (amount_to_sell, coin, price, (price * amount_to_sell))
            # print sellorder

        print message

        return message

    def set_buy_trade(self, coin, price):
        """Buy"""

        print "  BUYING %.8f BTC worth of %s" % (MINIMUM_PURCHASE, coin)

        buy_coins = MINIMUM_PURCHASE / price

        buyorder, error = self.api_wrapper.submit_trade(coin + "_BTC", 'Buy', price, buy_coins)

        if error != None:
            print error
            return None
        else:
            message = "BUY ORDER PLACED: %.2f %s @ %.8fBTC. TOTAL: %.8fBTC" % (buy_coins, coin, price, (price * buy_coins))
            print "  " + message
            return message
            # print buyorder

    def sendemail(self, trade_type, body='', coin=''):

        if EMAIL_TO != '':

            try:

                from email.mime.text import MIMEText

                message = MIMEText(body)

                if trade_type == "Buy":
                    message['Subject'] = "BUY order [%s]" % coin
                elif trade_type == "Sell":
                    message['Subject'] = "SELL order [%s]" % coin
                elif trade_type == "running":
                    message['Subject'] = "CryptopiaBot is Running"
                elif trade_type == "error":
                    message['Subject'] = "CryptopiaBot Error"

                message['From'] = EMAIL_FROM_NAME + ' <' + EMAIL_FROM + '>'
                message['To'] = EMAIL_TO

                # If an authentication error is returned, try visiting:
                # https://accounts.google.com/DisplayUnlockCaptcha

                server = smtplib.SMTP('smtp.gmail.com:587')
                server.ehlo()
                server.starttls()
                server.login(GMAIL_USER, GMAIL_PASSWORD)
                server.sendmail(EMAIL_FROM, [EMAIL_TO], message.as_string())
                server.quit()

                print " >> Sent an email."

            except:

                print "ERROR: Something went wrong sending an email."


if KEY == '' and SECRET == '':

    print '\r\n ERROR: Please add your Cryptopia public and secret keys to json/settings.json'
    exit()

cb = CryptopiaBot()

time_start = 0

first_run = True

has_sent_error_email = False

while True:
    time_start = time.time()

    cb.run()

    print "\r\n  This loop took [%d seconds] to complete\r\n" % (time.time() - time_start)

    print "\r\n  [ WAIT %.2f MINUTES UNTIL NEXT RUN ]\r\n" % (WAIT_TIME / 60.0)

    if error_starting_up == False:
        if first_run:
            cb.sendemail('running')
            first_run = False
    elif error_starting_up == True:
        if has_sent_error_email == False:
            cb.sendemail('error', body=error_message)
            has_sent_error_email = True

    time.sleep(WAIT_TIME)
