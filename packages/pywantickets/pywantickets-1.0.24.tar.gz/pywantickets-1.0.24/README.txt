==========
Change Log
==========

1.0.23 (July 11, 2014)
======================
* Added a generic customer for parsing customers and address.
* Implemented GrandTotat, Customer and Address for GetOrderDetailsRequest.
* Added parse_cart_item function to be used in Cart and in a TicketOrder.
* Implemented OrderItems, they are supposed to be different to cart items.
* 

1.0.22 (July 11, 2014)
======================
* Fixed the way order details is parsed, it wasn't being parsed at correct level.

1.0.21 (July 11, 2014)
======================
* Fixed order_id in GetOrderDetailsRequest implementation

1.0.20 (July 3, 2014)
======================

* Event dates are parsed accordingly its timezone.

1.0.19 (July 3, 2014)
======================

* If a date comes empty in purchase client, it will be converted to **None**.
* Changed the parse order for dates received in search client.
* Implemented *last_response* in clients.
* Implemented get_zone_list in WanticketsSearchClient.
* Implemented Search -> getPromerList.

