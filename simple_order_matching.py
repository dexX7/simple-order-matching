import time
import math

import event

# the abundant usage of assertions is
# only inteded to find critical spots
# more than half of this code can probably 
# be deleted

class OrderStatus:
    New = 0
    PartiallyFilled = 1
    Filled = 2
    Canceled = 3

    AsString = {
        New: "new",
        PartiallyFilled: "partially filled",
        Filled: "filled completely",
        Canceled: "canceled",
    }

    
class Orderbook(object):
    __slots__ = ['orders']

    onListing = event.Event()
    onDelisting = event.Event()

    def __init__(self):
        self.orders = []

    def list(self, order):
        """Add an order to the orderbook."""
        assert isinstance(order, Order)
        self.orders.append(order)
        self.report_listing(order)

    def delist(self, order):
        """Remove an order from the orderbook."""
        assert isinstance(order, Order)
        self.orders.remove(order)
        self.report_delisting(order)

    def get_orders(self, currency_for_sale, currency_desired):
        """Get orders with the desired currency pair.

        Orders are sorted by price whereby old orders are prioritized."""        
        potential_orders = \
            list(filter(lambda order:
            order.currency_for_sale == currency_for_sale and 
            order.currency_desired == currency_desired, self.orders))

        # sort orders by price and timestamp
        # timestamp represents block height and transaction position
        potential_orders.sort(key=lambda order: order.timestamp)
        potential_orders.sort(key=lambda order: order.get_unit_price())
        return potential_orders

    @classmethod
    def report_listing(cls, order):
        """Fires an event for a new listings."""
        assert isinstance(order, Order)
        cls.onListing(order)

    @classmethod
    def report_delisting(cls, order):
        """Fires an event for a delisted entry."""
        assert isinstance(order, Order)
        cls.onDelisting(order)

        
