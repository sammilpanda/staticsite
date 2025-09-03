import unittest

from textnode import *
from htmlnode import *
from funcs import *


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
    def test_not_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.TEXT)
        self.assertNotEqual(node, node2)
    def test_repr(self):
        node = TextNode("This is a text node", TextType.TEXT)
        self.assertNotEqual(repr(node), "TextNode(This is a text node, bold, None)")
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
    def test_split_nodes_delimiter(self):
        node = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is another text node", TextType.TEXT)
        nodes = [node, node2]
        new_nodes = split_nodes_delimiter(nodes, " ", TextType.TEXT)
        self.assertEqual(new_nodes[0], TextNode("This", TextType.TEXT))
        self.assertEqual(new_nodes[1], TextNode("is", TextType.TEXT))
        self.assertEqual(new_nodes[2], TextNode("a", TextType.TEXT))
        self.assertEqual(new_nodes[3], TextNode("text", TextType.TEXT))
        self.assertEqual(new_nodes[4], TextNode("node", TextType.TEXT))
    def test_split_nodes_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes[0], TextNode("This is text with a ", TextType.TEXT))
        self.assertEqual(new_nodes[1], TextNode("code block", TextType.CODE))
        self.assertEqual(new_nodes[2], TextNode(" word", TextType.TEXT))
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a [link](https://www.example.com)"
        )
        self.assertListEqual([("link", "https://www.example.com")], matches)

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
    
    def test_split_links(self):
        node = TextNode(
            "This is text with a [link](https://www.example.com) and another [second link](https://www.example.com/2)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.example.com"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second link", TextType.LINK, "https://www.example.com/2"),
            ],
            new_nodes,
        )
    
    def test_text_to_textnodes(self):
        text = "This is a **bold** text with an ![image](https://i.imgur.com/zjjcJKZ.png) and a [link](https://www.example.com)."
        nodes = text_to_textnodes(text)
        self.assertEqual(len(nodes), 7)
        self.assertEqual(nodes[0], TextNode("This is a ", TextType.TEXT))
        self.assertEqual(nodes[1], TextNode("bold", TextType.BOLD))
        self.assertEqual(nodes[2], TextNode(" text with an ", TextType.TEXT))
        self.assertEqual(nodes[3], TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"))
        self.assertEqual(nodes[4], TextNode(" and a ", TextType.TEXT))
        self.assertEqual(nodes[5], TextNode("link", TextType.LINK, "https://www.example.com"))
        self.assertEqual(nodes[6], TextNode(".", TextType.TEXT))
    
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
    
    def test_block_to_block_type(self):
        self.assertEqual(block_to_block_type("This is a paragraph."), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("# This is a heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("```python\nprint('Hello, World!')\n```"), BlockType.CODE)
        self.assertEqual(block_to_block_type("> This is a quote"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type("- This is an unordered list item"), BlockType.UNORDERED_LIST)
        self.assertEqual(block_to_block_type("1. This is an ordered list item"), BlockType.ORDERED_LIST)
    
if __name__ == "__main__":
    unittest.main()