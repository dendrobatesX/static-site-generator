import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):

    def test_props_to_html_multiple(self):
        node = HTMLNode(
            tag="a",
            props={
                "href": "https://www.google.com",
                "target": "_blank"
            }
        )
        result = node.props_to_html()
        expected = ' href="https://www.google.com" target="_blank"'
        self.assertEqual(result, expected)

    def test_props_to_html_single(self):
        node = HTMLNode(
            tag="p",
            props={"class": "text"}
        )
        result = node.props_to_html()
        expected = ' class="text"'
        self.assertEqual(result, expected)

    def test_props_to_html_empty(self):
        node = HTMLNode(tag="div", props=None)
        result = node.props_to_html()
        expected = ""
        self.assertEqual(result, expected)

class TestLeafNode(unittest.TestCase):

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_with_props(self):
        node = LeafNode(
            "a",
            "Google",
            {"href": "https://google.com", "target": "_blank"}
        )
        expected = '<a href="https://google.com" target="_blank">Google</a>'
        self.assertEqual(node.to_html(), expected)

    def test_leaf_no_tag(self):
        node = LeafNode(None, "Just text")
        self.assertEqual(node.to_html(), "Just text")

    def test_leaf_no_value_raises(self):
        node = LeafNode("p", None)
        with self.assertRaises(ValueError):
            node.to_html()
class TestParentNode(unittest.TestCase):

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
    )
    def test_single_child(self):
        child = LeafNode("span", "child")
        parent = ParentNode("div", [child])
        self.assertEqual(parent.to_html(), "<div><span>child</span></div>")

    def test_multiple_children(self):
        children = [
            LeafNode("p", "one"),
            LeafNode("p", "two"),
        ]
        parent = ParentNode("div", children)
        self.assertEqual(
            parent.to_html(),
            "<div><p>one</p><p>two</p></div>"
        )

    def test_nested_parent(self):
        child = ParentNode("span", [
            LeafNode("b", "bold")
        ])
        parent = ParentNode("div", [child])
        self.assertEqual(
            parent.to_html(),
            "<div><span><b>bold</b></span></div>"
        )

    def test_deeply_nested_structure(self):
        node = ParentNode("div", [
            ParentNode("ul", [
                ParentNode("li", [
                    LeafNode("span", "item")
                ])
            ])
        ])
        self.assertEqual(
            node.to_html(),
            "<div><ul><li><span>item</span></li></ul></div>"
        )

    def test_parent_with_props(self):
        parent = ParentNode(
            "div",
            [LeafNode("p", "text")],
            {"class": "container"}
        )
        self.assertEqual(
            parent.to_html(),
            '<div class="container"><p>text</p></div>'
        )

    def test_empty_children_list(self):
        parent = ParentNode("div", [])
        self.assertEqual(parent.to_html(), "<div></div>")

    def test_missing_tag_raises(self):
        parent = ParentNode(None, [LeafNode("p", "text")])
        with self.assertRaises(ValueError):
            parent.to_html()

    def test_missing_children_raises(self):
        parent = ParentNode("div", None)
        with self.assertRaises(ValueError):
            parent.to_html()
if __name__ == "__main__":
    unittest.main()