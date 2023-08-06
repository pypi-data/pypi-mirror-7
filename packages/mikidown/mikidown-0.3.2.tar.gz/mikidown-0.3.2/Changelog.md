# Mikidown Changelogs

## Version 0.3.2

- asciimathml markdown extensions is supported. If you don't have it grab it from [here [AUR]](https://aur.archlinux.org/packages/python-asciimathml-git) or [here [github]](https://github.com/mtahmed/python-asciimathml)
- The MathJax javascript file by default points to the CDN. You can point it to a different place if you want.
- A dialog for configuring notebook settings has been added. You can easily change the order of how markdown uses its extensions by dragging and dropping. Disabling and enabling's also as easy as clicking a checkmark next to the corresponding item.
- Rudimentary support for highlighting asciimathml blocks is there
- There's a box in the index tab that can be used to easily access items without clicking through the note tree. Type path/to/note (where that is the path to your note) to check it out.
- Highlighting for setext style headers works too.

### Enabling asciimathml
For existing notebooks, will be autoenabled on new ones. This is for enabling it on old ones (all of this can easily be done in the notebook settings dialog too):

0. Make sure that the user has the python 3 version of [asciimathml](https://github.com/mtahmed/python-asciimathml) installed.
1. in notebookPath/notebook.conf, look for the line that says "extensions =". Add asciimathml to the end of it.
2. in notebookPath/notebook.conf, add a line that says:```mathJax = /path/to/your/MathJax.js```
For most people, pointing to the mathjax CDN mentioned below is fine:
http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML
3. Type away some asciimathml. The script pointed to in mathJax should auto-process the MathML elements spat out by asciimathml.

After following these instructions, this text //should// be processed with mathjax:

$$
sqrt 1^2^3^4
$$

### Disabling asciimathml

1. in notebookPath/notebook.conf, look for the line that says "extensions =". Remove asciimathml from it.

## Version 0.3.0

- Notebook folder redesigned, see [#23]
        // notebook.conf attachments/ css/ notes/ _site/ //

- When attachment (image or document) is inserted, it is saved into **attachment/** folder
- Spell checking support with enchant, see [#24]
        new optional dependencies: [pyenchant]

- A simple static site generator incorporated

        mikidown generate
        mikidown preview


[#23]: https://github.com/rnons/mikidown/issues/23
[#24]: https://github.com/rnons/mikidown/issues/24
[pyenchant]: https://pypi.python.org/pypi/pyenchant
