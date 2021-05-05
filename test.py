import unittest

from main import greetings, is_palindrome, format_output, add_class_method, add_instance_method


class ExampleTest(unittest.TestCase):
    @greetings
    def show_greetings(self):
        return "joe doe"

    def test_result(self):
        self.assertEqual(self.show_greetings(), "Hello Joe Doe")

    @is_palindrome
    def show_sentence(self):
        return "annA"

    def test_result(self):
        self.assertEqual(self.show_sentence(), "annA - is palindrome")

    @format_output("first_name")
    def show_dict(self):
        return {
            "first_name": "Jan",
            "last_name": "Kowalski",
        }

    def test_result(self):
        self.assertEqual(self.show_dict(), {"first_name": "Jan"})


if __name__ == "__main__":
    unittest.main()