class Order(object):
    __slots__ = [
        'id', 'timestamp', 'status',
        'currency_for_sale', 'amount_for_sale', 'initial_amount_for_sale',
        'currency_desired', 'amount_desired', 'initial_amount_desired']

    __id = -1

    onNewOrder = event.Event()
    onPendingAmountUpdate = event.Event()
    onUpdatedOrder = event.Event()
    onStatusUpdate = event.Event()

    def __init__(self, currency_for_sale, amount_for_sale, 
                 currency_desired, amount_desired, timestamp=None,
                 status=0):

        assert 0 < long(math.floor(amount_for_sale))
        assert 0 < long(math.floor(amount_desired))        
        assert currency_for_sale != currency_desired

        # assign ascending, unique id
        self.id = self.__get_new_id()
        
        # represents block height and transaction index
        if None == timestamp:
            timestamp = long(round(time.time() * 1000))

        self.timestamp = timestamp
        self.status = status
        self.currency_for_sale = currency_for_sale
        self.currency_desired = currency_desired

        # only whole units can be traded!
        self.amount_desired = long(math.ceil(amount_desired))
        self.amount_for_sale = long(math.floor(amount_for_sale))        

        # this should never be not the case unless forced
        assert self.amount_desired == amount_desired
        assert self.amount_for_sale == amount_for_sale        

        # store to calculate total amounts later
        self.initial_amount_desired = self.amount_desired
        self.initial_amount_for_sale = self.amount_for_sale        
                
        # report creation of new order
        self.report_new_order(self)
        
    def get_unit_price(self):
        """Upper price limit"""
        unit_price = float('Inf')
        if self.amount_for_sale > 0:
            unit_price = \
                float(self.amount_desired) / float(self.amount_for_sale)
        return unit_price

    def get_unit_price_inverse(self):
        """Inverse of upper price limit to match against other orders"""
        unit_price_inverse = float('NaN')
        if self.amount_desired > 0:
            unit_price_inverse = \
                float(self.amount_for_sale) / float(self.amount_desired)
        return unit_price_inverse

    def get_received_amount(self):
        received = self.initial_amount_desired - self.amount_desired
        return received
    
    def would_accept(self, unit_price_proposed):
        """Accept (inverse) unit prices which are considered as better."""
        unit_price = self.get_unit_price()
        order_accepted = unit_price <= unit_price_proposed
        return order_accepted
    
    def matches_with(self, order_new):
        """Determine, if this order can be matched against another one."""
        assert isinstance(order_new, Order)

        # is there ever the case where an order is chosen as valid 
        # match, but later not accepted after rounding of fractional 
        # amounts during order execution?

        # existing order's currency id for sale is the same as the new 
        # order's currency id desired
        currency_for_sale_match = \
            self.currency_for_sale == order_new.currency_desired

        # existing order's currency id desired is the same as the new 
        # order's currency id for sale
        currency_desired_match = \
            self.currency_desired == order_new.currency_for_sale
        
        # existing order's unit price is less than or equal to the 
        # reciprocal of the new order's unit price
        reciprocal = order_new.get_unit_price_inverse()
        accepted_price = self.would_accept(reciprocal)

        # existing order's address is not the new order's address
        no_self_trade = True

        # existing order is still open (not completely fulfilled or 
        # canceled)
        open_order = \
            self.status != OrderStatus.Canceled \
            and self.status != OrderStatus.Filled

        # only match, if all requirements are fulfilled
        valid_match = \
            currency_for_sale_match \
            and currency_desired_match \
            and accepted_price \
            and no_self_trade \
            and open_order

        return valid_match

    def update_order(self, amount_received, amount_spent):
        """Fill and update order.
        
        The order is updated based on received and spent amounts. The 
        order is considered as completely filled, if the full "desired" 
        amount is reached."""
        assert 0 < long(math.floor(amount_received))
        assert 0 < long(math.floor(amount_spent))
        
        # desired amount is based on limit price
        updated_amount_desired = self.amount_desired - amount_received

        # the new amount for sale is derived from desired amount (!)
        updated_amount_for_sale = \
            float(updated_amount_desired) / self.get_unit_price()

        # rounding up was chosen, because the user still receives the 
        # amount he wanted in the first place in total and in the case 
        # of rounding down the price may be "below market price"
        updated_amount_for_sale = long(math.ceil(updated_amount_for_sale))
        assert updated_amount_for_sale == updated_amount_for_sale

        # make sure not more than remaining units are sold
        updated_amount_remaining = self.amount_for_sale - amount_spent
        assert updated_amount_for_sale <= updated_amount_remaining
        
        # report updated amounts before applying them
        self.report_pending_update(
            self, updated_amount_for_sale, updated_amount_desired)

        # set updated amounts
        self.amount_desired = updated_amount_desired
        self.amount_for_sale = updated_amount_for_sale

        # the order is filled completely, if the desired amount is 
        # reached
        if updated_amount_desired > 0:
            self.set_status(OrderStatus.PartiallyFilled)
        else:
            self.set_status(OrderStatus.Filled)
        
        # report traded amounts
        self.report_updated_order(self, amount_received, amount_spent)

        return self
       
    def set_status(self, new_status):
        """Updates status of the Order."""
        if self.status != new_status:
            # report new status
            self.report_status_update(self, new_status)
            self.status = new_status

    def id_to_string(self):
        return "[ID %i]" % self.id

    def __str__(self):
        s = "[ID %i] offers %i %s, desires %i %s at %f (%f)" % \
            (self.id, self.amount_for_sale, self.currency_for_sale, 
             self.amount_desired, self.currency_desired,
             self.get_unit_price(), self.get_unit_price_inverse())
        return s
 
    @classmethod
    def __get_new_id(cls):
        cls.__id = cls.__id + 1
        return cls.__id

    @classmethod
    def create_sell_order(
            cls, amount_for_sale, price, currency_for_sale, currency_desired):
        """Create a new sell order.

        This is a helper for more intuitive order creation. The price 
        is nominated in the currency of the property sold for."""
        amount_desired = float(amount_for_sale) * float(price)

        # explicitly round down to a whole number to avoid problems 
        # based on strange floating point representations
        amount_for_sale = long(math.floor(amount_for_sale))

        return cls(currency_for_sale, amount_for_sale,
                   currency_desired, amount_desired)

    @classmethod
    def create_buy_order(
            cls, amount_desired, price, currency_desired, currency_for_sale):
        """Create a new buy order.

        This is a helper for more intuitive order creation. The price 
        is nominated in the currency of the property bought with."""
        amount_for_sale = float(amount_desired) * float(price)

        # explicitly round down to a whole number to avoid problems 
        # based on strange floating point representations
        amount_for_sale = long(math.floor(amount_for_sale))

        return cls(currency_for_sale, amount_for_sale,
                   currency_desired, amount_desired)

    @classmethod
    def report_new_order(cls, order):
        """Fires an event for a new created Order."""
        assert isinstance(order, Order)
        order.onNewOrder(order)
                
    @classmethod
    def report_pending_update(
            cls, order, new_amount_for_sale, new_amount_desired):
        """Fires event with updated amounts before applying them."""
        assert isinstance(order, Order)
        assert isinstance(new_amount_for_sale, long)
        assert isinstance(new_amount_desired, long)
        cls.onPendingAmountUpdate(order, new_amount_for_sale, new_amount_desired)

    @classmethod
    def report_updated_order(cls, order, amount_received, amount_spent):
        """Fires event with given and received amounts after a trade."""
        assert isinstance(order, Order)
        assert isinstance(amount_received, long)
        assert isinstance(amount_spent, long)
        cls.onUpdatedOrder(order, amount_received, amount_spent)

    @classmethod
    def report_status_update(cls, order, status):
        """Fires event with updated status."""
        assert isinstance(order, Order)
        assert isinstance(status, int)
        cls.onStatusUpdate(order, status)
 
               
