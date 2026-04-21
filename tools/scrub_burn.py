import os
import re
import sys

def scrub_burn_ignore_sudo(directory):
    # Matches 'burn-ignore-sudo' (case insensitive) and any immediate trailing spaces, tabs, colons, or dashes.
    # We explicitly avoid matching \n so we don't accidentally consume line breaks.
    tag_pattern = re.compile(r'burn-ignore-sudo[ \t:-]*', re.IGNORECASE)
    
    # Matches a Python comment that is completely empty at the end of a line (e.g., "  # \n" or "x = 1  #\n")
    empty_py_comment = re.compile(r'[ \t]*#[ \t]*\n?$')
    
    # Matches an XML comment that is completely empty
    empty_xml_comment = re.compile(r'')

    files_modified = 0

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if not (filename.endswith('.py') or filename.endswith('.xml')):
                continue
                
            filepath = os.path.join(root, filename)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                continue
                
            new_lines = []
            changed = False
            
            for line in lines:
                # Fast bypass for lines without the target
                if 'burn-ignore-sudo' not in line.lower():
                    new_lines.append(line)
                    continue
                    
                changed = True
                
                # 1. Remove the tag and any trailing punctuation tying it to the next words
                mod_line = tag_pattern.sub('', line)
                
                # 2. Cleanup empty comments based on file type
                if filename.endswith('.py'):
                    # If the comment is now just an empty hash, strip it out
                    if empty_py_comment.search(mod_line):
                        mod_line = empty_py_comment.sub('\n', mod_line)
                    
                    # If it was a full-line comment that is now empty, drop the line entirely
                    if line.strip().startswith('#') and not mod_line.strip():
                        continue 
                        
                elif filename.endswith('.xml'):
                    # If the XML comment is now empty, strip it out
                    if empty_xml_comment.search(mod_line):
                        mod_line = empty_xml_comment.sub('', mod_line)
                    
                    # If it was a full-line XML comment that is now empty, drop the line entirely
                    if line.strip().startswith('`  →  *(Drops the entire line from the XML file)*
