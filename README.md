# compprogutils

Because I got too lazy to type.

Install by pulling then running `pip install .`. This might go on PyPI once it gets polished enough.
As of now, requires you have a `~/.cpu` folder with some needed files. I'll figure out a way to package this in.

##### Basic usage:

```
cpu make-contest 5
```
prepares a folder with 5 problems.
```
cpu add-solution -n normal A.cpp
```
registers the solution file in `A.cpp` with name `normal`
```
cpu compile-solution normal
```
compiles the solution `normal`
```
cpu add-test
```
reads in a test from standard input. Generator programs are supported.
```
cpu run-solution normal -i 3
```
Feed test 3 into `normal`'s standard input.
```
cpu stress-test -r 10 normal brute largeGen
```
Use `largeGen` to make test cases. Attempt to break 	`normal`, using `brute`'s output as AC.

Most commands you'll need to run a lot have aliases.

### TODOs

- Documentation, tests, all the normal stuff
- Including the `~/.cpu` folder in the package setup
- Colorizing output + removing `stress-test`'s output for test
- Library code; dumping library code into current directory
- Support for interactive problems
- `online-judge-tools`-style `make-contest`
- More robust and usable `checker_utils` library

Contributions are accepted (and appreciated).