class MatchingEngine:
    __slots__ = ['orderbook']

    onOrderArrival = event.Event()
    onTrade = event.Event()

    def __init__(self):
        self.orderbook = Orderbook()

    def get_best_match(self, new_order):
        """Find best match for an order.

        The "perfect match" is an order with inverted currency pair and
        best price. In the case of more than one candidate, the oldest 
        one is chosen."""
        assert None != new_order

        best_match = None

        # get all open orders with matching currency pair
        potential_orders = self.orderbook.get_orders(
            new_order.currency_desired, new_order.currency_for_sale)

        # only orders with a favorable unit price are considered
        potential_matches = \
            list(filter(lambda order:
                        order.matches_with(new_order), potential_orders))

        # the best match should be the last item in the list
        if len(potential_matches) > 0:
            best_match = potential_matches[0]

        return best_match    

    def add_order(self, order_new):
        """Add an order.

        Returns Order after execution or listing.
        
        New orders are matched against existing ones and in the case
        of a match, the orders are executed. Partially filled orders 
        are updated. This is done repeatingly until no more matches 
        are found. If the order is still (partially) unfulfilled, the 
        order is added to the orderbook."""
        assert None != order_new

        # announce arrival of a new order
        self.report_order_arrival(order_new)

        # the best match is the cheapest and oldest one
        best_match = self.get_best_match(order_new)

        if best_match != None:
            # the order is executed
            self.execute_orders(best_match, order_new)                                    
        else:
            # add order to the orderbook
            self.orderbook.list(order_new)
        
        return order_new

    def get_traded_amounts(self, order_old, order_new):
        """Calculate traded amounts.

        The given orders are executed and a tuple of actually traded 
        amounts is returned."""
        assert None != order_old
        assert None != order_new
        assert 0 < long(math.floor(order_old.amount_for_sale))
        assert 0 < long(math.floor(order_new.amount_for_sale))
        assert order_old.matches_with(order_new)
        assert order_new.matches_with(order_old)

        # extra variables are used for better readability
        a1_available = order_old.amount_for_sale
        a1_unit_price = order_old.get_unit_price()
        
        # only whole units can be traded!
        a1_desired = math.ceil(order_old.amount_desired)
        a2_desired = math.ceil(order_new.amount_desired)
        assert a1_desired == order_old.amount_desired
        assert a2_desired == order_new.amount_desired
        
        # these are the traded amounts
        amount_to_a2 = long(min(a2_desired, a1_available))
        amount_to_a1 = long(math.ceil(amount_to_a2 * a1_unit_price))
        
        # check, if price after rounding up is within accepted range
        updated_unit_price = float(amount_to_a1) /  float(amount_to_a2)
        updated_unit_price_inverse = float(amount_to_a2) /  float(amount_to_a1)
        assert order_old.would_accept(updated_unit_price)
        assert order_new.would_accept(updated_unit_price_inverse)

        return (amount_to_a1, amount_to_a2)

    def execute_orders(self, order_old, order_new):
        """Match and execute two orders.
      
        The traded amounts are based on the "desired" amount" and not
        on the amounts "up for sale". The "amount for sale" may rather
        be considered as threshold or upper limit.

        In the case an existing order is filled partially, the order 
        is updated.

        A new order is matched against existing orders until the order 
        is completely filled or no potential match is found."""
        # determine the actually traded amounts
        (amount_to_a1, amount_to_a2) = \
            self.get_traded_amounts(order_old, order_new)
        
        # report trade
        self.report_trade(order_old, order_new, amount_to_a1, amount_to_a2)
        
        # update existing order based on traded amounts
        order_old.update_order(amount_to_a1, amount_to_a2)
                
        if order_old.status == OrderStatus.Filled:
            # the existing order is removed from the orderbook
            self.orderbook.delist(order_old)

        # update pending order based on traded amounts
        order_new.update_order(amount_to_a2, amount_to_a1)
        
        if order_new.status != OrderStatus.Filled:
            # the updated, new order is enqueued until filled or listed
            self.add_order(order_new)
    
    def __str__(self):
        response = "Open Orders:"
        if not self.orderbook:
            response += "\nNo open orders available."
        for order in self.orderbook.orders:
            response += "\n" + str(order)
        return response
    
    @classmethod
    def report_order_arrival(cls, order):
        """Fires event for enqueued Order."""
        assert isinstance(order, Order)
        cls.onOrderArrival(order)

    @classmethod
    def report_trade(cls, order_a1, order_a2, amount_to_a1, amount_to_a2):
        """Fires event after a trade with traded amounts and orders."""
        assert isinstance(order_a1, Order)
        assert isinstance(order_a2, Order)
        assert isinstance(amount_to_a1, long)
        assert isinstance(amount_to_a2, long)
        cls.onTrade(order_a1, order_a2, amount_to_a1, amount_to_a2)