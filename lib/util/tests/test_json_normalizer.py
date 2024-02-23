
import unittest

from ..json_normalizer import normalize_data, ValidationError


class TestJsonNormalizer(unittest.TestCase):
    def run_test(self, spec, data, expected):
        result = normalize_data(spec, data)
        self.assertEqual(result, expected)

    def test_allow_single_item_with_none_is_none(self):
        spec = {
            "allow_single_item": True,
        }
        data = None
        expected = None

        self.assertEqual(normalize_data(spec, data), expected)

    def test_none_value_does_not_collapse(self):
        spec = {
            "keys": {
                "a": {
                },
            },
        }
        data = { "a": None }
        expected = { "a": None }

        self.assertEqual(normalize_data(spec, data), expected)


    def test_none_value_does_not_collapse_with_single_item(self):
        spec = {
            "keys": {
                "a": {
                    "allow_single_item": True,
                },
            },
        }
        data = { "a": None }
        expected = { "a": None }

        self.assertEqual(normalize_data(spec, data), expected)


    def test_dict_default_key(self):
        spec = {
            "default_key": "d", 
            "keys": {} 
        }
        data = "test"
        expected = { "d": "test" }
        self.assertEqual(normalize_data(spec, data), expected)


    def test_dict_override_default_value(self):
        spec = {
            "keys": {
                "d": { "default_value": "dv", "required": True }
            }
        }
        data = { "d": "a"}
        expected = { "d": "a" }
        self.assertEqual(normalize_data(spec, data), expected)

    def test_dict_default_value(self):
        spec = {
            "keys": {
                "d": { "default_value": "dv", "required": True }
            }
        }
        data = {}
        expected = { "d": "dv" }
        self.assertEqual(normalize_data(spec, data), expected)



    def test_dict_default_key_default_value(self):
        spec = {
            "default_key": "d",
            "default_value": "v",
            "keys": {}
        }
        data = None
        expected = { "d": "v" }
        self.assertEqual(normalize_data(spec, data), expected)


    def test_list_allow_single_item(self):
        spec = { "allow_single_item": True }
        data = 1
        expected = [1]
        self.assertEqual(normalize_data(spec, data), expected)

    def test_list_default_value(self):
        spec = { "default_value": [] }
        data = None
        expected = []
        self.assertEqual(normalize_data(spec, data), expected)


    def test_list_default_value_single_item(self):
        spec = { "default_value": [], "allow_single_item": True }
        data = None
        expected = []
        self.assertEqual(normalize_data(spec, data), expected)

    def test_list_processes_items(self):
        spec = { 
            "items": {
                "type": "int"
            }
        }
        data = [1,2,3]
        expected = [1,2,3]
        self.assertEqual(normalize_data(spec, data), expected)

        data = ["a", "b", "c"]
        self.assertRaises(ValidationError, normalize_data, spec, data)


    def nested_default_keys_and_values(self):
        spec = {
            "default_key": "d",
            "default_value": {},
            "keys": {
                "i": {
                    "default_value": "hello",
                },
            },
        }
        data = None
        expected = { "d": { "i": "hello" } }
        self.assertEqual(normalize_data(spec, data), expected)

    def test_typecheck(self):
        self.assertEqual(normalize_data({ "type": "str" }, "hello"), "hello")
        self.assertEqual(normalize_data({ "type": "int" }, 0), 0)
        self.assertEqual(normalize_data({ "type": "dict" }, {}), {})
        self.assertEqual(normalize_data({ "type": "list" }, []), [])

        self.assertRaises(ValidationError, normalize_data, { "type": "int" }, "hello")
        self.assertRaises(ValidationError, normalize_data, { "type": "str" }, 0)
        self.assertRaises(ValidationError, normalize_data, { "type": "list" }, {})
        self.assertRaises(ValidationError, normalize_data, { "type": "dict" }, [])

    def test_required(self):
        self.assertEqual(normalize_data({ "required": True }, "hello"), "hello")

        self.assertRaises(ValidationError, normalize_data, { "required": True }, None)

        spec = {
            "keys": {
                "a": { "required": True }
             }
        }
        self.assertRaises(ValidationError, normalize_data, spec, {})
        self.assertEqual(normalize_data(spec, { "a": 0 }), { "a": 0 })

    def test_parse(self):
        spec = {
            "type": "list",
            "items": {
                "type": "dict",
                "default_key": "cmd",
                "keys": {
                    "cmd": {
                        "type": "str",
                        "required": True,
                    },
                    "args": {
                        "type": "list",
                        "allow_single_item": True,
                        "default_value": [],
                        "required": True,
                    },
                },
            },
        }

        data = [ { "cmd": "a", "args": ["A", 1] } ]
        expected = [ { "cmd": "a", "args": ["A", 1] } ]
        self.assertEqual(normalize_data(spec, data), expected)


    def test_complex(self):
        self.run_test({ "default_key": "d", "keys": { "d": { "required": True }} }, "dv", { "d": "dv" } )
        self.run_test({ "default_key": "a", "keys": { "a": { "keys": { "b": { "required": True } } } } }, {}, {})

        self.run_test({
            "keys": {
                "input": {
                    "default_key": "type",
                    "keys": {
                        "type": {
                            "required": True,
                        },
                    },
                },
            }
        }, {}, {})


        # below is a complex test.
        basic_spec = {
            "keys": {
                "no_match": {
                },
                "default_val": {
                    "default_value": True,
                    "required": True,
                },
                "insert_lst": {
                    "allow_single_item": True,
                },
                "insert_dict": {
                    "default_key": "key",
                },
                "insert_dict_default": {
                    "default_key": "key",
                },
                "dict_default": {
                    "default_key": "key",
                },
            }
        }
        spec = {
            "default_key": "some",
            "keys": {
                **basic_spec["keys"],
                "dict_nested": basic_spec,
                "array": {
                    "items": basic_spec
                }
            }
        }
        basic_data = {
            "nochange": 1,
            "none": None,
            "insert_lst": "ins",
            "insert_dict": "val", # key: key
            "insert_dict_default": "val", # key: key
            "dict_default": {
                "key": "value",
                "default": False,
            },
        }

        data = {
            **basic_data,
            "dict_nested": {
                **basic_data,
            },
            "array": [
                basic_data,
                basic_data,
            ],
        }

        expected = {"nochange": 1, "none": None, "insert_lst": ["ins"], "insert_dict": {"key": "val"}, "insert_dict_default": {"key": "val"}, "dict_default": {"key": "value", "default": False}, "dict_nested": {"nochange": 1, "none": None, "insert_lst": ["ins"], "insert_dict": {"key": "val"}, "insert_dict_default": {"key": "val"}, "dict_default": {"key": "value", "default": False}, "default_val": True}, "array": [{"nochange": 1, "none": None, "insert_lst": ["ins"], "insert_dict": {"key": "val"}, "insert_dict_default": {"key": "val"}, "dict_default": {"key": "value", "default": False}, "default_val": True}, {"nochange": 1, "none": None, "insert_lst": ["ins"], "insert_dict": {"key": "val"}, "insert_dict_default": {"key": "val"}, "dict_default": {"key": "value", "default": False}, "default_val": True}], "default_val": True}

        self.run_test(spec, data, expected)

