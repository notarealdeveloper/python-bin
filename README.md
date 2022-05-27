# unix.py

A unix shell monad.

## examples

```python

import unix

unix.cat('/etc/hosts').grep('[0-9]*')

unix.curl('-s icanhazip.com')

unix.cowsay('hello')
```
