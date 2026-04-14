import unittest

from textnode import (TextNode, TextType, text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, 
                        extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes,
                        markdown_to_blocks, block_to_block_type, BlockType, markdown_to_html_node,
                        extract_title)

from htmlnode import HTMLNode, LeafNode, ParentNode


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
        

    def test_neq(self):
        node = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_eq1(self):
        node = TextNode("This is a text node", TextType.BOLD, "http//")
        node2 = TextNode("This is a text node", TextType.BOLD, "http//")
        self.assertEqual(node, node2)

    def test_neq1(self):
        node = TextNode("This is a text", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

           
class TestTextNodeToHTML(unittest.TestCase):

    def test_text(self):
        node = TextNode("hello", TextType.TEXT)
        html = text_node_to_html_node(node)
        self.assertEqual(html.tag, None)
        self.assertEqual(html.value, "hello")

    def test_bold(self):
        node = TextNode("bold text", TextType.BOLD)
        html = text_node_to_html_node(node)
        self.assertEqual(html.tag, "b")
        self.assertEqual(html.value, "bold text")

    def test_italic(self):
        node = TextNode("italic text", TextType.ITALIC)
        html = text_node_to_html_node(node)
        self.assertEqual(html.tag, "i")
        self.assertEqual(html.value, "italic text")

    def test_code(self):
        node = TextNode("print('hi')", TextType.CODE)
        html = text_node_to_html_node(node)
        self.assertEqual(html.tag, "code")
        self.assertEqual(html.value, "print('hi')")

    def test_link(self):
        node = TextNode("Google", TextType.LINK, "https://google.com")
        html = text_node_to_html_node(node)
        self.assertEqual(html.tag, "a")
        self.assertEqual(html.value, "Google")
        self.assertEqual(html.props, {"href": "https://google.com"})

    def test_image(self):
        node = TextNode("alt text", TextType.IMAGE, "image.png")
        html = text_node_to_html_node(node)
        self.assertEqual(html.tag, "img")
        self.assertEqual(html.value, "")
        self.assertEqual(
            html.props,
            {"src": "image.png", "alt": "alt text"}
        )

    def test_invalid_type_raises(self):
        class FakeType:
            pass

        node = TextNode("oops", FakeType())
        with self.assertRaises(Exception):
            text_node_to_html_node(node)

class TestSplitNodesDelimiter(unittest.TestCase):

    def test_code_split(self):
        node = TextNode("This is `code` text", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[1].text, "code")
        self.assertEqual(result[1].text_type, TextType.CODE)

    def test_bold_split(self):
        node = TextNode("This is **bold** text", TextType.TEXT)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)

        self.assertEqual(result[1].text, "bold")
        self.assertEqual(result[1].text_type, TextType.BOLD)

    def test_italic_split(self):
        node = TextNode("This is _italic_ text", TextType.TEXT)
        result = split_nodes_delimiter([node], "_", TextType.ITALIC)

        self.assertEqual(result[1].text, "italic")
        self.assertEqual(result[1].text_type, TextType.ITALIC)

    def test_multiple_splits(self):
        node = TextNode("`a` and `b`", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text, "a")
        self.assertEqual(result[0].text_type, TextType.CODE)

    def test_no_delimiter(self):
        node = TextNode("just text", TextType.TEXT)
        result = split_nodes_delimiter([node], "`", TextType.CODE)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "just text")

    def test_unmatched_delimiter_raises(self):
        node = TextNode("This is `broken text", TextType.TEXT)

        with self.assertRaises(Exception):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_non_text_nodes_unchanged(self):
        node = TextNode("bold", TextType.BOLD)
        result = split_nodes_delimiter([node], "`", TextType.CODE)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text_type, TextType.BOLD)

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)
    
    def test_extract_images(self):
        text = "![alt](img.png)"
        result = extract_markdown_images(text)
        self.assertEqual(result, [("alt", "img.png")])

    def test_extract_links(self):
        text = "[Google](https://google.com)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [("Google", "https://google.com")])

    def test_extract_multiple(self):
        text = "![a](1.png) and ![b](2.png)"
        result = extract_markdown_images(text)
        self.assertEqual(result, [("a", "1.png"), ("b", "2.png")])

    def test_links_ignore_images(self):
        text = "![img](a.png) and [link](b.com)"
        result = extract_markdown_links(text)
        self.assertEqual(result, [("link", "b.com")])
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
    def test_single_link(self):
        node = TextNode("Go to [Google](https://google.com)", TextType.TEXT)
        result = split_nodes_link([node])

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].text, "Go to ")
        self.assertEqual(result[1].text_type, TextType.LINK)
        self.assertEqual(result[1].url, "https://google.com")

    def test_multiple_links(self):
        node = TextNode("[A](a.com) and [B](b.com)", TextType.TEXT)
        result = split_nodes_link([node])

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text_type, TextType.LINK)
        self.assertEqual(result[1].text_type, TextType.TEXT)
        self.assertEqual(result[2].text_type, TextType.LINK)

    def test_no_links(self):
        node = TextNode("just text", TextType.TEXT)
        result = split_nodes_link([node])

        self.assertEqual(len(result), 1)

    def test_non_text_node(self):
        node = TextNode("bold", TextType.BOLD)
        result = split_nodes_link([node])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text_type, TextType.BOLD)

    def test_single_image(self):
        node = TextNode("Hello ![cat](cat.png) world", TextType.TEXT)
        result = split_nodes_image([node])

        self.assertEqual(len(result), 3)
        self.assertEqual(result[1].text_type, TextType.IMAGE)
        self.assertEqual(result[1].text, "cat")
        self.assertEqual(result[1].url, "cat.png")

    def test_multiple_images(self):
        node = TextNode("![a](1.png) and ![b](2.png)", TextType.TEXT)
        result = split_nodes_image([node])

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].text_type, TextType.IMAGE)
        self.assertEqual(result[1].text_type, TextType.TEXT)
        self.assertEqual(result[2].text_type, TextType.IMAGE)

    def test_no_images(self):
        node = TextNode("just text", TextType.TEXT)
        result = split_nodes_image([node])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, "just text")

    def test_non_text_node(self):
        node = TextNode("bold", TextType.BOLD)
        result = split_nodes_image([node])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text_type, TextType.BOLD)     



