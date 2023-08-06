# zzz

Python library that waits until something happens.

## Benefit

You will no longer have to write annoying `while`/`time.sleep()` checks
to wait until a variable is euqal to a certain value.

## Usage

It's real simple.

All you gotta do is just have an import statement:

```
from zzz import z
```

After that, you use the `z` function on any
variable/object/function/method/thing ("VOFMT").  You pass the aforementioned
VOFMT as the first argument (`variable`), a `value` that the VOFMT should be
equal to, and lastly an optional `delay` argument, which determines how long to
wait between the checks for the aforementioned conditional equivalence.

## Author

`zzz` was written by David Gay.

## License

AGPLv3+. See `LICENSE` file for full text.

## A note about formatting

I believe that Markdown is superior to ReStructured Text and do not care that
PyPI only parses ReStructured Text. You will have to deal with it. You are a
smart person. Crack the readme open in your text editor, toss it through a
Markdown renderer, or deal with it. You will have many worse moments before
your continual decay leads to your inevitable final breath and the collection
of atoms called "you" disperse and take their place within other beings.
