import time
import math

# set to 1 for minimal debug info
# set to 2 for normal debug info
# set to 3 for extended debug info
DEBUG = 2

# divisible amounts are also integers internally, but COIN can be used
# for smoother expressions, e.g.: the amount "0.1" (BTC) can be expressed 
# by "0.1*COIN" (BTC) instead of "10000000" (BTC)
COIN = 100000000

# smart properties and currencies are simply represented by strings
cBITCOIN = "BTC"
cMASTERCOIN = "MSC"
cIndiv1 = "Indiv1"
cIndiv2 = "Indiv2"

class Order(object):
    __slots__ = [
        'id', 'timestamp', 'currency_for_sale', 'amount_for_sale',
        'currency_desired', 'unit_price', 'unit_price_inverse']

    _id = -1

    def _get_new_id(self):
        Order._id = Order._id + 1
        return Order._id

    def __init__(
            self, currency_for_sale, amount_for_sale, currency_desired,
            amount_desired, timestamp=None):

        assert 0 < int(math.floor(amount_for_sale))
        assert 0 < int(math.floor(amount_desired))
        assert currency_for_sale != currency_desired

        # assign ascending, unique id
        self.id = self._get_new_id()        

        # represents block height and transaction index
        if None == timestamp:
            timestamp = int(round(time.time() * 1000))
        self.timestamp = timestamp
        
        self.currency_for_sale = currency_for_sale
        self.currency_desired = currency_desired
        
        # unit prices can be considered as worst accepted trading price
        self.unit_price = float(amount_desired) / float(amount_for_sale)
        self.unit_price_inverse = 1.0 / self.unit_price

        # only whole units can be sold!
        self.amount_for_sale = int(math.floor(amount_for_sale))

        # this should never be not the case unless forced
        assert self.amount_for_sale == amount_for_sale

        log("Creating new order...")
        log(self)

    def get_desired_amount(self):
        """The desired amount is derived from the price limit."""

        desired_amount = float(self.amount_for_sale) * self.unit_price
        return desired_amount
    
    def would_accept(self, unit_price_proposed):
        """Accept (inverse) unit prices which are considered as better."""

        order_accepted = self.unit_price <= unit_price_proposed
        return order_accepted

    def matches_with(self, order_new):
        """Determine, if this order can be matched against another one.
        
        See valid_match() for details."""

        return Order.valid_match(self, order_new)    

    @staticmethod
    def valid_match(order_existing, order_new):
        """Determine, if two orders can be matched."""

        # TODO: evaluate the effect of rounding of fractional amounts
        # TODO: evaluate the effect of rounding of fractional amounts
        # TODO: evaluate the effect of rounding of fractional amounts
        
        # is there ever the case where an order is chosen as valid 
        # match, but later not accepted after rounding of fractional 
        # amounts during order execution?

        # existing order's currency id for sale is the same as the new 
        # order's currency id desired
        currency_for_sale_match = \
            order_existing.currency_for_sale == order_new.currency_desired

        # existing order's currency id desired is the same as the new 
        # order's currency id for sale
        currency_desired_match = \
            order_existing.currency_desired == order_new.currency_for_sale
        
        # existing order's unit price is less than or equal to the 
        # reciprocal of the new order's unit price
        reciprocal = order_new.unit_price_inverse
        accepted_price = order_existing.would_accept(reciprocal)

        # existing order's address is not the new order's address
        no_self_trade = True

        # existing order is still open (not completely fulfilled or 
        # canceled)
        open_order = True

        # only match, if all requirements are fulfilled
        valid_match = \
            currency_for_sale_match \
            and currency_desired_match \
            and accepted_price \
            and no_self_trade \
            and open_order

        return valid_match

    @staticmethod
    def create_sell_order(
            amount_for_sale, price, currency_for_sale, currency_desired):
        """Create a new sell order.

        This is a helper for more intuitive order creation. The price 
        is nominated in the currency of the property sold for."""

        amount_desired = float(amount_for_sale) * float(price)

        # explicitly round down to a whole number to avoid problems 
        # based on strange floating point representations
        amount_for_sale = int(math.floor(amount_for_sale))

        sell_order = Order(currency_for_sale, amount_for_sale,
                           currency_desired, amount_desired)

        return sell_order

    @staticmethod
    def create_buy_order(
            amount_desired, price, currency_desired, currency_for_sale):
        """Create a new buy order.

        This is a helper for more intuitive order creation. The price 
        is nominated in the currency of the property bought with."""

        amount_for_sale = float(amount_desired) * float(price)

        # explicitly round down to a whole number to avoid problems 
        # based on strange floating point representations
        amount_for_sale = int(math.floor(amount_for_sale))

        buy_order = Order(currency_for_sale, amount_for_sale,
                          currency_desired, amount_desired)

        return buy_order

    # visual helper
    # visual helper
    # visual helper

    def print_id(self):
        return "[ID %i]" % self.id

    def print_timestamp(self):
        return "%s time: %i" % (self.print_id(), self.timestamp)

    def print_currency_for_sale(self):
        return "%s currency for sale: %s" % \
            (self.print_id(), self.currency_for_sale)

    def print_currency_desired(self):
        return "%s currency desired: %s" % \
            (self.print_id(), self.currency_desired)

    def print_amount_for_sale(self):
        return "%s amount for sale: %i %s" % \
            (self.print_id(), self.amount_for_sale, self.currency_for_sale)

    def print_amount_desired(self):
        return "%s amount desired: %i %s" % \
            (self.print_id(), self.get_desired_amount(),
             self.currency_desired)

    def print_unit_price(self):
        return "%s unit price: %s %s/%s" % \
            (self.print_id(), formatted_decimal(self.unit_price),
             self.currency_desired, self.currency_for_sale)
    
    def print_inverse_unit_price(self):
        return "%s inverse unit price: %s %s/%s" % \
            (self.print_id(), formatted_decimal(self.unit_price_inverse),
             self.currency_for_sale, self. currency_desired)

    def __str__(self):
        return "%s\n%s\n%s\n%s\n%s" % \
            (self.print_timestamp(), self.print_amount_for_sale(), 
             self.print_amount_desired(), self.print_unit_price(), 
             self.print_inverse_unit_price())

    def __repr__(self):
        return str(self)


