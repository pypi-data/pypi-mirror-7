wireframe2html
==============
[![Build Status](https://travis-ci.org/chbrun/wireframe2html.svg?branch=master)](https://travis-ci.org/chbrun/wireframe2html)
[![Coverage Status](https://img.shields.io/coveralls/chbrun/wireframe2html.svg)](https://coveralls.io/r/chbrun/wireframe2html)

convert screens from wireframesketcher into html

Use : 
  - jinja2 : templating
  - foundation

Alpha version : only foundation widgets
   - alert
   - button
   - Topbar
   - Paragraph
   - Label
   - Table
   - Header

## Usage ##

```bash
python wireframe2html.py -s [screenName]
```

## Examples ##
There are 2 examples in examples directory :
  - Homepage.screen : simple hompage
  - Projects_list.screen : simple page with table

```bash
python wireframe2html.py -s Homepage
python wireframe2html.py -s Projects_list
```

Then open Homepage.html with your browser, and clic on Projects in TopBar
