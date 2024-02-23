
import unittest

from .. import json_normalizer


class TestJsonNormalizer(unittest.TestCase):
    def run_test(self, spec, data, expected):
        result = json_normalizer.normalize_data(spec, data)
        self.assertEqual(result, expected)

    def test_allow_single_item_with_none_is_none(self):
        spec = {
            "type": "list",
            "allow_single_item": True,
        }
        data = None
        expected = None

        self.assertEqual(json_normalizer.normalize_data(spec, data), expected)

    def test_none_value_does_not_collapse(self):
        spec = {
            "type": "dict",
            "keys": {
                "a": {
                    "type": "list",
                },
            },
        }
        data = { "a": None }
        expected = { "a": None }

        self.assertEqual(json_normalizer.normalize_data(spec, data), expected)

    def test_none_value_does_not_collapse_with_single_item(self):
        spec = {
            "type": "dict",
            "keys": {
                "a": {
                    "type": "list",
                    "allow_single_item": True,
                },
            },
        }
        data = { "a": None }
        expected = { "a": None }

        self.assertEqual(json_normalizer.normalize_data(spec, data), expected)


    def test_all(self):
        self.run_test({"type": "dict", "default_key": "d", "keys": {} }, "test", { "d": "test" } )
        self.run_test({"type": "dict", "keys": { "d": { "type": "str", "default_value": "dv", "required": True }} }, {}, { "d": "dv" } )
        self.run_test({"type": "dict", "default_key": "d", "keys": { "d": { "type": "str", "required": True }} }, "dv", { "d": "dv" } )
        self.run_test({"type": "dict", "default_key": "d", "default_value": {}, "keys": { "d": { "type": "str", "default_value": "dv", "required": True }} }, None, { "d": "dv" } )


        self.run_test({"type": "list", "allow_single_item": True }, 1, [1])
        self.run_test({"type": "list", "default_value": [] }, None, [])

        self.run_test({"type": "list", "allow_single_item": True, "default_value": [] }, None, [])

        self.run_test({"type":"dict", "default_key": "a", "keys": { "a": { "type": "dict", "keys": { "b": { "type": "dict", "required": True } } } } }, {}, {})

        self.run_test({
            "type": "dict",
            "keys": {
                "input": {
                    "type": "dict",
                    "default_key": "type",
                    "keys": {
                        "type": {
                            "type": "str",
                            "required": True,
                        },
                    },
                },
            }
        }, {}, {})


        # below is a complex test.
        basic_spec = {
            "type": "dict",
            "keys": {
                "no_match": {
                    "type": "list",
                },
                "default_val": {
                    "type": "bool",
                    "default_value": True,
                    "required": True,
                },
                "insert_lst": {
                    "type": "list",
                    "allow_single_item": True,
                },
                "insert_dict": {
                    "type": "dict",
                    "default_key": "key",
                },
                "insert_dict_default": {
                    "type": "dict",
                    "default_key": "key",
                },
                "dict_default": {
                    "type": "dict",
                    "default_key": "key",
                },
            }
        }
        spec = {
            "type": "dict",
            "default_key": "some",
            "keys": {
                **basic_spec["keys"],
                "dict_nested": basic_spec,
                "array": {
                    "type": "list",
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