class MatchingEngine:
    __slots__ = ['orders']

    def __init__(self):
        self.orders = []

    def get_orders(self, currency_for_sale, currency_desired):
        """Get orders with the desired currency pair.

        Orders are sorted by price whereby old orders are prioritized."""

        potential_orders = \
            filter(lambda order:
                   order.currency_for_sale == currency_for_sale and 
                   order.currency_desired == currency_desired, self.orders)

        # sort orders by price and timestamp
        # timestamp represents block height and transaction position
        potential_orders.sort(key=lambda order: order.timestamp, reverse=True)
        potential_orders.sort(key=lambda order: order.unit_price, reverse=True)

        return potential_orders

    def get_best_match(self, new_order):
        """Find best match for an order.

        The "perfect match" is an order with inverted currency pair and
        best price. In the case of more than one candidate, the oldest 
        one is chosen."""

        assert None != new_order

        best_match = None

        # get all orders with desired currency pair, sorted
        potential_orders = self.get_orders(new_order.currency_desired,
                                           new_order.currency_for_sale)

        # only orders with a favorable unit price are considered
        potential_matches = \
            filter(lambda order:
                   order.matches_with(new_order), potential_orders)

        # the best match should be the last item in the list
        if len(potential_matches) > 0:
            best_match = potential_matches.pop()

        log("Best match for Order %s:" % new_order.print_id())
        log(best_match)

        return best_match    

    def add_order(self, order_new):
        """Add an order to the orderbook.
        
        New orders are matched against existing ones and in the case
        of a match, the orders are executed. Partially filled orders 
        are updated and added back to the orderbook. This is done 
        recursively until no more matches are found."""

        assert None != order_new

        log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        log("Adding Order %s to the orderbook..." % order_new.print_id())
        log(order_new)

        # the best match is the cheapest and oldest one
        best_match = self.get_best_match(order_new)

        if best_match == None:
            self._append_order(order_new)
        else:
            self.execute_orders(best_match, order_new)

        log("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    def execute_orders(self, order_old, order_new):
        """Match and execute two orders.
      
        The traded amounts are based on the "desired" amount" and not
        on the amounts "up for sale". The "amount for sale" may rather
        be considered as threshold or upper limit.

        In the case an existing order is filled partially, the order 
        is removed from the orderbook and an updated order is added.

        A new order is matched against existing orders until the order 
        is completely filled or no potential match is found."""

        assert None != order_old
        assert None != order_new
        assert 0 < int(math.floor(order_old.amount_for_sale))
        assert 0 < int(math.floor(order_new.amount_for_sale))

        # extra variables are used for better readability
        a1_available = order_old.amount_for_sale
        a2_available = order_new.amount_for_sale
        a1_unit_price = order_old.unit_price
        a2_unit_price = order_new.unit_price
        
        # only whole units can be traded!
        a1_desired = math.ceil(order_old.get_desired_amount())
        a2_desired = math.ceil(order_new.get_desired_amount())
        
        # these are the traded amounts
        amount_to_a2 = min(a2_desired, a1_available)
        amount_to_a1 = math.ceil(amount_to_a2 * a1_unit_price)
        
        # these are the amounts for updated orders
        a1_updated_amount_desired = a1_desired - amount_to_a1
        a2_updated_amount_desired = a2_desired - amount_to_a2

        a1_updated_amount_for_sale = \
            float(a1_updated_amount_desired) / a1_unit_price
        a2_updated_amount_for_sale = \
            float(a2_updated_amount_desired) / a2_unit_price

        # rounding up was chosen, because the user still receives the 
        # amount he wanted in the first place in total and in the case 
        # of rounding down the price may be "below market price"
        a1_updated_amount_for_sale = math.ceil(a1_updated_amount_for_sale)
        a2_updated_amount_for_sale = math.ceil(a2_updated_amount_for_sale)                
        
        # check, if price after rounding up is within accepted range
        updated_unit_price = float(amount_to_a1) /  float(amount_to_a2)
        updated_unit_price_inverse = 1.0 / updated_unit_price
        assert order_old.would_accept(updated_unit_price)
        assert order_new.would_accept(updated_unit_price_inverse)

        # make sure not more than remaining units are sold
        assert a1_updated_amount_for_sale <= (a1_available - amount_to_a2)
        assert a2_updated_amount_for_sale <= (a2_available - amount_to_a1)        
        
        ################################
        log("A1 offers %i %s and wants %i %s at >= %s %s/%s." % \
            (a1_available, order_old.currency_for_sale, a1_desired,
                order_old.currency_desired,
                formatted_decimal(order_old.unit_price),
                order_old.currency_desired, order_old.currency_for_sale),
            level=3)

        log("A2 wants %i %s and offers %i %s at <= %s %s/%s." % \
            (a2_desired, 
                order_new.currency_desired, a2_available,
                order_new.currency_for_sale, 
                formatted_decimal(order_new.unit_price_inverse),
                order_new.currency_for_sale, order_new.currency_desired),
            level=3)

        log("A1 gives %i %s for %i %s at %s %s/%s." % \
            (amount_to_a2, order_old.currency_for_sale,
                amount_to_a1, order_old.currency_desired,
                formatted_decimal(updated_unit_price), 
                order_old.currency_desired, order_old.currency_for_sale),
            level=3)

        log("A2 gives %i %s for %i %s." % \
            (amount_to_a1, order_new.currency_for_sale, 
                amount_to_a2, order_new.currency_desired),
            level=3)

        log("A1 now has %i %s remaining and wants %i %s." % \
            ((a1_available-amount_to_a2), order_old.currency_for_sale,
                (a1_desired-amount_to_a1), order_old.currency_desired),
            level=3)
        
        log("A2 now has %i %s remaining and wants %i %s." % \
            ((a2_available-amount_to_a1), order_new.currency_for_sale, 
                (a2_desired-amount_to_a2), order_new.currency_desired),
            level=3)
        ################################

        # display information about the trade
        log("%i %s traded for %i %s at %s %s/%s." % \
            (amount_to_a1, order_old.currency_desired,
             amount_to_a2, order_new.currency_desired,
             formatted_decimal(updated_unit_price),
             order_old.currency_desired, order_new.currency_desired),
            level=1)

        # display state information of the existing order
        if a1_updated_amount_desired > 0:
            log("Order %s filled partially and will be replaced." % \
                order_old.print_id(), level=1)          
        else:
            log("Order %s filled completely." % \
                order_old.print_id(), level=1)

        # since there was a trade the orders are replaced by updated 
        # ones and the existing order is removed from the orderbook        
        # remember:
        # the new order was matched on the fly and was not yet added!
        self._remove_order(order_old)

        # display state information about the new order
        # note: this is done before the existing order is replaced for
        # better readability
        if a2_updated_amount_desired > 0:
            log("Order %s filled partially and will be updated." % \
                order_new.print_id(), level=1)
        else:
            log("Order %s filled completely." % \
                order_new.print_id(), level=1)

        # replace existing order
        if a1_updated_amount_desired > 0:
                                    
            # update existing order whereby all attributes are copied
            # except the available and desired amounts
            old_updated = Order(
                order_old.currency_for_sale, a1_updated_amount_for_sale, 
                order_old.currency_desired, a1_updated_amount_desired, 
                order_old.timestamp)

            # add the replaced existing order to the orderbook..
            # note: this should not trigger a new order execution
            self.add_order(old_updated)        
        
        # update new order
        if a2_updated_amount_desired > 0:

            # update new order whereby all attributes are copied except
            # the available and desired amounts
            new_updated = Order(
                order_new.currency_for_sale, a2_updated_amount_for_sale, 
                order_new.currency_desired, a2_updated_amount_desired, 
                order_new.timestamp)

            # add the updated new order to the orderbook..
            self.add_order(new_updated)
                
    def _append_order(self, order_new):
        """Adds an order to the orderbook."""

        assert None != order_new
        self.orders.append(order_new)
                        
        log("Added Order %s to the orderbook." % order_new.print_id(),
            level=1)

    def _remove_order(self, order_to_remove):
        """Removes an order from the orderbook."""

        assert None != order_to_remove
        self.orders.remove(order_to_remove)

        log("Removed Order %s." % order_to_remove.print_id(), level=1)

    def __str__(self):
        response = "Open Orders:"
        if not self.orders:
            response += "\nNo open orders available."
        for order in self.orders:
            response += "\n" + str(order)
        return response

    def __repr__(self):
        return str(self)


def formatted_decimal(number):
    """Format any number to 0.0#######."""
    float_number = float(number)
    s = "{:.8f}".format(float_number)
    # remove zeros on the right
    trimmed = s.rstrip('0')
    # make sure there is at least one zero on the right
    if trimmed.endswith('.'):
        return trimmed + '0'
    else:
        return trimmed

def log(msg, level=2):
    """Filter output results."""
    if level <= DEBUG:
        print(msg)

if __name__ == "__main__":
    engine = MatchingEngine()

    #create two orders
    orderA = Order(cIndiv2, 20, cIndiv1, 10)
    orderB = Order(cIndiv1, 12, cIndiv2, 17)

    ##add orders to the orderbook
    engine.add_order(orderA)
    engine.add_order(orderB)
    
    # show open orders
    print(engine)

    #engine.add_order(Order.create_sell_order(COIN*0.35, 0.23, cMASTERCOIN, cBITCOIN))
    #engine.add_order(Order.create_sell_order(COIN*2.25, 0.23, cMASTERCOIN, cBITCOIN))    
    #engine.add_order(Order.create_sell_order(COIN*15, 0.2155, cMASTERCOIN, cBITCOIN))
    #engine.add_order(Order.create_buy_order(COIN*20, 0.25, cMASTERCOIN, cBITCOIN))
    #print(engine)