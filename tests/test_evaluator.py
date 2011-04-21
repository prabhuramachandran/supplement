from supplement.evaluator import infer
from supplement.scope import StaticScope

from .helpers import pytest_funcarg__project

def pytest_funcarg__scope(request):
    project = pytest_funcarg__project(request)
    return StaticScope('test', project)

def test_string(scope):
    obj = infer("'str'", scope)
    assert 'lower' in obj

def test_dict(scope):
    obj = infer("{}", scope)
    assert 'keys' in obj

def test_list(scope):
    obj = infer("[]", scope)
    assert 'append' in obj

def test_tuple(scope):
    obj = infer("5, 'sss'", scope)
    assert 'append' not in obj
    assert 'index' in obj

def test_number(scope):
    obj = infer("100.5", scope)
    assert 'real' in obj

def test_instance_of_builtin_class(scope):
    obj = infer("set()", scope)
    assert 'add' in obj

    obj = infer("dict()", scope)
    assert 'keys' in obj

def test_eval_of_assigned_name(project):
    scope = project.create_scope("""
        d = dict()
    """)

    obj = infer('d', scope)
    assert 'iterkeys' in obj
    assert 'Class' not in obj.get_object().__class__.__name__

def test_eval_of_multi_assigned_name_from_tuple(project):
    scope = project.create_scope("""
        d, l = {}, []
    """)

    obj = infer('d', scope)
    assert 'iterkeys' in obj

    obj = infer('l', scope)
    assert 'append' in obj

def test_eval_of_multi_assigned_name_from_list(project):
    scope = project.create_scope("""
        d, l = [{}, []]
    """)

    obj = infer('d', scope)
    assert 'iterkeys' in obj

    obj = infer('l', scope)
    assert 'append' in obj

def test_eval_of_multi_assigned_name_from_imported_seq(project):
    project.create_module('toimport', '''
        value = [{}, []]
    ''')

    scope = project.create_scope('''
        import toimport
        d, l = toimport.value
    ''')

    obj = infer('d', scope)
    assert 'iterkeys' in obj

    obj = infer('l', scope)
    assert 'append' in obj

def test_eval_of_seq_item_get(project):
    scope = project.create_scope('''
        seq_value = [{}, []]
        d = seq_value[0]
        l = seq_value[1]
    ''')

    obj = infer('d', scope)
    assert 'iterkeys' in obj

    obj = infer('l', scope)
    assert 'append' in obj

def test_eval_of_dict_item_get(project):
    scope = project.create_scope('''
        dict_value = {'aaa':{}, 2:[]}
        d = dict_value['aaa']
        l = dict_value[2]
    ''')

    obj = infer('d', scope)
    assert 'iterkeys' in obj

    obj = infer('l', scope)
    assert 'append' in obj

def test_eval_of_function_call_without_arguments(project):
    scope = project.create_scope('''
        def func():
            return []
    ''')

    obj = infer('func()', scope)
    assert 'append' in obj

def test_eval_of_function_call_with_arguments(project):
    scope = project.create_scope('''
        def func(arg):
            return arg
    ''')

    obj = infer('func([])', scope)
    assert 'append' in obj

def test_eval_of_recursive_function_call(project):
    scope = project.create_scope('''
        def func():
            return func()
            return []
    ''')

    obj = infer('func()', scope)
    assert 'append' in obj

def test_eval_of_ping_pong_call(project):
    scope = project.create_scope('''
        def ping():
            return pong()
            return []

        def pong():
            return ping()
    ''')

    obj = infer('ping()', scope)
    assert 'append' in obj