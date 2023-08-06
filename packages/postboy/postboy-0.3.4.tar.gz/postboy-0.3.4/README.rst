PostBoy
=======

Simple distributed emailing system.

Usually websites send emails directly in request.
Sometime i tried to use as emailing daemon "ssmtp".
I was shocked when I tried to send ten mails from django.
This was about half a minute, and my request was processed long.

This system will be save your response time because your letters will be added to queue and delivered as soon as possible.

For working the Postboy needed RabbitMQ AMQP daemon. This may used as cluster or single server instance.
For delivering will be used any localhost MTA.

Installation
++++++++++++

        pip install postboy

Using
+++++

    /usr/bin/postboy --debug

Then try to use it in your code:

    >>> from postboy import Email, BrokerHandler
    >>> broker = BrokerHandler()
    >>> email = Email(sender='info@test.name', recipient='user@localhost', subject='Test')
    >>> broker.store(email.dumps())
    1 # <= return task id
