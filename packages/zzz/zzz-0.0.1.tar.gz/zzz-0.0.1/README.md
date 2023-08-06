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
wait between the checks for the the aforementioned conditional equivalence.

## Author

`zzz` was written by David Gay.

## License

AGPLv3+. See `LICENSE` file for full text.
