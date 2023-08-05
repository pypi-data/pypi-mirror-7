=============================
dj-webhooks
=============================

.. image:: https://pypip.in/d/dj-webhooks/badge.png
        :target: https://pypi.python.org/pypi/dj-webhooks

.. image:: https://badge.fury.io/py/dj-webhooks.png
    :target: https://badge.fury.io/py/dj-webhooks

.. image:: https://pypip.in/wheel/dj-webhooks/badge.png
    :target: https://pypi.python.org/pypi/dj-webhooks/
    :alt: Wheel Status

.. image:: https://travis-ci.org/pydanny/dj-webhooks.png?branch=master
    :target: https://travis-ci.org/pydanny/dj-webhooks

Django + Webhooks Made Easy

The full documentation is at https://dj-webhooks.readthedocs.org.

Requirements
------------

* Python 2.7.x or 3.3.2 or higher
* django>=1.5.5
* django-jsonfield>=0.9.12
* django-model-utils>=2.0.2
* django-rq>=0.6.1
* webhooks>=0.3.1

Quickstart
----------

Install dj-webhooks::

    pip install dj-webhooks

Configure some webhook events:

.. code-block:: python

    # settings.py
    WEBHOOK_EVENTS = (
        "purchase.paid",
        "purchase.refunded",
        "purchase.fulfilled"
    )

Add some webhook targets:

.. code-block:: python

    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(username="pydanny")

    from webhooks.models import Webhook
    WebhookTarget.objects.create(
        owner=user,
        event="purchase.paid",
        target_url="https://mystorefront.com/webhooks/",
        header_content_type=Webhook.CONTENT_TYPE_JSON,
    )

Then use it in a project:

.. code-block:: python

    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(username="pydanny")

    from djwebhooks.decorators import hook

    from myproject.models import Purchase

    # Event argument helps identify the webhook target
    @hook(event="purchase.paid")
    def send_purchase_confirmation(purchase, owner): # Webhook_owner also helps identify the webhook target
        return {
            "order_num": purchase.order_num,
            "date": purchase.confirm_date,
            "line_items": [x.sku for x in purchase.lineitem_set.filter(inventory__gt=0)]
        }

    for purchase in Purchase.objects.filter(status="paid"):
        send_purchase_confirmation(purchase=purchase, owner=user)

In a queue using django-rq
----------------------------

Assuming you are running Redis and also have django-rq configured:

.. code-block:: python

    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(username="pydanny")

    # import redis hook
    from djwebhooks.decorators import redis_hook

    from myproject.models import Purchase

    # Event argument helps identify the webhook target
    @redis_hook(event="purchase.paid")
    def send_purchase_confirmation(purchase, owner): # Webhook_owner also helps identify the webhook target
        return {
            "order_num": purchase.order_num,
            "date": purchase.confirm_date,
            "line_items": [x.sku for x in purchase.lineitem_set.filter(inventory__gt=0)]
        }

    for purchase in Purchase.objects.filter(status="paid"):
        job = send_purchase_confirmation(purchase=purchase, owner=user)


Features
--------

* Synchronous webhooks
* Delivery tracking via Django ORM.
* Options for asynchronous webhooks.

Planned Features
-----------------

* Delivery tracking via Redis and other write-fast datastores.




History
-------

0.2.1 (2014-05-17)
++++++++++++++++++

* Removed conf.py file as it just added abstraction
* Created exlicitly importable hooks. Makes settings management easier.
* Removed utils.py since we no longer do fancy dynamic imports (see previous bullet).
* Coverage now at 100%


0.2.0 (2014-05-15)
++++++++++++++++++

* Refactored the senders to be very extendable.
* Added an ORM based sender.
* Added a redis based sender that uses django-rq.
* Added a `redis-hook` decorator.
* Added admin views.
* Ramped up test coverage to 89%.
* setup.py now includes all dependencies.


0.1.0 (2014-05-12)
++++++++++++++++++

* First release on PyPI.

