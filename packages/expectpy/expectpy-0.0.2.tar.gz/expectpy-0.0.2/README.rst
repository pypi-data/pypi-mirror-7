################
expectpy 
################
.. image:: https://travis-ci.org/float1251/expectpy.svg?branch=master
    :target: https://travis-ci.org/float1251/expectpy
    
this is assertion library like chai.expect_

.. _chai.expect: http://chaijs.com/

***********************
not yet implemented
***********************
* deep
* keys
* instanceof
* respondTo
* itself
* closeTo
* members

************
Example
************

.. code-block:: python

    from expectpy import expect
    expect(1).to.be.equal(1)
    expect("1").to.be.length(1)
    expect([1, 2, 3]).to_not.contain(4)

**********
License
**********

(The MIT License)

Copyright (c) 2011-2014 takahiro iwatani taka.05022002@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
