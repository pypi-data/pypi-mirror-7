History
-------
This recipe is a fork of yaco.recipe.patch.


Supported options
-----------------

The recipe supports the following options:

patch
    Path to patch
    Recipe supports a list of patch one by line.
    Eg.
    patch = path/sub/patch1.patch   # comments are supported too
            path/sub/patch2.patch   # another one
            ...
            
patchlocation
    Location to apply patch

binary-patch
    Location of patch binary. Use patch in $PATH by default if any is specified.

update_mode
    'apply' : patch will be re-applied at each update
    'reverse_then_apply': path will be reversed then reapply
    'do_nothing' (DEFAULT): ...   

Example usage
-------------

We'll start by creating a buildout that uses the recipe::

    >>> write('buildout.cfg',
    ... """
    ... [buildout]
    ... parts = testpatch
    ...
    ... [testpatch]
    ... recipe = inouk.recipe.patch
    ... patch = %(patch)s
    ... patchlocation = %(patchlocation)s
    ... """ % { 'patch' : 'patch/example-test.patch', 'example/' : 'value2'}
    ... update_mode = apply
    ...)

Running the buildout gives us::

    >>> print 'start', system(buildout) 
    Installing testpatch.


