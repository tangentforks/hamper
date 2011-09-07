import re
import random

from zope.interface import implements, Interface, Attribute

from hamper.interfaces import Command, Plugin


class Quit(Plugin):
    """Know when hamper isn't wanted."""
    name = 'quit'

    class QuitCommand(Command):
        regex = 'go away'

        def command(self, bot, comm, groups):
            if comm['pm']:
                bot.msg(comm['channel'], "You can't do that from PM.")
                return False

            bot.msg(comm['channel'], 'Bye!')
            bot.leaveChannel(comm['channel'])
            return True


class Sed(Plugin):
    """To be honest, I feel strange in channels that don't have this."""

    name = 'sed'
    priority = -1

    class SedCommand(Command):
        regex = r's/(.*)/(.*)/(g?i?m?)'
        onlyDirected = False

        def command(self, bot, comm, groups):
            options = groups[2]

            regex_opts = re.I if 'i' in options else 0
            usr_regex = re.compile(groups[0], regex_opts)
            usr_replace = groups[1]

            g = 0 if 'g' in options else 1

            key = comm['channel']
            if key not in bot.factory.history:
                bot.msg(comm['channel'], 'Who are you?! How did you get in my '
                                         'house?!')
                return False

            for hist in reversed(bot.factory.history[key]):
                if 'm' in options and hist['user'] != comm['user']:
                    # Only look at the user's messages
                    continue

                # Don't look at other sed commands
                if hist['directed'] and hist['message'].startswith('s/'):
                    continue

                if usr_regex.search(hist['message']):
                    new_msg = usr_regex.sub(usr_replace, hist['message'], g)
                    bot.msg(comm['channel'], '{0} actually meant: {1}'
                            .format(hist['user'], new_msg))
                    break
            else:
                bot.msg(comm['channel'],
                    "Sorry, I couldn't match /{0}/.".format(usr_regex.pattern))

class LetMeGoogleThatForYou(Plugin):
    """Link to the sarcastic letmegooglethatforyou.com."""

    name = 'lmgtfy'

    class LMGTFYCommand(Command):
        regex = '^lmgtfy\s+(.*)'
        onlyDirected = False

        def command(self, bot, comm, groups):
            target = ''
            if comm['target']:
                target = comm['target'] + ': '
            args = groups[0].replace(' ', '+')
            bot.msg(comm['channel'], target + 'http://lmgtfy.com/?q=' + args)

def roll(num, sides, add):
    """Rolls a die of sides sides, num times, sums them, and adds add"""
    rolls = []
    for i in range(num):
        rolls.append(random.randint(1,sides))
    rolls.append(add)
    return rolls

class Dice(Plugin):
    """Random dice rolls!"""
    name = 'dice'
    onlyDirected = True
    priority = 3
    regex = '((\d*)d)?(\d*)(\+(\d*))?'

    class DiceCommand(Command):
        onlyDirected = True
        regex = '((\d*)d)?(\d*)(\+(\d*))?'

        def command(self, bot, com, groups):
            _, num, sides,_, add = groups

            if not num:
                num = 1
            else:
                num = int(num)

            if not sides:
                sides = 6
            else:
                sides = int (sides)

            if not add:
                add = 0
            else:
                add = int(add)

            result = roll(num,sides,add)
            output = ""
            output += "%s: You rolled %sd%s+%s and got " %(com['user']
                , num, sides, add)
            if len(result) < 11:
                # the last one is the constant to add
                for die in result[:-1]:
                    output += "%s, " % die
            else:
                output += "a lot of dice "

            output += "for a total of %s" % sum(result)

            bot.say(com['channel'], output)
lmgtfy = LetMeGoogleThatForYou()
sed = Sed()
quit = Quit()
dice = Dice()
