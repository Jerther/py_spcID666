# py_spcID666

Python script to get the ID666 tag, base and extended, from a SNES SPC file.

(Not tested with binary ID666 tags. Most are text anyways.)

Contributions welcome!

###Usage
From command line:
```sh
$ python spcid666.py snesmusic.spc
```

As a module:

```Python
import spcid666
spcid666.parse('snesmusic.spc')
```


###More info

http://wiki.superfamicom.org/snes/show/SPC+and+RSN+File+Format#extended-id666
http://www.johnloomis.org/cpe102/asgn/asgn1/riff.html

License
----
Free as in free beer! Any contribution is welcome.
