======
bdt_sitemap
======

BDT Sitemap is a sitemap.xml generator for local copies of websites. It follows the official Sitemap protocol: http://www.sitemaps.org/protocol.html

The protocol is extended in one way for convenience; HTML files containing meta tags with the 'id' and 'content' attributes will have their data added to their sitemap entries. This can be very useful in having tools navigate a site and act based on page content, without actually loading the pages. There are many ways to use this functionality, I choose to use it to define a corner image for each page, and if undefined the corner image used by the parent directory's index.html page is used.

BDT Sitemap can be called as a library by importing bdt.sitemap, and calling create_sitemap, or by being run standalone as bdt_sitemap. Arguments are detailed below.

Requirements
============

BDT Sitemap requires Python 2.6 or 2.7, and beautiful soup 4 (automatically installed by pip if you pip install).

Term Definitions
================

For conciseness, here are some terms with specific definitions when used here in this Readme:

Item: A file or directory encountered while 

Usage
=====
Can be used as a library, or run standalone in the command line.


Supports two arguments:

	Domain:		In url form, the domain name for which you're generating sitemaps. Subdomains are also supported. Each domain and subdomain must be run separately. 'domain.com' and 'subdomain.domain.ru' are both valid.

	LocalPath:	Path to the website directory as stored locally. Platform agnostic.

WARNING: If the LocalPath argument is not passed, current directory will be assumed! You will be asked if this was a mistake, and given a chance to exit, but that's all! You will end up with sitemap.xmls all over the place if you're not careful!


Usage:

	bdt_sitemap mysite.com ~/sites/sitefolder

	bdt_sitemap tadeuszow.com /home/xenmen/sites/Tadeuszow-site/main

	bdt_sitemap daniel.tadeuszow.com C:\Users\Xenmen\sites\Tadeuszow-site\daniel


Usage as a library in WIP, and presently creates a global variable called emod_time, and defines three functions:

	init_emod_time()

	compare_emod_time(newtime)

	create_sitemap(domain, site_dir, ignorelist=[])


Only create_sitemap should ever be called, the other two are internal functions. Ignorelist is only supported in the library functionality, standalone functionality is WIP. Ignorelist is a list of strings, which, if found in the path to a file or directory, that directory will be skipped, and if in the name of a file or directory, then that file or directory will

It is recommended to use bdt_sitemap standalone, and not as a library, until version 1.0. 
