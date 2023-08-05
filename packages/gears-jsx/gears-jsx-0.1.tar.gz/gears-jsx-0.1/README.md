gears-jsx
==================

JSX compiler for Gears. 

Bundled [react-tools](https://github.com/facebook/react) version: 0.10.0


Installation
------------

Install `gears-jsx` with pip:

    $ pip install gears-jsx


Requirements
------------
- [node.js](http://nodejs.org)


Usage
-----

Add `gears_jsx.JSXCompiler` to `environment`'s compilers registry:

    from gears_jsx import JSXCompiler
    environment.compilers.register('.jsx', JSXCompiler.as_handler())

If you use Gears in your Django project, add this code to its settings:

    GEARS_COMPILERS = {
        '.jsx': 'gears_jsx.JSXCompiler',
    }
