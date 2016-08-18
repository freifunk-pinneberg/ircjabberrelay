# -*- coding: utf-8 -*-

import sys
from twisted.internet import defer
from twisted.python import log
from twisted.words.protocols.jabber import jid
from wokkel import muc

class JabberBot(muc.MUCClient):
    """ """

    def __init__(self, manager, server, room, nick, callback):
        muc.MUCClient.__init__(self)
        self.manager   = manager
        self.server   = server
        self.room     = room
        self.nick     = nick
        self.callback = callback
        self.room_jid = jid.internJID(self.room+'@'+self.server+'/'+self.nick)

    def initialized(self):
        """The bot has connected to the xmpp server, now try to join the room.
        """
        log.msg("Connected to server")
        self.join(self.server, self.room, self.nick).addCallback(self.initRoom)

    @defer.inlineCallbacks
    def initRoom(self, room):
        """Configure the room if we just created it.
        """

        if int(room.status) == muc.STATUS_CODE_CREATED:
            config_form = yield self.getConfigureForm(self.room_jid.userhost())

            # set config default
            config_result = yield self.configure(self.room_jid.userhost())

    def receivedGroupChat(self, room, user, body):
        ismoderator = (user.role == 'moderator')
        if not user.nick.startswith(self.nick):
            #if body.startswith('/me '):
            #    self.callback("JABBER: * %s %s" % (user.nick, body.replace('/me ', '', 1)))
            #else:

            # send to irc only command messages
            if body.startswith('@who'):
                if self.manager.ircbot is not None:
                    self.manager.ircbot.names().addCallback(self.printOnline)
            elif ismoderator and body.startswith('@ignore '):
                nick = body.replace('@ignore ', '', 1).rstrip()
                if not nick in self.manager.ignoreList:
                    self.manager.addIgnore(nick)
                    self.sendMessage("Ignoring %s" % (nick))
            elif ismoderator and body.startswith('@unignore '):
                nick = body.replace('@unignore ', '', 1).rstrip()
                if nick in self.manager.ignoreList:
                    self.manager.removeIgnore(nick)
                    self.sendMessage("Unignoring %s" % (nick))
            elif ismoderator and body.startswith('@ignorelist'):
                if len(self.manager.ignoreList) > 0:
                    self.sendMessage("Ignoring " + ' '.join(self.manager.ignoreList))
                else:
                    self.sendMessage("Not ignoring anybody")
            elif body.startswith('@help'):
                self.sendMessage('\n'.join(
                    [u"@who - Show IRC users"
                    ] + (
                    [u"@ignore <username> - ignore user from IRC Channel",
                     u"@unignore <username> - relay messages from user in IRC Channel again",
                     u"@ignorelist - show users on ignorelist",
                    ]
                    if ismoderator else [])).encode('utf-8'))
            else:
                 msg = "<%s> %s" % (user.nick, msg)
                try:
                    msg = msg.encode('utf-8')
                except UnicodeDecodeError:
                    None
                self.callback(msg)

    def printOnline(self, namelist):
        namelist.sort()
        msg = ' '.join(namelist)
        self.groupChat(self.room_jid, msg.decode('utf-8'))

    def sendMessage(self, msg):
        #log.msg("jabber <- %s" % (msg))
        self.groupChat(self.room_jid, msg.decode('utf-8'))
