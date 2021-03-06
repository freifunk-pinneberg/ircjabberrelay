from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, defer
from twisted.python import log
import re

class IrcBot(irc.IRCClient):
    def __init__(self):
        self._namescallback = {}

    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def _get_realname(self):
        return self.factory.realname
    realname = property(_get_realname)

    def _get_userinfo(self):
        return self.factory.userinfo
    userinfo = property(_get_userinfo)

    def signedOn(self):
        self.join(self.factory.channel)
        log.msg("Signed on as %s." % (self.nickname,))
        self.factory.manager.setIRC(self)

    def joined(self, channel):
        log.msg("Joined %s." % (channel,))

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        message = msg

        # Check ignore list
        if user in self.factory.manager.ignoreList:
            return

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            return

        pattern = re.compile("<#\d{5}#\d{3}#\d{3}([^#]*)#\d{3}>(.*)", re.IGNORECASE)
        if pattern.search(msg.rstrip()) is not None:
            message = "<%s>%s" % (re.search(pattern, msg).group(1), re.search(pattern, msg).group(2))

        log.msg("irc msg = %s" % message)

        if self.isUtf8(msg):
            if message.startswith('@who'):
                self.factory.manager.jabberbot.getXMPPUsers().addCallback(self.printOnline)
            else:
                self.factory.callback("<%s> %s" % (user, msg.rstrip()))

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]

        # Check ignore list
        if user in self.factory.manager.ignoreList:
            return

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            return

        if self.isUtf8(msg):
            self.factory.callback("<%s> %s" % (user, msg.rstrip()))

    def sendMessage(self, msg):
        #log.msg("irc <- %s" % (msg))
        self.msg(self.factory.channel, msg)

    def isUtf8(self, msg):
        try:
            msg.decode('utf-8')
            return True
        except UnicodeDecodeError:
            return False

    def names(self):
        channel = self.factory.channel.lower()
        d = defer.Deferred()
        if channel not in self._namescallback:
            self._namescallback[channel] = ([], [])

        self._namescallback[channel][0].append(d)
        self.sendLine("NAMES %s" % channel)
        return d

    def irc_RPL_NAMREPLY(self, prefix, params):
        channel = params[2].lower()
        nicklist = params[3].split(' ')

        if channel not in self._namescallback:
            return

        n = self._namescallback[channel][1]
        n += nicklist

    def irc_RPL_ENDOFNAMES(self, prefix, params):
        channel = params[1].lower()
        if channel not in self._namescallback:
            return

        callbacks, namelist = self._namescallback[channel]

        for cb in callbacks:
            cb.callback(namelist)

        del self._namescallback[channel]

    def printOnline(self, namelist):
            namelist.sort()
            msg = ' '.join(namelist)
            self.sendMessage(msg.decode('utf-8'))

class IrcBotFactory(protocol.ClientFactory):
    protocol = IrcBot

    def __init__(self, manager, channel, nickname, realname, userinfo, callback):
        self.manager = manager
        self.channel = channel
        self.nickname = nickname
        self.realname = realname
        self.userinfo = userinfo
        self.callback = callback

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % (reason,)
        reactor.stop()
