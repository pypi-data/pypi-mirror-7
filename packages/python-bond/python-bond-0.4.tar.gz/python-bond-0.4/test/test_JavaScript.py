from __future__ import print_function
import bond
from bond.JavaScript import JavaScript
from test import *

def test_basic():
    js = JavaScript(timeout=1)
    js.close()


def test_call_marshalling():
    js = JavaScript(timeout=1)

    js.eval_block(r'function test_str() { return "Hello world!"; }')
    assert(str(js.call('test_str')) == "Hello world!")

    js.eval_block(r'function test_array() { return [42]; }')
    assert(js.call('test_array') == [42])

    js.eval_block(r'function test_number() { return 42; }')
    assert(js.call('test_number') == 42)

    js.eval_block(r'function test_undefined() { return; }')
    assert(js.call('test_undefined') is None)

    js.eval_block(r'function test_null() { return null; }')
    assert(js.call('test_null') is None)

    js.eval_block(r'function test_boxed_undefined() { return [undefined]; }')
    ret = js.call('test_boxed_undefined')
    assert(str(ret) == str([None]))

    js.eval_block(r'function test_nothing() { return undefined; }')
    assert(js.call('test_nothing') is None)

    js.eval_block(r'function test_identity(arg) { return arg; }')
    js_identity = js.callable('test_identity')
    for value in [True, False, 0, 1, "String", [], [u"String"]]:
        ret = js_identity(value)
        print("{} => {}".format(value, ret))
        assert(str(ret) == str(value))

    js.eval_block(r'function test_multi_arg(arg1, arg2) { return arg1 + " " + arg2; }')
    assert(str(js.call('test_multi_arg', "Hello", "world!")) == "Hello world!")

    js.eval_block(r'function test_nested(arg) { return test_identity(arg); }')
    js_nested = js.callable('test_nested')
    for value in [True, False, 0, 1, "String", [], [u"String"]]:
        ret = js_nested(value)
        print("{} => {}".format(value, ret))
        assert(str(ret) == str(value))


def test_call_simple():
    js = JavaScript(timeout=1)

    # define a function and call it
    js.eval_block('function test_simple() { return "Hello world!"; }')
    js.eval('test_simple()')

    # test the call interface
    ret = js.call('test_simple')
    assert(str(ret) == "Hello world!")

    # try 'callable'
    js_simple = js.callable('test_simple')
    ret = js_simple()
    assert(str(ret) == "Hello world!")


def test_call_stm():
    js = JavaScript(timeout=1)

    # test the call interface with a normal function
    js.eval_block('function copy(arg) { return arg; }')
    ret = js.call('copy', "Hello world!")
    assert(str(ret) == "Hello world!")

    # try with an object
    ret = js.call('String', "Hello world!")
    assert(str(ret) == "Hello world!")

    # try with a statement
    ret = js.call('function(arg) { return arg; }', "Hello world!")
    assert(str(ret) == "Hello world!")


def test_call_error():
    js = JavaScript(timeout=1)
    js.eval_block('function test_simple(arg) { return eval(arg); }')
    ret = js.call('test_simple', 1)
    assert(ret == 1)

    # unknown function
    failed = False
    try:
        js.call('test_undefined')
    except bond.RemoteException as e:
        print(e)
        failed = True
    assert(failed)

    # check that the environment is still alive
    assert(js.eval('1') == 1)


def test_eval():
    js = JavaScript(timeout=1)

    # literal values
    assert(js.eval('1') == 1)
    assert(js.eval('null') is None)
    assert(js.eval('undefined') is None)

    # expression
    assert(js.eval('1 + 1') == 2)

    # define a variable
    js.eval_block('var x = 1;')
    assert(js.eval('x') == 1)

    # define a function
    js.eval_block(r'function test_js(arg) { return arg + 1; }')
    assert(js.eval('test_js(0)') == 1)


def test_eval_error():
    js = JavaScript(timeout=1)

    # try a correct statement before
    assert(js.eval('1') == 1)

    # broken statement
    failed = False
    try:
        js.eval('"')
    except bond.RemoteException as e:
        print(e)
        failed = True
    assert(failed)

    # check that the environment is still alive
    assert(js.eval('1') == 1)


