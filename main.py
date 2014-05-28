from simple_order_matching import *

# divisible amounts are also integers internally, but COIN can be used
# for smoother expressions, e.g.: the amount "0.1" (BTC) can be expressed 
# by "0.1*COIN" (BTC) instead of "10000000" (BTC)
COIN = 100000000

# smart properties and currencies are simply represented by strings
cBITCOIN = "BTC"
cMASTERCOIN = "MSC"
cIndiv1 = "Indiv1"
cIndiv2 = "Indiv2"

class SampleView(object):

    # skip this

    def order_created_callback(self, order):
        print("New Order %s created: %s %s offered, %s %s desired @ %s (%s)" % \
            (order.id_to_string(),
             self.formatted_money(order.amount_for_sale, order.currency_for_sale),
             order.currency_for_sale,
             self.formatted_money(order.amount_desired, order.currency_desired),
             order.currency_desired,
             self.formatted_decimal(order.get_unit_price()),
             self.formatted_decimal(order.get_unit_price_inverse())))

    def pending_update_callback(self, order, new_amount_for_sale, new_amount_desired):
        result = "Updated Order %s: %s => %s %s offered, %s => %s %s desired" % \
            (order.id_to_string(),
             self.formatted_money(order.amount_for_sale, order.currency_for_sale),
             self.formatted_money(new_amount_for_sale, order.currency_for_sale),
             order.currency_for_sale,
             self.formatted_money(order.amount_desired, order.currency_desired),
             self.formatted_money(new_amount_desired, order.currency_desired),
             order.currency_desired)
        if new_amount_desired > 0 and new_amount_for_sale > 0:
            unit_price = float(new_amount_desired) /  float(new_amount_for_sale)
            unit_price_inverse = 1.0 / unit_price
            result = "%s @ %s (%s)" % \
                (result, self.formatted_decimal(unit_price),
                 self.formatted_decimal(unit_price_inverse))
        print(result)

    def status_update_callback(self, order, status):
        print("Set status of Order %s: %s" % \
            (order.id_to_string(), OrderStatus.AsString[status]))

    def updated_order_callback(self, order, amount_received, amount_spent):
        print("%s %s: %s/%s %s" % \
            (order.id_to_string(),
             OrderStatus.AsString[order.status],
             self.formatted_money(
                order.get_received_amount(), order.currency_desired),
             self.formatted_money(order.initial_amount_desired, order.currency_desired),
             order.currency_desired))
            
    def order_arrival_callback(self, order):
        print("%s enqueued." % order.id_to_string())

    def trade_execution_callback(self, order_a1, order_a2, amount_to_a1, amount_to_a2):
        unit_price = float(amount_to_a1) /  float(amount_to_a2)
        unit_price_inverse = 1.0 / unit_price
        print("Executed %s, %s: %s %s traded for %s %s @ %s (%s)" % \
            (order_a2.id_to_string(), order_a1.id_to_string(), 
             self.formatted_money(
             amount_to_a2, order_a2.currency_desired), 
             order_a2.currency_desired, 
             self.formatted_money(
             amount_to_a1, order_a1.currency_desired), 
             order_a1.currency_desired,
             self.formatted_decimal(unit_price),
             self.formatted_decimal(unit_price_inverse)))

    def listed_order_callback(self, order):
        print("%s added to the orderbook." % order.id_to_string())

    def delisted_order_callback(self, order):
        print("%s removed from the orderbook." % order.id_to_string())

    # workaround to format amounts for divisible tokens
    def formatted_money(self, number, currency):
        if currency == cBITCOIN or currency == cMASTERCOIN:
            amt = float(number) / float(COIN)
            return self.formatted_decimal(amt)
        else:
            return "%i" % number
    
    # set number of deciamals via "decimals"
    def formatted_decimal(self, number, decimals=4):
        """Format any number to 0.0#######."""
        float_number = float(number)
        s = "{:.{num_decimals}f}".format(float_number, num_decimals=decimals)
        # remove zeros on the right
        trimmed = s.rstrip('0')
        # make sure there is at least one zero on the right
        if trimmed.endswith('.'):
            return trimmed + '0'
        else:
            return trimmed
        

if __name__ == "__main__":
    
    # the sample view class is a proof of concept to demonstrate 
    # how the callbacks are used and which data is transferred.

    view = SampleView()

    # there are few events available to allow easier access to the 
    # actual data. instead of parsing some output, it would be more 
    # convenient to simply register a custom method which is called 
    # once the event is fired. more than one callback can be 
    # registered.
    # arguments are mostly order objects and other related values.
        
    MatchingEngine.onOrderArrival += view.order_arrival_callback
    MatchingEngine.onTrade += view.trade_execution_callback

    Orderbook.onDelisting += view.delisted_order_callback
    Orderbook.onListing += view.listed_order_callback

    Order.onNewOrder += view.order_created_callback
    Order.onPendingAmountUpdate += view.pending_update_callback
    Order.onStatusUpdate += view.status_update_callback
    Order.onUpdatedOrder += view.updated_order_callback

    # there is probably a lot of room for optimizations and it's not 
    # yet clear to me, if the applied trading and execution logic is 
    # sufficient or correct.

    engine = MatchingEngine()
    
    # create two orders
    orderA = Order(cIndiv2, 20, cIndiv1, 10)
    orderB = Order(cIndiv1, 12, cIndiv2, 17)

    # add orders to the orderbook
    engine.add_order(orderA)
    engine.add_order(orderB)

    engine.add_order(Order.create_sell_order(COIN*0.35, 0.23, cMASTERCOIN, cBITCOIN))
    engine.add_order(Order.create_sell_order(COIN*2.25, 0.23, cMASTERCOIN, cBITCOIN))    
    engine.add_order(Order.create_sell_order(COIN*15, 0.2155, cMASTERCOIN, cBITCOIN))
    engine.add_order(Order.create_buy_order(COIN*20, 0.25, cMASTERCOIN, cBITCOIN))