from htmlnode import *
from textnode import *
from pathlib import Path

import re
import os

def text_node_to_html_node(text_node):
    """Convert a TextNode to an HTMLNode (LeafNode)."""
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    elif text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    elif text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    elif text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    elif text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    elif text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
    else:
        raise Exception(f"Unknown text type: {text_node.text_type}")
    
def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        parts = node.text.split(delimiter)
        if len(parts) % 2 == 0:
            raise ValueError(f"Invalid markdown, formatted section not closed")
        
        for i, part in enumerate(parts):
            if part == "":
                continue
            if i % 2 == 0:
                # Even indices are regular text
                new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                # Odd indices are the formatted text
                new_nodes.append(TextNode(part, text_type))
    
    return new_nodes

def extract_markdown_images(text):
    """Extract markdown images from text and return list of (alt_text, url) tuples."""
    pattern = r"!\[([^\[\]]*?)\]\(([^\(\)]*?)\)"
    matches = re.findall(pattern, text)
    return matches

def extract_markdown_links(text):
    """Extract markdown links from text and return list of (link_text, url) tuples."""
    pattern = r"\[([^\[\]]*?)\]\(([^\(\)]*?)\)"
    matches = re.findall(pattern, text)
    return matches

def split_nodes_image(old_nodes):
    """Split nodes that contain markdown images into separate TextNodes."""
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
        
        current_text = text
        for alt_text, url in images:
            # Find the full markdown pattern
            image_pattern = f"![{alt_text}]({url})"
            parts = current_text.split(image_pattern, 1)
            
            if len(parts) == 2:
                # Add text before the image (if any)
                if parts[0]:
                    new_nodes.append(TextNode(parts[0], TextType.TEXT))
                
                # Add the image node
                new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
                
                # Continue with remaining text
                current_text = parts[1]
        
        # Add any remaining text after the last image
        if current_text:
            new_nodes.append(TextNode(current_text, TextType.TEXT))
    
    return new_nodes
def split_nodes_link(old_nodes):
    """Split nodes that contain markdown links into separate TextNodes."""
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
        
        current_text = text
        for link_text, url in links:
            # Find the full markdown pattern
            link_pattern = f"[{link_text}]({url})"
            parts = current_text.split(link_pattern, 1)
            
            if len(parts) == 2:
                # Add text before the link (if any)
                if parts[0]:
                    new_nodes.append(TextNode(parts[0], TextType.TEXT))
                
                # Add the link node
                new_nodes.append(TextNode(link_text, TextType.LINK, url))
                
                # Continue with remaining text
                current_text = parts[1]
        
        # Add any remaining text after the last link
        if current_text:
            new_nodes.append(TextNode(current_text, TextType.TEXT))
    
    return new_nodes

def text_to_textnodes(text):
    """Convert raw markdown text to a list of TextNodes with all formatting applied."""
    # Start with a single TEXT node
    nodes = [TextNode(text, TextType.TEXT)]
    
    # Apply all the different formatting types in sequence
    # Order matters - images before links to avoid conflicts
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    
    return nodes

def markdown_to_blocks(markdown):
    """Convert raw markdown text to a list of blocks."""
    # Split the markdown by double newlines (empty lines)
    blocks = markdown.split("\n\n")
    
    # Clean up each block by stripping whitespace and filtering out empty blocks
    cleaned_blocks = []
    for block in blocks:
        # Strip whitespace from the entire block
        cleaned_block = block.strip()
        # Only add non-empty blocks
        if cleaned_block:
            cleaned_blocks.append(cleaned_block)
    
    return cleaned_blocks

def block_to_block_type(block):
    """Convert a markdown block to its corresponding BlockType."""
    if block.startswith("#"):
        return BlockType.HEADING
    elif block.startswith("```"):
        return BlockType.CODE
    elif block.startswith(">"):
        return BlockType.QUOTE
    elif block.startswith("- "):
        return BlockType.UNORDERED_LIST
    elif block[0].isdigit() and block[1] == ".":
        return BlockType.ORDERED_LIST
    else:
        return BlockType.PARAGRAPH

def text_to_children(text):
    """Convert text with inline markdown to a list of HTMLNode children."""
    # Convert text to TextNodes with all inline formatting
    text_nodes = text_to_textnodes(text)
    
    # Convert each TextNode to an HTMLNode
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    
    return children

def heading_to_html_node(block):
    """Convert a heading block to an HTMLNode."""
    # Count the number of # characters
    level = 0
    for char in block:
        if char == '#':
            level += 1
        else:
            break
    
    if level < 1 or level > 6:
        raise ValueError(f"Invalid heading level: {level}")
    
    # Extract text after the # characters and space
    text = block[level:].strip()
    
    # Create children from the heading text
    children = text_to_children(text)
    
    return ParentNode(f"h{level}", children)

