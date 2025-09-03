import os
import shutil
import sys

from copystatic import copy_files_recursive
from funcs import generate_pages_recursive

dir_path_static = "./static"
dir_path_public = "./docs"  # Changed from public to docs for GitHub Pages
dir_path_content = "./content"
template_path = "./template.html"

def main():
    # Get basepath from command line argument, default to "/"
    basepath = "/"
    if len(sys.argv) > 1:
        basepath = sys.argv[1]
    
    print(f"Using basepath: {basepath}")
    
    print("Deleting docs directory...")
    if os.path.exists(dir_path_public):
        shutil.rmtree(dir_path_public)

    print("Copying static files to docs directory...")
    copy_files_recursive(dir_path_static, dir_path_public)
    
    print("Generating pages recursively...")
    generate_pages_recursive(dir_path_content, template_path, dir_path_public, basepath)
    
    print("Static site generation complete!")

if __name__ == "__main__":
    main()