# Fatafat - publish quickly!

Fatafat is a minimalistic static blog generator written in Python. It is also an offline blogging tool with **simple** and **quick** publishing options.

## With Fatafat you can ...

* Write blog articles in Markdown.
* Publish an article to a remote host (currently Github) using a single command.
* Test changes to blog theme, blog articles in a local *dev* version of your blog.
* Focus more on writing!

## Installation

To install fatafat, simply:

	$ pip install fatafat

## Prerequisites

### Generate ssh keys

Currently [Github](http://pages.github.com) is the only remote host which is supported. To publish to Github from command line, you will need to setup your ssh keys. Read details [here](https://help.github.com/articles/generating-ssh-keys).

### Create empty Github project

Fatafat pushes to the repository *github_username*.github.io. Make sure that the empty repository (DO NOT create the readme or the .gitignore files) is created before you use Fatafat.
	
## Why the name "Fatafat"?

I say why not! "Fatafat" means "quick" in Hindi.

## Found issues?

Currently, Fatafat is a "toddler" project and is being actively developed. I am using it for my own [blog](http://isubuz.github.io). Incase you run into issues, please [log](https://github.com/isubuz/fatafat/issues) the same. 

If you find the project useful, why not look into the issues yourself and send pull requests!

## Usage

### Command Line Interface

When installed, ``fatafat`` command is available for use. This command can be used to perform various actions on the blog. Run ``fatafat --help`` for details. To get help on individual action, run ``fatafat <action> --help``. Note that the ``fatafat`` command must be run at the root of the directory which contains your blog.

This [cheatsheet](#cheatsheet) lists all possible actions that can be performed using the ``fatafat`` command.

### Creating a new blog

First create the empty Github repository *github_username*.github.io. 

To create a new blog in ``bubblewrap`` directory:

	$ mkdir bubblewrap
	$ cd bubblewrap
	$ fatafat start

The ``start`` option prompts the user for blog configuration details. The following details are requested:

* blog title - title of your blog
* production URL - remote URL of your blog. Eg. http://isubuz.github.io
* development URL - local URL of your blog. Eg. http://localhost:8000
* github username
* disqus sitename

Once done, the following directories will be created:

	bubblewrap
	|-- contents
	|-- prod
	|-- dev
		
All articles go into the ``contents`` directory. The directory structure for ``prod`` and ``dev`` is same and stores the production version and the development version of the blog. 

	|-- config.py			# blog configuration file
	|-- data				# blog data files
	|-- site				# static output
	|   |-- README.md
	|   |-- articles		# generated HTML files for articles
	|   |-- assets			# css, js files
	|-- themes
	|   |-- simi
	|   |   |-- assets		# css, js files
	|   |   |-- templates	# jinja2 templates

There are few important differences between the ``dev`` and the ``prod`` directory.

* ``config.py`` in both directories are setup such that the URLs generated in the static output is correct i.e. local URL for ``dev`` and remote URL for ``prod``. This helps because you can run ``python -m SimpleHTTPServer`` in ``dev/site`` or ``prod/site`` to see and navigate through the changes you made to your blog
* ``site`` directory in ``prod`` is a ``git`` repository.

### Add a new article

To add a new article, simply create a new file with ``.md`` extension under ``contents``. Articles belonging to a common theme can be grouped in a directory. E.g.

	$ cd bubblewrap
	$ vim contents/loner.md
	$ vim contents/python/meta_what.md
	$ vim contents/python/why_should_i_decorate.md
	
Each article has associated metadata, some required and some optional. The metadata starts from the first line of the document and is separated from the article content by a blank line. 

E.g. ``contents/loner.md`` can look like - 

	Title: I am a lonely article
	Summary: My story
	Date: 27-07-1983
	Status: draft
	
	I am lonely, because I am at the root!

``Title`` and ``Date`` are **required**. Currently ``Date`` must be in ``DD-MM-YYYY`` format. Support for other formats could be added later.
 
 ``Summary`` and ``Status`` are optional. If ``Status`` is absent, the article is considered to be published.
 
### Publish article(s)

To publish an article, ``cd`` to the root of the blog directory and run ``fatafat publish -f <rel_path_to_article>`` in terminal. E.g -

	$ cd <path_to_blog>
	$ fatafat publish -f contents/loner.md
	
That's it!

The above command will update the local development blog only. To update the production blog specify option ``--prod``. To push the changes to Github, specify option ``--sync``. See [cheatsheet](#cheatsheet) for more details.

	$ cd <path_to_blog>
	$ fatafat publish -f contents/loner.md --prod --sync

To publish more than one article, pass the relative paths of the all the articles to the ``fatafat publish -f`` command. E.g - 

	$ cd <path_to_blog>
	$ fatafat publish -f contents/loner.md contents/python/meta_what.md

To publish all articles, simply use ``fatafat publish``. E.g -

	$ cd <path_to_blog>
	$ fatafat publish

### Removing an article

Currently, removing an article or renaming a markdown file isn't handled entirely correctly. The HTML file generated for the deleted/renamed article remains in the ``site`` directory and has to be removed manually.

This is on the top of my list of TODOs. So it should be addressed soon.

## Themes

Currently Fatafat comes with the default theme [simi](). But you add new themes easily. 

* Create a directory similar to the default theme and put in under the ``themes`` directory of your blog.
* Update the ``THEME`` field in ``config.py`` to use the new theme.

Every theme has two folders, ``assets`` and ``templates``. ``assets`` stores the javascript and the css files. ``templates`` stores the jinja2 templates used to generate the static output. Currently fatafat looks for ``index.jinja2`` and ``article.jinja2`` under the templates directory.

The following variables are available in template ``article.jinja2``:

* article.title
* article.summary
* article.content
* article.date

The following variables are available in template ``index.jinja2``:

* articles - which is a list of articles. Each article has the same attributes as above.

The following variables are available in all templates:

* SITENAME - blog title
* SITEURL - blog URL 

You might have observed that the template variables names matches to those in Pelican. The goal is to make pelican themes compatible with fatafat.

## Cheatsheet <a name="cheatsheet"></a>

The ``fatafat`` command must be run at the root of the directory which stores the blog files. The following commands can be run in terminal to perform various actions on the blog:

	# Create a new blog
	$ fatafat start
	
	# Publish all articles to dev directory
	$ fatafat publish
	
	# Publish a single article to dev directory
	$ fatafat publish -f contents/article1.md
	
	# Publish multiple articles to dev directory
	$ fatafat publish -f contents/article1.md contents/group/article2.md contents/article3.md
	
	# Publish all articles to prod directory
	$ fatafat publish --prod
	
	# Publish all articles to prod directory and sync with remote host
	$ fatafat publish --prod --sync
	
	# Publish a single article to prod directory
	$ fatafat publish -f contents/article1.md --prod
	
	# Publish a single article to prod directory and sync with remote host
	$ fatafat publish -f contents/article1.md --prod --sync
	
	# Publish multiple articles to prod directory
	$ fatafat publish -f contents/article1.md contents/group/article2.md --prod
	
	# Publish multiple articles to prod directory and sync with remote host
	$ fatafat publish -f contents/article1.md contents/group/article2.md --prod --sync

## Contact / Feedback

Send me a message at "i DOT subhajit DOT ghosh AT gmail DOT com" with any feedback.