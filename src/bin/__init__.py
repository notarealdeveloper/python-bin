#!/usr/bin/env python3

__all__ = (
    'Unix',
    'Lines',
)

import os
import sys
import glob
import shlex
import subprocess

def get_executables():
    executables = []
    for dirname in os.getenv('PATH').split(':'):
        for pathname in glob.glob(f"{dirname}/*"):
            if os.path.exists(pathname):
                if os.stat(pathname).st_mode & 0o111:
                    basename = os.path.basename(pathname)
                    executables.append(basename)
    return sorted(set(executables))

binary_to_identifier = {k:k.replace('-', '_') for k in get_executables()}
identifier_to_binary = {v:k for k,v in binary_to_identifier.items()}

class Unix:

    """ A unix shell monad """

    def __new__(cls, arg=""):
        """
            Conceptually this is just setting "self.text=text",
            but with an extra bit to ensure idempotence and
            make us monadic.
        """
        if isinstance(arg, cls):
            self = arg
        else:
            self = super().__new__(cls)
            self.text = arg
        return self

    def __getattribute__(self, name):
        try:    return super().__getattribute__(name)
        except: return self.__getattribute_as_unix_cmd__(name)

    def __getattribute_as_unix_cmd__(self, name):
        """ This is where the magic happens """
        binary_name = identifier_to_binary.get(name, name)
        def cmd(arg = ""):
            arg = str(arg)
            process = subprocess.Popen(
                [binary_name] + shlex.split(arg),
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE
            )
            self_as_text = self.text.encode()
            process.stdin.write(self_as_text)
            process.stdin.close()
            output_as_text = process.stdout.read().decode()
            return self.__class__(output_as_text) # be monadic
        return cmd

    def __eq__(self, other):
        return str(self) == str(other)

    def __repr__(self):
        return self.text

    def lines(self, char = "\n"):
        # turn ourselves into a lines object
        return Lines(self.text.strip(char).split(char))

    split = lines

    def __or__(self, string):
        """
            Strip the input so that piping into commands that
            happen to start with spaces doesn't fail. e.g.,
            typing '  cowsay ' should be the same as 'cowsay'
        """
        cmd_raw = string.strip(' ')
        i = cmd_raw.find(' ')
        if i > 0:
            cmd, args = (cmd_raw[:i], cmd_raw[i+1:])
            return getattr(self, cmd)(args)
        else:
            cmd = cmd_raw
            return getattr(self, cmd)()

    def __dir__(self):
        return sorted(binary_to_identifier.values())



class Lines(list):

    """
    A monad representing lines of text.

    This class collects operations commonly used on lists
    of lines of text: one of the conceptual primitives of
    unix shell programming.

    It's "monadic" in the sense that all its methods return
    an instance of itself, which is what allows for the nice
    "guaranteed composition" style of programming that makes
    the unix shell itself so pleasant to work with. The one
    exception to this is "join", which turns us back into a
    Unix() object, representing a simple string-like text stream.
    """

    def map(self, f):
        return self.__class__(map(f, self))

    def filter(self, f):
        return self.__class__(filter(f, self))

    # Note: `foreach` and `nonempty` were intended to be
    # different from `map` and `filter` above, but the
    # fact that `Lines` is currently a subclass of list
    # causes the iterators to be expanded into lists,
    # making the results the same.

    def foreach(self, f):
        return self.__class__((f(line) for line in self))

    def nonempty(self):
        return self.__class__((line for line in self if line))

    def split(self, char = '\n'):
        return self.__class__(
            self.__class__(line.split(char)) for line in self
        )

    def join(self, char = '\n'):
        """
            Transforms a Lines object back into a
            Unix object containing the same lines.

            When transitioning back to a unix object,
            append a newline at the end if we're joining
            in the default way: namely, turning a list of
            lines into actual lines.

            If called with any argument other than '\n',
            don't add an extra copy of char at the end.
            This seems like a kludge at first glance,
            but in practice this is almost always the
            desired behavior.
        """
        end = '\n' if char == '\n' else ''
        try:
            return Unix(char.join(self) + end)
        except TypeError:
            # This is needed if we have a Lines object containing Unix
            # instances rather than str instances, for instance, from:
            #
            # >>> unix.find('/etc/systemd -type f').head('-2').lines().map(unix.cat)
            #
            # Which creates a Lines object containing Unix objects.
            # A problem arises if we then try to call `.join()` on the
            # resulting Lines object. The only alternative solution
            # would be to make this work naturally by making Unix into
            # a subclass of `str`, but the added inconvenience of subclassing
            # an immutable type makes this solution much more parsimonious.
            return Unix(char.join(str(line) for line in self) + end)

    def __getattribute__(self, name):
        try:    return super().__getattribute__(name)
        except: return self.__getattribute_as_unix_cmd__(name)


    def __getattribute_as_unix_cmd__(self, name):
        """ This is where the magic happens (again) """
        def cmd(arg = ""):
            process = subprocess.Popen(
                [name] + shlex.split(arg),
                stdin = subprocess.PIPE,
                stdout = subprocess.PIPE
            )
            input_as_unix = self.join()
            input_as_text = input_as_unix.text.encode()
            process.stdin.write(input_as_text)
            process.stdin.close()
            output_as_text  = process.stdout.read().decode()
            output_as_unix  = Unix(output_as_text)
            output_as_lines = output_as_unix.lines()
            return self.__class__(output_as_lines) # be monadic
        return cmd


UPGRADE_MODULE_TO_CLASS_INSTANCE = True

if UPGRADE_MODULE_TO_CLASS_INSTANCE:

    # upgrade the module to an instance on import!
    mod = Unix()
    sys.modules[__name__] = mod

else:

    def __getattr__(attr):

        """ Module level getattr to allow us to call, e.g.,

            unix.cat('/etc/hosts')

            without defining a top-level attribute named 'cat', and
            without having to instantiate the class unix before we
            can use it.
        """

        return getattr(Unix(), attr)

