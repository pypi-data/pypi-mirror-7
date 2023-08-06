PostBoy
=======

Simple distributed emailing system. Consists of broker (based on pyzmq) and worker.

Installation
++++++++++++

        pip install postboy

Using
+++++

    /usr/bin/postboy-broker --debug

    /usr/bin/postboy-worker --debug

Then try to use it.
    >>> from postboy import Email, BrokerHandler
    >>> broker = BrokerHandler()
    >>> email = Email(sender='info@test.name', recipient='user@localhost', subject='Test')
    >>> broker.store(email.dumps())
    1 # <= return task id