def paragraph_to_html_node(block):
    """Convert a paragraph block to an HTMLNode."""
    # Replace newlines with spaces and normalize whitespace
    text = block.replace('\n', ' ')
    # Replace multiple consecutive spaces with single space
    text = ' '.join(text.split())
    children = text_to_children(text)
    return ParentNode("p", children)

def code_to_html_node(block):
    """Convert a code block to an HTMLNode."""
    # Remove the ``` markers from start and end
    code_text = block[3:-3]
    
    # For code blocks, we don't parse inline markdown
    # Just create a plain text node
    text_node = TextNode(code_text, TextType.TEXT)
    code_leaf = text_node_to_html_node(text_node)
    
    return ParentNode("pre", [ParentNode("code", [code_leaf])])

def quote_to_html_node(block):
    """Convert a quote block to an HTMLNode."""
    # Remove > from each line and join
    lines = block.split('\n')
    quote_lines = []
    for line in lines:
        if line.startswith('> '):
            quote_lines.append(line[2:])
        elif line.startswith('>'):
            quote_lines.append(line[1:])
        else:
            quote_lines.append(line)
    
    quote_text = '\n'.join(quote_lines)
    children = text_to_children(quote_text)
    
    return ParentNode("blockquote", children)

def unordered_list_to_html_node(block):
    """Convert an unordered list block to an HTMLNode."""
    lines = block.split('\n')
    list_items = []
    
    for line in lines:
        # Remove the "- " prefix
        if line.startswith('- '):
            item_text = line[2:]
            children = text_to_children(item_text)
            list_item = ParentNode("li", children)
            list_items.append(list_item)
    
    return ParentNode("ul", list_items)

def ordered_list_to_html_node(block):
    """Convert an ordered list block to an HTMLNode."""
    lines = block.split('\n')
    list_items = []
    
    for line in lines:
        # Find the first ". " and remove everything before and including it
        dot_index = line.find('. ')
        if dot_index != -1:
            item_text = line[dot_index + 2:]
            children = text_to_children(item_text)
            list_item = ParentNode("li", children)
            list_items.append(list_item)
    
    return ParentNode("ol", list_items)

def block_to_html_node(block):
    """Convert a single block to its corresponding HTMLNode."""
    block_type = block_to_block_type(block)
    
    if block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    elif block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    elif block_type == BlockType.CODE:
        return code_to_html_node(block)
    elif block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
    elif block_type == BlockType.UNORDERED_LIST:
        return unordered_list_to_html_node(block)
    elif block_type == BlockType.ORDERED_LIST:
        return ordered_list_to_html_node(block)
    else:
        raise ValueError(f"Unknown block type: {block_type}")

def markdown_to_html_node(markdown):
    """Convert raw markdown text to an HTML node."""
    # Split the markdown into blocks
    blocks = markdown_to_blocks(markdown)
    
    # Convert each block to an HTMLNode
    html_blocks = []
    for block in blocks:
        block_node = block_to_html_node(block)
        html_blocks.append(block_node)
    
    # Wrap all blocks in a parent div
    return ParentNode("div", html_blocks)

def extract_title(markdown):
    """Extract the title from the markdown text."""
    # Split the markdown into lines
    lines = markdown.split('\n')
    
    # Find the first h1 heading (starts with single #)
    for line in lines:
        line = line.strip()
        if line.startswith('# ') and not line.startswith('## '):
            # Remove the # and any extra whitespace
            return line[2:].strip()
    
    # If no h1 heading found, raise an exception
    raise ValueError("No h1 header found in markdown")

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    for filename in os.listdir(dir_path_content):
        from_path = os.path.join(dir_path_content, filename)
        dest_path = os.path.join(dest_dir_path, filename)
        if os.path.isfile(from_path):
            dest_path = Path(dest_path).with_suffix(".html")
            generate_page(from_path, template_path, dest_path, basepath)
        else:
            generate_pages_recursive(from_path, template_path, dest_path, basepath)


def generate_page(from_path, template_path, dest_path, basepath):
    print(f" * {from_path} {template_path} -> {dest_path}")
    from_file = open(from_path, "r")
    markdown_content = from_file.read()
    from_file.close()

    template_file = open(template_path, "r")
    template = template_file.read()
    template_file.close()

    node = markdown_to_html_node(markdown_content)
    html = node.to_html()

    title = extract_title(markdown_content)
    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", html)
    template = template.replace('href="/', 'href="' + basepath)
    template = template.replace('src="/', 'src="' + basepath)

    dest_dir_path = os.path.dirname(dest_path)
    if dest_dir_path != "":
        os.makedirs(dest_dir_path, exist_ok=True)
    to_file = open(dest_path, "w")
    to_file.write(template)
