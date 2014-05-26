Simple order matching engine to test and verify different matching strategies.

Whole units are used -- `COIN` may be used as modificator.

### Example 1:

Create some simple orders:
```python
engine = MatchingEngine()
orderA = Order("Indiv2", 20, "Indiv1", 10)
orderB = Order("Indiv1", 12, "Indiv2", 17)
engine.add_order(orderA)
engine.add_order(orderB)
```
Result:
```python
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
Adding Order [ID 0] to the orderbook...
[ID 0] time: 1401085087296
[ID 0] amount for sale: 20 Indiv2
[ID 0] amount desired: 10 Indiv1
[ID 0] unit price: 0.5 Indiv1/Indiv2
[ID 0] inverse unit price: 2.0 Indiv2/Indiv1
Best match for Order [ID 0]:
None
Added Order [ID 0] to the orderbook.
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
Adding Order [ID 1] to the orderbook...
[ID 1] time: 1401085087300
[ID 1] amount for sale: 12 Indiv1
[ID 1] amount desired: 17 Indiv2
[ID 1] unit price: 1.41666667 Indiv2/Indiv1
[ID 1] inverse unit price: 0.70588235 Indiv1/Indiv2
Best match for Order [ID 1]:
[ID 0] time: 1401085087296
[ID 0] amount for sale: 20 Indiv2
[ID 0] amount desired: 10 Indiv1
[ID 0] unit price: 0.5 Indiv1/Indiv2
[ID 0] inverse unit price: 2.0 Indiv2/Indiv1
9 Indiv1 traded for 17 Indiv2 at 0.52941176 Indiv1/Indiv2.
Order [ID 0] filled partially and will be replaced.
Removed Order [ID 0].
Order [ID 1] filled completely.
Creating new order...
[ID 2] time: 1401085087296
[ID 2] amount for sale: 2 Indiv2
[ID 2] amount desired: 1 Indiv1
[ID 2] unit price: 0.5 Indiv1/Indiv2
[ID 2] inverse unit price: 2.0 Indiv2/Indiv1
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
Adding Order [ID 2] to the orderbook...
[ID 2] time: 1401085087296
[ID 2] amount for sale: 2 Indiv2
[ID 2] amount desired: 1 Indiv1
[ID 2] unit price: 0.5 Indiv1/Indiv2
[ID 2] inverse unit price: 2.0 Indiv2/Indiv1
Best match for Order [ID 2]:
None
Added Order [ID 2] to the orderbook.
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
```

### Example 2:

```python
DEBUG = 1 # minimal debug info
```
```python
engine.add_order(Order.create_sell_order(COIN*0.35, 0.23, cMASTERCOIN, cBITCOIN))
engine.add_order(Order.create_sell_order(COIN*2.25, 0.23, cMASTERCOIN, cBITCOIN))    
engine.add_order(Order.create_sell_order(COIN*15, 0.2155, cMASTERCOIN, cBITCOIN))
engine.add_order(Order.create_buy_order(COIN*20, 0.25, cMASTERCOIN, cBITCOIN))
```
Result:
```python
Added Order [ID 0] to the orderbook.
Added Order [ID 1] to the orderbook.
Added Order [ID 2] to the orderbook.
323250000 BTC traded for 1500000000 MSC at 0.2155 BTC/MSC.
Order [ID 2] filled completely.
Removed Order [ID 2].
Order [ID 3] filled partially and will be updated.
8050000 BTC traded for 35000000 MSC at 0.23 BTC/MSC.
Order [ID 0] filled completely.
Removed Order [ID 0].
Order [ID 4] filled partially and will be updated.
51750000 BTC traded for 225000000 MSC at 0.23 BTC/MSC.
Order [ID 1] filled completely.
Removed Order [ID 1].
Order [ID 5] filled partially and will be updated.
Added Order [ID 6] to the orderbook.
```
And finally:
```python
print(engine) # show open orders
```
Result:
```python
Open Orders:
[ID 6] time: 1401086985416
[ID 6] amount for sale: 60000000 BTC
[ID 6] amount desired: 240000000 MSC
[ID 6] unit price: 4.0 MSC/BTC
[ID 6] inverse unit price: 0.25 BTC/MSC
```