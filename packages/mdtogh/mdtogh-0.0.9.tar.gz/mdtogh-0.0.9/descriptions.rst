==========================
Markdown to Github Html
==========================

Motivation
===============

Basically, You may want to convert md files into Html looks exactly like github does.

Maybe you would try `pandoc`_, but html it generates looks **not** very well.

So, I start writing this small tool, inspired by `grip`_

Features
=================

mdtogh can **convert** your md files into html files like github does with features belows:

- toc support
- custom toc(use one file to be toc)
- index.html for your book
- next/prev files link
- file regexp to select your md files
- fix relative link(ie. `<a href="01.md"></a>` => `<a href="01.html"></a>`)
- custom template
- offline renderer
- proxy support(respect https_proxy environment variable)
- cache support

demo
=================

I've generate a book written by julycoding: `The-Art-Of-Programming-By-July`_.

Demo link: `taop.marchtea.com`_

You can check on that.


Installation
==============

From `pypi`_

.. code-block:: bash

    $ pip install mdtogh 

Also, you can clone repo & install with setup.py.

.. code-block:: bash

	$ git clone https://github.com/marchtea/md_to_github_html.git
	$ cd md_to_github_html
	$ python setup.py install

**Maybe you will need add sudo**

Usage
==================

Generate one or more files

.. code-block:: bash

    $ cd mdfiles
	$ mdtogh 01.md 02.md 03.md
	
Generate all md files in current directory

.. code-block:: bash

    $ cd mdfiles
    $ mdtogh
    
Generate md files in other directory

.. code-block:: bash

	$ mdtogh ../mdfiles

Generate files with file reg support

.. code-block:: bash

	$ cd mdfiles
	$ mdtogh --file_reg='^\d.+\.md'

Generate files with toc & toc_depth support

.. code-block:: bash

	$ cd mdfiles
	$ mdtogh --toc --toc_depth=2 --file_reg='^\d.+\.md'

Generate files with additional book info

.. code-block:: bash

	$ cd mdfiles
	$ mdtogh --toc --book='book.json'
	
The format of book.json is given below.

Generate files with custom template

.. code-block:: bash

	$ cd mdfiles
	$ mdtogh --templates=path_to_templates 01.md
	
The rules for templates is given below.

Generate files with custom toc file

.. code-block:: bash

	$ cd mdfiles
	$ mdtogh --toc --toc_file=Readme.md --file_reg='^\d.+\.md'

Offline rendering:

.. code-block:: bash

	$ cd mdfiles
	$ mdtogh --offline 01.0.md

**Recommanded** options to generate book

.. code-block:: bash

	$ mdtogh --css --toc --book='book.json' --file_reg='your reg exp'

**Recommanded** options to generate several files

.. code-block:: bash

	$ mdtogh 01.md 02.md

For more options

.. code-block:: bash

	mdtogh -h
	
Something You May Notice
=================================

As to generate files exactly like github does, the easiest way is to use
`api`_ if offers. But it has its own `limits`_.

- 60 for anonymous requests an hour
- 5000 for requests using Basic Authentication an hour

So, you may using --user & --pass options

.. code-block:: bash

	$ mdtogh --user='your_github_username' --pass='your login password'
	
Your info are sended through https which is safe. mdtogh will not save any of it.


book.json
========================

.. code-block:: javascript 

    {
        "title": "Demo book",
        "description": "This is a book.",
        "coverimage": "demo.jpg"
    }

Custom Templates Support
========================

mdtogh now support custom templates. You can use --templates to specific where to locate templates. You should give at least three files belows:

- content.html
- toc.html
- index.html

mdtogh use `jinja2`_ as template engine.

For tutorial of template writing, please check `jinja doc`_

- content.html

content.html is used for generate standalone html file with things like head, body **after** content of md file is rendered by github or offline renderer.

mdtogh will pass several  parameters to content.html which you can use:

- filetitle 	*#booktitle in book.json`*
- content      *#contents after render by `github` or `offline renderer`*
- toc          *#not support yet*
- needtoc		 *#whether toc is needed*
- prevfile     *#link to prevfile. only used when `--toc` is set*
- nextfile     *#link to nextfile. only used when `--toc`is set*


toc.html

toc.html is used for generate table of content which will be used later in index.html. So, you don't need add html or body tag.


Parameters passed to toc.html.

- tocs 
- toc_depth

tocs

tocs is a list of headers. It's set like 

.. code-block:: javascript 

    [
        ['h1', 'top header', 'headerlink'],
        ['h2', 'sub header', 'header link'],
        ....
    ]

toc_depth

toc_depth is set by user. It refers the maxium depth of header. It's an integer value. ie.

.. code-block:: javascript 

	2

index.html

index.html is used for generate index.html for book. 

Parameters passed to toc.html:

- booktitle *#title in book.json*
- coverimage *#coverimage in book.json*
- description *#description in book.json*
- toc         *#toc rendered with toc.html*
- custom_toc  *#whether use custom_toc. custom_toc is rendered like normal md file*

TODO
===================
mdtogh is still on developing.

Features are developing or will be add later.

- support recursive options.
- add toc in content.html

Contibuting
===============

Any **help** will be **appreciated**.

- open issues if you find any questions
- complete one in TODO list
- add features you like
- feel free to open pull request

Links
=====================

- `Github repo`_
- `grip`_
- `github markdown api`_

Change Log
=====================

- 2014/4/30 0.0.9 add option: --timeout. set timeout for requests. add cache support. now it will skip file which is not changed.
- 2014/3/12 0.0.8 add option: --offline. offline rendering is supported.
- 2014/3/11 0.0.7 add option: --toc_file. user can specific one file as toc. relative link will be resolved automatically.
- 2014/3/6 0.0.6 add option: --encoding for offline renderer, fix relative link, add support for custom template
- 2014/3/5 0.0.5 add MANIFEST.in, fix pacakge wrapped by setup.py. Fix css link not include while rendering after first downloading css files
- 2014/3/4 0.0.3 fix error leads by unicode filename
- 2014/3/3 0.0.2 add --toc_depth support, fix get_html_name bug
- 2014/3/1 0.0.1 first release

Thanks
==========

Special thanks to `grip`_. Without its excellent work, this tool can't be done.

.. _limits: http://developer.github.com/v3/#rate-limiting
.. _api: http://developer.github.com/v3/markdown/
.. _github markdown api: http://developer.github.com/v3/markdown/
.. _pypi: https://pypi.python.org/pypi
.. _grip: https://github.com/joeyespo/grip
.. _pandoc: http://johnmacfarlane.net/pandoc/index.html
.. _The-Art-Of-Programming-By-July: https://github.com/julycoding/The-Art-Of-Programming-By-July
.. _taop.marchtea.com: http://taop.marchtea.com
.. _Github repo: http://github.com/marchtea/mdtogh
.. _jinja2: https://github.com/mitsuhiko/jinja2 
.. _jinja doc: http://jinja.pocoo.org/docs/
