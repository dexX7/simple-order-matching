Simple order matching engine to test and verify different matching strategies.

### An overview:

Callbacks are used to access data:
```python
view = SampleView()

MatchingEngine.onOrderArrival += view.order_arrival_callback
MatchingEngine.onTrade += view.trade_execution_callback

Orderbook.onDelisting += view.delisted_order_callback
Orderbook.onListing += view.listed_order_callback

Order.onNewOrder += view.order_created_callback
Order.onPendingAmountUpdate += view.pending_update_callback
Order.onStatusUpdate += view.status_update_callback
Order.onUpdatedOrder += view.updated_order_callback
```
The maching engine is initialized and some trades created:
```python
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
```
Text based sample output:
```python
New Order [ID 0] created: 20 Indiv2 offered, 10 Indiv1 desired @ 0.5 (2.0)
New Order [ID 1] created: 12 Indiv1 offered, 17 Indiv2 desired @ 1.4167 (0.7059)
[ID 0] enqueued.
[ID 0] added to the orderbook.
[ID 1] enqueued.
Executed [ID 1], [ID 0]: 17 Indiv2 traded for 9 Indiv1 @ 0.5294 (1.8889)
Updated Order [ID 0]: 20 => 2 Indiv2 offered, 10 => 1 Indiv1 desired @ 0.5 (2.0)
Set status of Order [ID 0]: partially filled
[ID 0] partially filled: 9/10 Indiv1
Updated Order [ID 1]: 12 => 0 Indiv1 offered, 17 => 0 Indiv2 desired
Set status of Order [ID 1]: filled completely
[ID 1] filled completely: 17/17 Indiv2
New Order [ID 2] created: 0.35 MSC offered, 0.0805 BTC desired @ 0.23 (4.3478)
[ID 2] enqueued.
[ID 2] added to the orderbook.
New Order [ID 3] created: 2.25 MSC offered, 0.5175 BTC desired @ 0.23 (4.3478)
[ID 3] enqueued.
[ID 3] added to the orderbook.
New Order [ID 4] created: 15.0 MSC offered, 3.2325 BTC desired @ 0.2155 (4.6404)
[ID 4] enqueued.
[ID 4] added to the orderbook.
New Order [ID 5] created: 5.0 BTC offered, 20.0 MSC desired @ 4.0 (0.25)
[ID 5] enqueued.
Executed [ID 5], [ID 4]: 15.0 MSC traded for 3.2325 BTC @ 0.2155 (4.6404)
Updated Order [ID 4]: 15.0 => 0.0 MSC offered, 3.2325 => 0.0 BTC desired
Set status of Order [ID 4]: filled completely
[ID 4] filled completely: 3.2325/3.2325 BTC
[ID 4] removed from the orderbook.
Updated Order [ID 5]: 5.0 => 1.25 BTC offered, 20.0 => 5.0 MSC desired @ 4.0 (0.25)
Set status of Order [ID 5]: partially filled
[ID 5] partially filled: 15.0/20.0 MSC
[ID 5] enqueued.
Executed [ID 5], [ID 2]: 0.35 MSC traded for 0.0805 BTC @ 0.23 (4.3478)
Updated Order [ID 2]: 0.35 => 0.0 MSC offered, 0.0805 => 0.0 BTC desired
Set status of Order [ID 2]: filled completely
[ID 2] filled completely: 0.0805/0.0805 BTC
[ID 2] removed from the orderbook.
Updated Order [ID 5]: 1.25 => 1.1625 BTC offered, 5.0 => 4.65 MSC desired @ 4.0 (0.25)
[ID 5] partially filled: 15.35/20.0 MSC
[ID 5] enqueued.
Executed [ID 5], [ID 3]: 2.25 MSC traded for 0.5175 BTC @ 0.23 (4.3478)
Updated Order [ID 3]: 2.25 => 0.0 MSC offered, 0.5175 => 0.0 BTC desired
Set status of Order [ID 3]: filled completely
[ID 3] filled completely: 0.5175/0.5175 BTC
[ID 3] removed from the orderbook.
Updated Order [ID 5]: 1.1625 => 0.6 BTC offered, 4.65 => 2.4 MSC desired @ 4.0 (0.25)
[ID 5] partially filled: 17.6/20.0 MSC
[ID 5] enqueued.
[ID 5] added to the orderbook.
```