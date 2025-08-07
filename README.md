# bin

A unix shell monad.

## examples

```python
import bin

bin.cat('/etc/hosts').grep('[0-9]*')

bin.curl('-s icanhazip.com')

bin.cowsay('hello')
```
