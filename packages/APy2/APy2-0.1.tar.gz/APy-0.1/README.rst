=====
 APy
=====

With *APy* you can make a Python API and then, serve it online, make scalable 
intercommunicable applications, document and organize your code, make command 
line interfaces quickly, reuse it in other applications, and more cool stuff...

*APy* provides utilities to easily create aplications or modules that must 
interact with other applications or modules. Its just that simple.

*APy* can receive python functions (and restful objects soon) and collects data,
doc, and annotations of it. Then a *APy* stores all functions and manages
them by context. One can also retrive a *Context* object to easily access
all the functions of that given context.

Some simple usage looks like this::

    #!/usr/bin/env python

    from apy.core.api import Api

    api = Api()

    @api.add()
    def foo(a, b, c):
    	return a * b + c

    with api.context("web"):
    	@api.add()
    	def foo(a, b):
    		return a + b

    if __name__ == "__main__":
    	with context("web") as web:
    		print(web.foo())


To download and install PyApiMaker use::

	pip install git+https://github.com/Jbat1Jumper/APy.git

Or any python3 pip shortcut that you may have.


`Full documentation here <https://github.com/Jbat1Jumper/APy/wiki>`