class TestTextToTextNodes(unittest.TestCase):

    def test_plain_text(self):
        text = "just plain text"
        nodes = text_to_textnodes(text)

        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].text_type, TextType.TEXT)
        self.assertEqual(nodes[0].text, text)

    def test_bold(self):
        text = "This is **bold** text"
        nodes = text_to_textnodes(text)

        self.assertEqual(nodes[1].text_type, TextType.BOLD)
        self.assertEqual(nodes[1].text, "bold")

    def test_italic(self):
        text = "This is _italic_ text"
        nodes = text_to_textnodes(text)

        self.assertEqual(nodes[1].text_type, TextType.ITALIC)
        self.assertEqual(nodes[1].text, "italic")

    def test_code(self):
        text = "This is `code` text"
        nodes = text_to_textnodes(text)

        self.assertEqual(nodes[1].text_type, TextType.CODE)
        self.assertEqual(nodes[1].text, "code")

    def test_link(self):
        text = "Go to [Google](https://google.com)"
        nodes = text_to_textnodes(text)

        self.assertEqual(nodes[1].text_type, TextType.LINK)
        self.assertEqual(nodes[1].text, "Google")
        self.assertEqual(nodes[1].url, "https://google.com")

    def test_image(self):
        text = "Look ![cat](cat.png)"
        nodes = text_to_textnodes(text)

        self.assertEqual(nodes[1].text_type, TextType.IMAGE)
        self.assertEqual(nodes[1].text, "cat")
        self.assertEqual(nodes[1].url, "cat.png")

    def test_mixed_formatting(self):
        text = "Text **bold** and _italic_"
        nodes = text_to_textnodes(text)

        self.assertEqual(nodes[1].text_type, TextType.BOLD)
        self.assertEqual(nodes[3].text_type, TextType.ITALIC)

    def test_all_types(self):
        text = "Text **bold** _italic_ `code` [link](url)"
        nodes = text_to_textnodes(text)

        types = [n.text_type for n in nodes]

        self.assertIn(TextType.BOLD, types)
        self.assertIn(TextType.ITALIC, types)
        self.assertIn(TextType.CODE, types)
        self.assertIn(TextType.LINK, types)

    def test_multiple_same_type(self):
        text = "**one** and **two**"
        nodes = text_to_textnodes(text)

        bold_nodes = [n for n in nodes if n.text_type == TextType.BOLD]

        self.assertEqual(len(bold_nodes), 2)
        self.assertEqual(bold_nodes[0].text, "one")
        self.assertEqual(bold_nodes[1].text, "two")

    def test_formatting_at_start(self):
        text = "**bold** text"
        nodes = text_to_textnodes(text)

        self.assertEqual(nodes[0].text_type, TextType.BOLD)
        self.assertEqual(nodes[1].text, " text")

    def test_image_and_link(self):
        text = "![img](a.png) and [link](b.com)"
        nodes = text_to_textnodes(text)

        self.assertEqual(nodes[0].text_type, TextType.IMAGE)
        self.assertEqual(nodes[2].text_type, TextType.LINK)

class Testmarkdowntoblocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

   

    def test_single_block(self):
        md = "This is a paragraph"
        result = markdown_to_blocks(md)

        self.assertEqual(result, ["This is a paragraph"])

    def test_multiple_blocks(self):
        md = "First block\n\nSecond block\n\nThird block"
        result = markdown_to_blocks(md)

        self.assertEqual(result, [
            "First block",
            "Second block",
            "Third block"
        ])

    def test_strips_whitespace(self):
        md = "  First block  \n\n   Second block   "
        result = markdown_to_blocks(md)

        self.assertEqual(result, [
            "First block",
            "Second block"
        ])

    def test_empty_string(self):
        md = ""
        result = markdown_to_blocks(md)

        self.assertEqual(result, [""])

    def test_extra_newlines(self):
        md = "Block one\n\n\n\nBlock two"
        result = markdown_to_blocks(md)

        self.assertEqual(result, [
            "Block one",
            "",
            "Block two"
        ])

    def test_only_newlines(self):
        md = "\n\n"
        result = markdown_to_blocks(md)

        self.assertEqual(result, ["", ""])

    def test_mixed_content(self):
        md = "Line 1\nLine 2\n\nLine 3"
        result = markdown_to_blocks(md)

        self.assertEqual(result, [
            "Line 1\nLine 2",
            "Line 3"
        ])
class TestBlocktoblock(unittest.TestCase):
    def test_heading(self):
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)

    def test_code(self):
        block = "```\ncode\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_quote(self):
        self.assertEqual(block_to_block_type("> quote"), BlockType.QUOTE)

    def test_unordered_list(self):
        self.assertEqual(block_to_block_type("- item"), BlockType.UNORDERED_LIST)

    def test_ordered_list(self):
        self.assertEqual(block_to_block_type("1. item"), BlockType.ORDERED_LIST)

    def test_paragraph(self):
        self.assertEqual(block_to_block_type("just text"), BlockType.PARAGRAPH) 

    def test_paragraphs(self):
        md = """
    This is **bolded** paragraph
    text in a p
    tag here

    This is another paragraph with _italic_ text and `code` here

    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
    ```
    This is text that _should_ remain
    the **same** even with inline stuff
    ```
    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )    

class TestMarkdownToHTMLNode(unittest.TestCase):

    def test_empty_string(self):
        md = ""
        node = markdown_to_html_node(md)
        html = node.to_html()

        self.assertEqual(html, "<div></div>")

    def test_only_newlines(self):
        md = "\n\n"
        node = markdown_to_html_node(md)
        html = node.to_html()

        self.assertEqual(html, "<div></div>")

    def test_ignores_empty_blocks_between(self):
        md = "First paragraph\n\n\n\nSecond paragraph"
        node = markdown_to_html_node(md)
        html = node.to_html()

        self.assertEqual(
            html,
            "<div><p>First paragraph</p><p>Second paragraph</p></div>"
        )

    def test_leading_and_trailing_newlines(self):
        md = "\n\nFirst paragraph\n\nSecond paragraph\n\n"
        node = markdown_to_html_node(md)
        html = node.to_html()

        self.assertEqual(
            html,
            "<div><p>First paragraph</p><p>Second paragraph</p></div>"
        )

    def test_mixed_empty_and_content(self):
        md = "\n\nFirst\n\n\nSecond\n\n\n\nThird\n\n"
        node = markdown_to_html_node(md)
        html = node.to_html()

        self.assertEqual(
            html,
            "<div><p>First</p><p>Second</p><p>Third</p></div>"
        )
class TestExtractTitle(unittest.TestCase):

    def test_basic(self):
        md = "# Hello"
        self.assertEqual(extract_title(md), "Hello")

    def test_with_whitespace(self):
        md = "   # Hello World   "
        self.assertEqual(extract_title(md), "Hello World")

    def test_multiline(self):
        md = "Some text\n# Title Here\nMore text"
        self.assertEqual(extract_title(md), "Title Here")

    def test_ignores_h2(self):
        md = "## Not this\n# Correct Title"
        self.assertEqual(extract_title(md), "Correct Title")

    def test_no_h1_raises(self):
        md = "## Only h2 here"
        with self.assertRaises(Exception):
            extract_title(md)

    def test_multiple_h1_returns_first(self):
        md = "# First\n# Second"
        self.assertEqual(extract_title(md), "First")



if __name__ == "__main__":
    unittest.main()