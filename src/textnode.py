from enum import Enum
from htmlnode import HTMLNode, LeafNode, ParentNode
import re
class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class BlockType(Enum):
    PARAGRAPH= "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"




class TextNode():
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url   

    def __eq__(self, other):
        if self.text==other.text and self.text_type==other.text_type and self.url==other.url:
            return True
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"

def text_node_to_html_node(text_node):
    if text_node.text_type not in TextType:
        raise Exception("Invalid TextType")

    match text_node.text_type:       
        case TextType.TEXT:
            return LeafNode(None, text_node.text)

        case TextType.BOLD:
            return LeafNode("b", text_node.text)

        case TextType.ITALIC:
            return LeafNode("i", text_node.text)

        case TextType.CODE:
            return LeafNode("code", text_node.text)

        case TextType.LINK:
            return LeafNode(
                "a",
                text_node.text,
                {"href": text_node.url}
            )

        case TextType.IMAGE:
            return LeafNode(
                "img",
                "",
                {
                    "src": text_node.url,
                    "alt": text_node.text
                }
            )

        case _:
            raise Exception("Unhandled TextType")

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes=[]
    
    for node in old_nodes:        
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        parts = node.text.split(delimiter)
       
        if len(parts) == 1:
            new_nodes.append(node)
            continue
       
        if len(parts) % 2 == 0:
            raise Exception(f"Invalid Markdown: unmatched delimiter '{delimiter}'")
        
        for i, part in enumerate(parts):
            if part == "":
                continue

            if i % 2 == 0:
                new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(part, text_type))

    return new_nodes

def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)

def split_nodes_image(old_nodes):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        images = extract_markdown_images(text)
      
        if not images:
            new_nodes.append(node)
            continue

        for alt, url in images:
            image_markdown = f"![{alt}]({url})"

            before, after = text.split(image_markdown, 1)

          
            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))

            new_nodes.append(TextNode(alt, TextType.IMAGE, url))

            text = after

        if text:
            new_nodes.append(TextNode(text, TextType.TEXT))

    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue

        text = node.text
        links = extract_markdown_links(text)

       
        if not links:
            new_nodes.append(node)
            continue

        for anchor, url in links:
            link_markdown = f"[{anchor}]({url})"

            before, after = text.split(link_markdown, 1)

           
            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))

           
            new_nodes.append(TextNode(anchor, TextType.LINK, url))

            
            text = after

       
        if text:
            new_nodes.append(TextNode(text, TextType.TEXT))

    return new_nodes

def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]

    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)

    return nodes

def markdown_to_blocks(markdown):
    marklist = markdown.split("\n\n")
    return [block.strip() for block in marklist]

def block_to_block_type(block):
    if any(block.startswith("#" * i + " ") for i in range(1, 7)):
        return BlockType.HEADING
    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE
    if block.startswith("> ") or block.startswith(">"):
        return BlockType.QUOTE
    if block.startswith("- "):
        return BlockType.UNORDERED_LIST
    if re.match(r"^\d+\.\s", block):
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH

def markdown_to_html_node(markdown):
    blocks=markdown_to_blocks(markdown)
    children=[]
    for block in blocks:
        if not block:
            continue
        block_type=block_to_block_type(block)

        if block_type == BlockType.PARAGRAPH:
            paragraph = " ".join(block.split())
            text_nodes = text_to_textnodes(paragraph)
            html_children = [text_node_to_html_node(n) for n in text_nodes]
            children.append(ParentNode("p", html_children))

        elif block_type == BlockType.HEADING:
            level = block.count("#", 0, block.find(" "))
            text = block[level + 1:]
            paragraph = " ".join(text.split())
            text_nodes = text_to_textnodes(paragraph)
            html_children = [text_node_to_html_node(n) for n in text_nodes]
            children.append(ParentNode(f"h{level}", html_children))

        elif block_type == BlockType.CODE:
            lines = block.split("\n")

            code_lines = lines[1:-1]

            code_lines = [line.lstrip() for line in code_lines]

            code_text = "\n".join(code_lines) + "\n"

            children.append(
                ParentNode("pre", [
                    LeafNode("code", code_text)
                ])
            )

        elif block_type == BlockType.QUOTE:
            text = block.lstrip("> ").strip()
            paragraph = " ".join(text.split())
            text_nodes = text_to_textnodes(paragraph)
            html_children = [text_node_to_html_node(n) for n in text_nodes]
            children.append(ParentNode("blockquote", html_children))

        elif block_type == BlockType.UNORDERED_LIST:
            items = block.split("\n")
            li_nodes = []
            for item in items:
                text = item[2:]  
                paragraph = " ".join(text.split())
                text_nodes = text_to_textnodes(paragraph)
                html_children = [text_node_to_html_node(n) for n in text_nodes]
                li_nodes.append(ParentNode("li", html_children))
            children.append(ParentNode("ul", li_nodes))

        elif block_type == BlockType.ORDERED_LIST:
            items = block.split("\n")
            li_nodes = []
            for item in items:
                # remove "1. ", "2. ", etc.
                text = item.split(". ", 1)[1]
                paragraph = " ".join(text.split())
                text_nodes = text_to_textnodes(paragraph)
                html_children = [text_node_to_html_node(n) for n in text_nodes]
                li_nodes.append(ParentNode("li", html_children))
            children.append(ParentNode("ol", li_nodes))

    return ParentNode("div", children)

def extract_title(markdown):
    lines = markdown.split("\n")

    for line in lines:
        line = line.strip()
       
        if line.startswith("# ") and not line.startswith("##"):
            return line[2:].strip()

    raise Exception("No h1 header found")

