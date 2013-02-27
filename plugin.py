###
# Copyright (c) 2012, Roland Hieber
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import re

import supybot.conf as conf
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class MediaWikiShortLinks(callbacks.PluginRegexp):
  """If activated, the plugin looks for wikilink syntax like [[Article]] or
  {{Template}} in the channel and spits out the corresponding long URL to the
  wiki page. Set the channel value plugins.MediaWikiShortLinks.mediaWikiUrl to
  enable wikilink snarfing."""
  threaded = True
  regexps = ['mediaWikiTitleSnarfer', 'mediaWikiTemplateSnarfer']

  def mwUrlTitleEncode(self, s):
    """urlencode only the special characters in a MediaWiki page title, but 
    let other characters untouched for better readability"""
    s = s.replace(" ","_")
    s = s.replace("~","%7E")
    s = s.replace("&","%26")
    s = s.replace("#","%23")
    s = s.replace("?","%3F")
    s = s.replace("(","%28")  # prevents some clients to detect the whole URL
    s = s.replace(")","%29")
    return s
 
  # a snarfer for wiki titles like [[Template]]
  def mediaWikiTitleSnarfer(self, irc, msg, match):
    r"\[\[(.+?)\]\]"
    #self.log.info("snarfed title with match: %s" % match.groups())
    channel = msg.args[0]
    if not irc.isChannel(channel):
      return
    if callbacks.addressed(irc.nick, msg):
      return
    # workaround for stupid line-breaking in config file after 80 chars -.-
    url = self.registryValue('mediaWikiUrl', channel).translate(None, " \t\n\r")
    if url:
      if not url.endswith("/"):
        url += "/"
      # apparently, this function is only called for the first match at all :(
      page = match.group(1).strip()
      irc.reply(url + self.mwUrlTitleEncode(page), prefixNick=False)

  mediaWikiTitleSnarfer = urlSnarfer(mediaWikiTitleSnarfer)

  # a snarfer for templates like {{Template}}
  def mediaWikiTemplateSnarfer(self, irc, msg, match):
    r"\{\{(.+?)\}\}"
    #self.log.info("snarfed with match: %s" % match.groups())
    channel = msg.args[0]
    if not irc.isChannel(channel):
      return
    if callbacks.addressed(irc.nick, msg):
      return
    url = self.registryValue('mediaWikiUrl', channel)
    if url:
      if not url.endswith("/"):
        url += "/"
      # apparently, this function is only called for the first match at all :(
      page = match.group(1).strip()
      irc.reply(url + "Template:" + self.mwUrlTitleEncode(page),
        prefixNick=False)

  mediaWikiTemplateSnarfer = urlSnarfer(mediaWikiTemplateSnarfer)

Class = MediaWikiShortLinks

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
