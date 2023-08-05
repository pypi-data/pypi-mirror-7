DAD - Deliver Asynchronous Data
================================

Used to notify MOM (Message Oriented Middleware), throught STOMP (Simple Text Oriented Messaging Protocol).

Example of usage
----------------

::

    from dad.mom import Middleware
    from dad.event import SemanticEvent


    middleware = Middleware(host="localhost", port=61613)
    event = SemanticEvent(
        instance="http://dbpedia.org/Nina",
        klass="http://dbpedia.org/Dog",
        graph="http://dbpedia.org/animal",
        action="a")
    middleware.notify(event)
