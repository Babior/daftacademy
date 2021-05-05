import string
import types


# Task 2.1
def greetings(greet):
    def inner(name: str):
        return f'Hello {greet(name).title()}'

    return inner


# Task 2.2
def is_palindrome(show_sentence):
    def inner(line: str):
        """
        :param func:
        :return:
        """
        s = str(show_sentence(line))
        s1 = s.translate({ord(c): None for c in string.whitespace}).translate(
            {ord(c): None for c in string.punctuation}).lower()
        rev = ''.join(reversed(s1))
        if s1 == rev:
            return f'{s} - is palindrome'
        return f'{s} - is not palindrome'

    return inner


# Task 2.3
def format_output(*args):
    def real_decorator(func):
        """
        Decorator to find keys in not formatted string
        :param func: dict keys
        :return: dict item (key-value)
        """

        def wrapper(*arg):
            tmp = func(*arg)
            tmp_val = ""
            result_dict = {}
            for arg in args:
                if arg in tmp:
                    result_dict[arg] = tmp.get(arg)
                elif "__" in arg:
                    tmp_keys = arg.split("__")
                    for i in tmp_keys:
                        if i in tmp:
                            tmp_val += f"{tmp[i]} "
                        else:
                            raise ValueError()
                    result_dict[arg] = tmp_val.rstrip()
                else:
                    raise ValueError()
            return result_dict

        return wrapper

    return real_decorator


# Task 2.4
def add_class_method(cls):
    def wrapper(fn):
        setattr(cls, fn.__name__, fn)
        return fn

    return wrapper


def add_instance_method(cls):
    def wrapper(fn):
        self_fn = lambda self: fn()
        setattr(cls, fn.__name__, self_fn)
        return fn

    return wrapper


# Testing 2.4
def test_add_class_method():
    class A:
        pass

    @add_class_method(A)
    def foo():
        return "Hello!"

    assert A.foo() == "Hello!"


def test_add_instance_method():
    class A:
        pass

    @add_instance_method(A)
    def bar():
        return "Hello again!"

    assert A().bar() == "Hello again!"


def test_methods_issues():
    class Dummy:
        def method(self):
            return "instance method called"

        @classmethod
        def classmethod(cls):
            return "class method called"

        @staticmethod
        def staticmethod():
            return "static method called"

    @add_class_method(Dummy)
    def foo():
        return "Hello!"

    @add_instance_method(Dummy)
    def bar():
        return "Hello again!"

    assert Dummy().bar() == "Hello again!"
    assert Dummy.foo() == "Hello!"


test_add_class_method()
test_add_instance_method()
test_methods_issues()