def test_ser_err():
    js = JavaScript(timeout=1, trans_except=True)

    # construct an unserializable type
    js.eval_block(r'''
    var circular = [];
    circular.push(circular);
    var fun_ref = function() {};
    function func() { return circular; }
    function exceptional() { throw circular; }
    ''')

    # try to send it across
    failed = False
    try:
        js.eval('circular')
    except bond.SerializationException as e:
        print(e)
        failed = (e.side == "remote")
    assert(failed)

    # ensure the env didn't just die
    assert(js.eval('1') == 1)

    # try to send a function
    failed = False
    try:
        js.eval('fun_ref')
    except bond.SerializationException as e:
        print(e)
        failed = (e.side == "remote")
    assert(failed)

    # ensure the env didn't just die
    assert(js.eval('1') == 1)

    # try to send a function definition
    failed = False
    try:
        js.eval('function test() {}')
    except bond.SerializationException as e:
        print(e)
        failed = (e.side == "remote")
    assert(failed)

    # ensure the env didn't just die
    assert(js.eval('1') == 1)

    # ... with call (return)
    failed = False
    try:
        js.call('func')
    except bond.SerializationException as e:
        print(e)
        failed = (e.side == "remote")
    assert(failed)

    # ensure the env didn't just die
    assert(js.eval('1') == 1)

    # ... with an exception
    failed = False
    try:
        js.call('exceptional')
    except bond.SerializationException as e:
        print(e)
        failed = (e.side == "remote")
    assert(failed)

    # ensure the env didn't just die
    assert(js.eval('1') == 1)


def test_exception():
    js = JavaScript(timeout=1)

    # remote exception
    js.eval_block('function exceptional() { throw new Error("an error") }')

    # ... in eval
    failed = False
    try:
        js.eval('exceptional()')
    except bond.RemoteException as e:
        print(e)
        failed = True
    assert(failed)

    # ... in eval_block
    failed = False
    try:
        js.eval_block('exceptional()')
    except bond.RemoteException as e:
        print(e)
        failed = True
    assert(failed)

    # ... in call
    failed = False
    try:
        js.call('exceptional')
    except bond.RemoteException as e:
        print(e)
        failed = True
    assert(failed)


def test_export():
    def call_me():
        return 42

    js = JavaScript(timeout=1)
    js.export(call_me, 'call_me')
    assert(js.call('call_me') == 42)


def test_export_redef():
    js = JavaScript(timeout=1)

    def call_me():
        return 42

    js.export(call_me)
    try:
        js.export(call_me)
    except:
        pass

    assert(js.call('call_me') == 42)


def test_export_invalid():
    js = JavaScript(timeout=1)

    def call_me():
        return 42

    try:
        # Interestingly enough, this works in Js, though it won't be
        # possible to call the function normally
        js.export(call_me, 'invalid name')
    except Exception as e:
        print(e)

    assert(js.eval('1') == 1)


def test_export_recursive():
    js = JavaScript(timeout=1)

    # define a remote function
    js.eval_block(r'function func_js(arg) { return arg + 1; }')
    func_js = js.callable('func_js')
    assert(func_js(0) == 1)

    # define a local function that calls the remote
    def func_python(arg):
        return func_js(arg + 1)

    assert(func_python(0) == 2)

    # export the function remotely and call it
    js.export(func_python, 'remote_func_python')
    remote_func_python = js.callable('remote_func_python')
    assert(remote_func_python(0) == 2)

    # define a remote function that calls us recursively
    js.eval_block(r'function func_js_rec(arg) { return remote_func_python(arg) + 1; }')
    func_js_rec = js.callable('func_js_rec')
    assert(func_js_rec(0) == 3)

    # inception
    def func_python_rec(arg):
        return func_js_rec(arg) + 1

    js.export(func_python_rec, 'remote_func_python_rec')
    js.eval_block(r'function func_js_rec_2(arg) { return remote_func_python_rec(arg) + 1; }')
    func_js_rec_2 = js.callable('func_js_rec_2')
    assert(func_js_rec_2(0) == 5)


def test_export_ser_err():
    def call_me(arg):
        pass

    js = JavaScript(timeout=1)
    js.export(call_me, 'call_me')
    js.eval_block('var fd = function(){};')

    failed = False
    try:
        js.eval('call_me(fd)')
    except bond.SerializationException as e:
        print(e)
        failed = (e.side == "remote")
    assert(failed)

    # ensure the env didn't just die
    assert(js.eval('1') == 1)


