#!/usr/bin/python3

import shlex
import subprocess

class M:

    """ A unix shell monad """

    # https://en.wikipedia.org/wiki/Monad_(functional_programming)

    def __init__(self, text = ""):
        # Conceptually just "self.text = text" but with an extra bit to ensure idempotence and make us monadic.
        self.text = text if not isinstance(text, self.__class__) else text.text

    def __getattribute__(self, name):
        try:    return super().__getattribute__(name)
        except: return self.__getattribute_as_unix_cmd__(name)

    # This is where the magic happens
    def __getattribute_as_unix_cmd__(self, name):
        def cmd(arg = ""):
            p = subprocess.Popen([name] + shlex.split(arg), stdin = subprocess.PIPE, stdout = subprocess.PIPE)
            p.stdin.write(self.text.encode())
            p.stdin.close()
            s = p.stdout.read().decode()
            return self.__class__(s) # be monad-y :P
        return cmd

    def __repr__(self):
        return self.text


# Not necessary at all, but makes the first call of each line in the examples file a bit nicer.
def echo(arg):
    return M().echo(arg)

def cat(arg):
    return M().cat(arg)

def find(arg):
    return M().find(arg)

def locate(arg):
    return M().locate(arg)



##################################################################
### Nice way to import the commands into the current namespace ###
##################################################################
# However, this is a bit fancier than we need, and has the cost
# of obscuring how simple this module actually is.
#
#def use(cmd):
#    f = lambda arg: M().__getattribute__(cmd)(arg)
#    f.__name__ = cmd
#    globals()[cmd] = f
#
#use("echo")
#use("cat")
#use("find")
#use("locate")


####################################################
### Monadic Lift, for absolutely no reason, lol. ###
####################################################
# 
# def f(s):
#     return s + "cake"
# 
# def Lift(f):
#     def F(S):
#         return M(f(S.text))
#     return F
# 
# Lift(f)(M('I like '))

# If we want to be pedantic about "really" being a monad (lol), change __init__ to this.
# If text is a string (usual case).
#if isinstance(text, str):
#    self.text = text
#
# If text is an M(...)
#elif isinstance(text, self.__class__):
#    self.text = text.text
#
# That's all. Any other case makes us non-monadic.
#else:
#    raise TypeError("Go home, {0}. You're drunk.".format(os.environ['USER'].capitalize()))
