Zephyr
======

Zephyr is an introductory language for programming beginners. Its main goals are simplicity, ease of learning, writability, and readability.

Why another programming language?
---------------------------------

Many languages taught in beginning programming, such as C++ and Java, were designed for general programming use. They often have cryptic or overcomplicated syntax that can discourage beginners, hindering their learning of general programming skills. Zephyr attempts to get out of the way as much as possible so beginners can concentrate on learning _programming_, not the quirks of a particular programming language.

Zephyr's _syntax_ is designed to read easily, avoiding cryptic abbreviations in favor of English keywords. While this makes programs longer, it also lowers a beginner's learning curve. The syntax draws inspiration from BASIC and Python, among other sources.

Zephyr is _interpreted_, eliminating the extra step of compiling, and _dynamically typed_, eliminating the extra step of defining variables.

Why learn this:

```C++
#include <iostream>
using namespace std;
int main()
{
    for(int i = 1; i <= 5; i++)
    {
        cout << i << " Hello world!" << endl;
    }
    return 0;
}
```

... when you could learn this:

```
for i from 1 to 5
    print i, "Hello world!"
next
```

For more examples, see the Programs subdirectory of this repository.

Limitations
-----------

While Zephyr is conceived of as a beginners' programming langauge, the current implementation is incomplete and not entirely user-friendly. Some of these problems are more easily solved than others. In order from most to least likely to be fixed:

- Zephyr should support operator precedence. Currently, all compound expressions must be fully parenthesized: `(x > 0) and (x < (y + 1))`.
- Users should not have to use relative or absolute paths in order to call the interpreter from any directory. At the moment, the usage `python zephyr.py program.zeph` only works if both the Zephyr implementation files and program.zeph are in the current working directory. A setup script should be provided to allow the usage `python zephyr.py program.zeph`, or, better, `zephyr program.zeph`.
- Error messages should include line numbers.
- Python-specific errors should not be displayed to the user, or at least should come with an explanation of, "You've found a bug in the Zephyr implementation."
- Zephyr should come with documentation.
- Error messages should be more informative for beginners: for instance, instead of `Encountered syntax error: was not expecting '"'`, the interpreter should say something like, `It looks like you're missing a quotation mark at the end of your string, line 6.`
- The user dependency on Python should be removed by packaging Zephyr as an executable.
- Zephyr should come with an IDE.

Installation and use (Windows)
------------------------------

1. Install Python 3.x ([python.org](http://python.org/downloads)).
2. `git clone` a local copy of this repository.
3. The Zephyr interpreter is zephyr.py. Pass your Zephyr program's name to it as a command-line argument. Alternately, you can edit the `defaultFile` variable and run zephyr.py without arguments.

**Example:**

To run the Hello World program, navigate to the Zephyr directory in the command prompt and execute `python zephyr.py Programs\helloWorld.zeph`.

(Tested on Windows XP and 7.)

Installation and use (Linux)
------------------------------

1. `git clone` a local copy of this repository.
2. The Zephyr interpreter is zephyr.py. Pass your Zephyr program's name to it as a command-line argument. Alternately, you can edit the `defaultFile` variable and run zephyr.py without arguments.

**Example:**

To run the Hello World program, navigate to the Zephyr directory and execute `python3 zephyr.py Programs/helloWorld.zeph`.

(Tested on Ubuntu 12.04.)

History
-------

Zephyr was created by David Loscutoff in 2010 for his Senior Thesis as a Computer Science undergrad at the University of Nebraska at Omaha.

License
-------

The code in this repository is released under the GNU General Public License, version 3. A copy can be found in the `LICENSE.txt` file.

Copyright (c) David Loscutoff, 2014.
