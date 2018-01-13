################
### EXAMPLES ###
################

from unix import *

def examples():

    cat("/etc/hosts").grep("192").sort()

    find('. -type f -name *.mp4').grep('-i keyword').sort().sed('s@.*/@@g')

    locate('*.mp3').grep('-i linux.action.show').cowsay()

    locate('-i .png').grep('-Pi gentoo').xargs("-d '\n' basename -a")

# examples()

#################################################
### EXAMPLES: If you don't want to import '*' ###
#################################################

from unix import M

def examples2():

    M().cat("/usr/share/dict/cracklib-small").grep("anal").tac()

    M().echo("/etc/hosts").xargs('cat').grep("-P '^(\d{1,3}[.])\d{1,3}'").sort()

    M("/etc/hosts").xargs('cat').grep("-P '^(\d{1,3}[.])\d{1,3}'").sort() # same as above

    M().wget("-q -O - kernel.org").grep("""-Po '(?<=href=")[^"]+(?=")'""")

    # These all work
    M().cat("/etc/ld.so.conf").grep("-Po .../lib").sort().uniq()
    M().cat("/etc/ld.so.conf").grep("-Po .../lib").sort().uniq().cowsay()
    M().cat("/etc/ld.so.conf").grep("-Po .../lib").sort().uniq().xcowsay()

    M().locate('*.webm').grep('2017').xargs('vlc')

    # We can decide to break out of the monadic do-stuff-chain at any time
    # and start interacting with the rest of python, like lists and stuff.
    list(map(M().basename, M().locate('*.webm').grep('2017').text.split()))

    # This library makes me irrationally happy...
    M().locate('*.gif').grep('[0-9]chan').base64().base64('-d').xargs('eog')

# examples2()