def test_export_except():
    js = JavaScript(timeout=1)

    def gen_exception():
        raise Exception("test")

    js.export(gen_exception)
    js.eval_block(r'''
    function test_exception()
    {
        var ret = false;
        try { gen_exception(); }
        catch(e) { ret = true; }
        return ret;
    }''')

    assert(js.call('test_exception') == True)


def test_output_redirect():
    js = JavaScript(timeout=1)

    # stdout
    js.eval_block(r'console.log("console.log: Hello world!");')
    js.eval_block(r'process.stdout.write("stdout: Hello world!\n");')
    assert(js.eval('1') == 1)

    # stderr
    js.eval_block(r'console.error("console.error: Hello world!");')
    js.eval_block(r'process.stderr.write("stderr: Hello world!\n");')
    assert(js.eval('1') == 1)


def test_trans_except():
    js_trans = JavaScript(timeout=1, trans_except=True)
    js_not_trans = JavaScript(timeout=1, trans_except=False)

    code = r'''function func() { throw func; }'''

    # by default exceptions are transparent, so the following should try to
    # serialize the code block (and fail)
    js_trans.eval_block(code)
    failed = False
    try:
        ret = js_trans.call('func')
    except bond.SerializationException as e:
        print(e)
        failed = (e.side == "remote")
    assert(failed)

    # ensure the env didn't just die
    assert(js_trans.eval('1') == 1)

    # this one though will just always forward the remote exception
    js_not_trans.eval_block(code)
    failed = False
    try:
        ret = js_not_trans.call('func')
    except bond.RemoteException as e:
        failed = True
    assert(failed)

    # ensure the env didn't just die
    assert(js_not_trans.eval('1') == 1)


def test_export_trans_except():
    js_trans = JavaScript(timeout=1, trans_except=True)
    js_not_trans = JavaScript(timeout=1, trans_except=False)

    def call_me():
       raise RuntimeError("a runtime error")

    # by default exceptions are transparent, so the following should try to
    # serialize RuntimeError in JSON (and fail)
    js_trans.export(call_me)
    js_trans.eval_block(r'''
    function test_exception()
    {
        var ret = false;
        try { call_me(); }
        catch(e)
        {
            ret = e.toString().indexOf("SerializationException") >= 0;
        }
        return ret;
    }
    ''')
    assert(js_trans.call('test_exception') == True)

    # this one though will just generate a string
    js_not_trans.export(call_me)
    js_not_trans.eval_block(r'''
    function test_exception()
    {
        var ret = false;
        try { call_me(); }
        catch(e)
        {
            err = e.toString()
            ret = (err.indexOf("SerializationException") < 0
                    && err.indexOf("a runtime error") >= 0);
        }
        return ret;
    }
    ''')
    assert(js_not_trans.call('test_exception') == True)


def test_stack_depth():
    def no_exception():
        pass

    def gen_exception():
        raise Exception("test")

    def gen_ser_err():
        return lambda x: x

    # check normal stack depth
    js = JavaScript(timeout=1)
    assert(bond_repl_depth(js) == 1)

    # check stack depth after calling a normal function
    js = JavaScript(timeout=1)
    js.export(no_exception)
    js.call('no_exception')
    assert(bond_repl_depth(js) == 1)

    # check stack depth after returning a serializable exception
    js = JavaScript(timeout=1)
    js.export(gen_exception)
    got_except = False
    try:
        js.call('gen_exception')
    except bond.RemoteException as e:
        print(e)
        got_except = True
    assert(got_except)
    assert(bond_repl_depth(js) == 1)

    # check stack depth after a remote serialization error
    js = JavaScript(timeout=1)
    js.export(gen_ser_err)
    got_except = False
    try:
        js.call('gen_ser_err')
    except bond.SerializationException as e:
        print(e)
        assert(e.side == "remote")
        got_except = True
    assert(got_except)
    assert(bond_repl_depth(js) == 1)


def test_buf_size():
    js = JavaScript(timeout=1)
    for size in [2 ** n for n in range(9, 16)]:
        print("testing buffer >= {} bytes".format(size))
        buf = "x" * size
        ret = js.call('String', buf)
        assert(ret == str(ret))
