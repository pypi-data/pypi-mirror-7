CI Unit Test
============

CI Unit Test is a library which enables to retrieve the results of unit tests in JSON format. This may be used in custom Continuous Integration systems which need to process the results of unit tests.

The results can be saved as is to a NoSQL database, or can be returned as a Python dictionary in order to be combined with other information before being saved.

Usage
-----

The results in JSON format can be obtained like this::

    suite = unittest.TestLoader().loadTestsFromTestCase(TestsDemo)
    json = ciunittest.JsonTestRunner().run(suite, formatted=True)
    print(json)

The results as a dictionary can be obtained like this::

    suite = unittest.TestLoader().loadTestsFromTestCase(TestsDemo)
    result = ciunittest.JsonTestRunner().run_raw(suite)
    print('Done %d tests in %d ms.' %
          (len(result['results']), result['spentMilliseconds']))

The code is inspired by http://pythonhosted.org/gchecky/unittest-pysrc.html

If you have any question or remark, please contact me at arseni.mourzenko@pelicandd.com. Critics are also welcome, since I have used Python for only a few days, and probably get lots of things wrong.