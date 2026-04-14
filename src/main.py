from textnode import TextNode, TextType, markdown_to_html_node, extract_title

import os
import shutil
import sys



def copy_directory(src, dst):   
    if os.path.exists(dst):
        shutil.rmtree(dst)

    os.mkdir(dst)

    _copy_recursive(src, dst)


def _copy_recursive(src, dst):
    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)

        if os.path.isfile(src_path):
            print(f"Copying file: {src_path} -> {dst_path}")
            shutil.copy(src_path, dst_path)

        else:
            print(f"Creating directory: {dst_path}")
            os.mkdir(dst_path)

            # 🔁 recursion happens here
            _copy_recursive(src_path, dst_path)
def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    with open(from_path, "r") as f:
        mark = f.read()
    with open(template_path, "r") as f:
        temp = f.read()
    mark_html=markdown_to_html_node(mark).to_html()
    title=extract_title(mark)
    new_temp=temp.replace("{{ Title }}",title).replace("{{ Content }}", mark_html).replace('href="/', f'href="{basepath}').replace('src="/',f'src="{basepath}')
    dirpath = os.path.dirname(dest_path)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
   
    with open(dest_path, "w") as f:
        f.write(new_temp)        


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    for entry in os.listdir(dir_path_content):
        src_path = os.path.join(dir_path_content, entry)
        dest_path = os.path.join(dest_dir_path, entry)
       
        if os.path.isdir(src_path):
            generate_pages_recursive(src_path, template_path, dest_path, basepath)
      
        elif entry.endswith(".md"):
            html_filename = entry.replace(".md", ".html")
            dest_file_path = os.path.join(dest_dir_path, html_filename)

            generate_page(src_path, template_path, dest_file_path, basepath)




def main():
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    else:
        basepath = "/"
    nowy=TextNode("this", TextType.IMAGE, "https://www.google.com")
    print(nowy.__repr__())
    copy_directory("static", "docs")
    generate_pages_recursive("content", "template.html", "docs", basepath)

main()    
