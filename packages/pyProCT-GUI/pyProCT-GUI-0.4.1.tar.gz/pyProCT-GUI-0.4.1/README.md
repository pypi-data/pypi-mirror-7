pyProClust-GUI
==============
A browser-based wizard-style Graphical Used Interface that can be used to:
- Generate (and run) [pyProCT](https://github.com/victor-gil-sepulveda/pyProCT) projects.
- Visualize pyProCT project's results.

## Installation
pyProCT-GUI is quite easy to install using *pip*. Just write:

```Shell
> sudo pip install pyProCT-GUI
```

If pyProCT is not yet installed in your system it will install it and all its dependencies.

## Running it
```Shell
> python -m pyproctgui.gui.main
```
The GUI will start a web server and pop a browser window up.

## Used Javascript libraries
- [chemdoodle](http://web.chemdoodle.com/)
- [handlebars](http://handlebarsjs.com/)
- [jquery](http://jquery.com/)
	- [jquery.ui](http://jqueryui.com/)
	- [filetree](http://www.abeautifulsite.net/blog/2007/06/php-file-tree/)
	- [wizard](https://github.com/kflorence/jquery-wizard/) (Kyle Florence)
- [markdown](https://github.com/evilstreak/markdown-js)
- [spinjs](http://fgnass.github.io/spin.js/)
- [jqplot](http://www.jqplot.com/)
- [threejs](http://threejs.org/)


##Tutorial
Work In Progress!
This documentation is not complete yet. If you have any question, please use Github features or send a mail to : victor.gil.sepulveda@gmail.com


#BUGS
- Generating te script when choosing a dcd file does not work propperly. A new screen is needed to choose the "atom info" file.

#TODO
- Offload all calculations to pyProCT
- Explore ANY generated clustering (even those which were not selected). This implies generate "on the fly" rmsfs, centers etc.
