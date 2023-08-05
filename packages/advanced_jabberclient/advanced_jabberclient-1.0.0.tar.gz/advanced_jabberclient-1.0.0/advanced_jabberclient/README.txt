Advanced jabber client for Twisted

I. Requirements:
 + Twisted


II. Added to jabber client factory:
 + Ping timeout (jabber server must have echo module)


III. How to use
 1. Install Twisted from pip
 2. Create factory (instead of use basicClientFactory): 
    factory = jabberClientFactory(jid=jid.JID(settings.USERNAME),
                                  secret=settings.PASSWORD,
                                  ping_timeout=settings.PING_TIMEOUT,
                                  ping_fail_time=settings.PING_FAIL_TIME,
                                  host=settings.HOST)
 3. Add observer for xmlstream for message (if not exist)
 4. In message observer add to message parse:
    for e in message.elements():
        if e.name == "body":
            command = e.__str__()
            if command == "ping":
                xmlstream.receivePing()
            else:
                ... [your command parser]


IV. Author
 + Vadim aka ruscoder
 + http://github.com/ruscoder/
