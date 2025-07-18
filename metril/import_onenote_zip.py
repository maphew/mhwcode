"""Process OneNote zip archive and prepare it for Trilium import.

Make OneNote HTML exports trilium compatible.
- Identifies and converts the page title (first h1 or p with larger font size) to a proper h1 tag
- Italicizes the date after fixing the title
- remove filelist.xml files (not needed) 
"""

import os
import re
import zipfile
from typing import Optional, Tuple
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment configuration
if load_dotenv():
    server_url = os.getenv('TRILIUM_HOST')
    token = os.getenv('TRILIUM_TOKEN')
else:
    print(".env not found")
    print("Please set TRILIUM_HOST and TRILIUM_TOKEN environment variables - https://github.com/zadam/trilium/wiki/ETAPI")
    exit(1)

import click
from trilium_py.client import ETAPI

@dataclass
class FontConfig:
    """Configuration for font size processing"""
    default_size: float = 11.0
    size_threshold_multiplier: float = 1.1  # Title should be >10% larger than base

def extract_font_size(style: Optional[str]) -> Optional[float]:
    """Extract font size value from CSS style string.
    
    Args:
        style: CSS style string that may contain font-size
        
    Returns:
        Float value of font size if found, None otherwise
    """
    if not style or 'font-size:' not in style:
        return None
    
    try:
        font_str = style.split('font-size:')[1].split(';')[0]
        return float(re.search(r'\d+(?:\.\d+)?', font_str).group())
    except (IndexError, AttributeError):
        return None

def get_base_font_size(soup: BeautifulSoup, config: FontConfig) -> float:
    """Extract base font size from body tag or return default.
    
    Args:
        soup: BeautifulSoup parsed HTML
        config: Font configuration settings
        
    Returns:
        Base font size value
    """
    body = soup.find('body')
    if body and (font_size := extract_font_size(body.get('style'))):
        print(f'Found body font size: {font_size}')
        return font_size
    
    print(f'Using default font size: {config.default_size}')
    return config.default_size

def process_title_tag(tag: Tag, base_font_size: float, config: FontConfig) -> Optional[str]:
    """Process a potential title tag and convert to h1 if appropriate.
    
    Args:
        tag: HTML tag to process
        base_font_size: Base font size for comparison
        config: Font configuration settings
        
    Returns:
        Processed title text if tag was converted to h1, None otherwise
    """
    if not tag.get('style'):
        return None
        
    font_size = extract_font_size(tag.get('style'))
    if not font_size or font_size <= base_font_size * config.size_threshold_multiplier:
        return None
        
    # Clean and normalize title text
    title = re.sub(r'\s+', ' ', tag.get_text())
    tag.name = 'h1'
    tag.string = title
    return title

def update_html_title(soup: BeautifulSoup, title: str) -> None:
    """Update both the <title> tag and create/update <h1> with the given title.
    
    Args:
        soup: BeautifulSoup parsed HTML
        title: Title text to set
    """
    # Update or create title tag in head
    head = soup.find('head')
    if not head:
        head = soup.new_tag('head')
        if soup.html:
            soup.html.insert(0, head)
        else:
            html = soup.new_tag('html')
            html.append(head)
            soup.append(html)
    
    title_tag = head.find('title')
    if not title_tag:
        title_tag = soup.new_tag('title')
        head.append(title_tag)
    title_tag.string = title
    
    # Update or create h1 tag in body
    h1_tag = soup.find('h1')
    if not h1_tag:
        h1_tag = soup.new_tag('h1')
        body = soup.find('body')
        if body:
            if body.contents:
                body.insert(0, h1_tag)
            else:
                body.append(h1_tag)
    h1_tag.string = title

def italicize_first_date(soup: BeautifulSoup) -> None:
    """Find and wrap date/time paragraphs in semantic HTML5 time tags.
    
    Args:
        soup: BeautifulSoup parsed HTML
    """
    h1_tag = soup.find('h1')
    if not h1_tag:
        return
    
    # Find the first two p tags after h1 (date and time)
    date_p = h1_tag.find_next('p')  # First p tag is the date
    if date_p:
        # Create time tag with datetime attribute
        date_text = date_p.get_text().strip()
        time_tag = soup.new_tag('time')
        try:
            # Try to parse the date to a standard format for the datetime attribute
            # OneNote format is typically YYYY-MMM-DD
            from datetime import datetime
            parsed_date = datetime.strptime(date_text, '%Y-%b-%d')
            time_tag['datetime'] = parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            # If we can't parse the date, just use the text as is
            time_tag['datetime'] = date_text
        
        date_p.string = date_text
        date_p.string.wrap(time_tag)
        
        # Get the next p tag (time)
        time_p = date_p.find_next('p')
        if time_p:
            time_text = time_p.get_text().strip()
            time_tag = soup.new_tag('time')
            try:
                # Try to parse the time
                parsed_time = datetime.strptime(time_text, '%I:%M %p')
                time_tag['datetime'] = parsed_time.strftime('%H:%M')
            except ValueError:
                time_tag['datetime'] = time_text
            
            time_p.string = time_text
            time_p.string.wrap(time_tag)

def convert_page_title_to_h1(html: bytes, config: FontConfig = FontConfig()) -> str:
    """Convert OneNote HTML page title to proper h1 tag and process date.
    
    Args:
        html: Raw HTML content
        config: Font configuration settings
        
    Returns:
        Processed HTML with proper h1 title and italicized date
    """
    soup = BeautifulSoup(html.decode('utf-8'), 'html.parser')
    base_font_size = get_base_font_size(soup, config)
    
    # Process potential title tags
    title = None
    for tag in soup.find_all(['h1', 'p'])[:5]:  # Check first 5 candidates
        try:
            if title := process_title_tag(tag, base_font_size, config):
                print(f'Found and converted title: {title}')
                # Remove the original tag since we'll create a new one
                tag.decompose()
                break
        except Exception as e:
            print(f'Error processing tag: {tag} - {str(e)}')
            continue
    
    if title:
        update_html_title(soup, title)
    
    # Process the date after finding the title
    try:
        italicize_first_date(soup)
        print('Processed date paragraph')
    except Exception as e:
        print(f'Error processing date: {str(e)}')
    
    new_html = soup.prettify()
    
    # Debug output
    new_title_index = new_html.find('title')
    if new_title_index >= 0:
        new_title = new_html[new_title_index - 1:new_title_index + 50]
        print(f'New title:\n{new_title}\n')
    body_index = new_html.find('<body')
    if body_index >= 0:
        preview = new_html[body_index:body_index + 700]
        print(f'Preview of processed HTML body:\n{preview}\n')
    
    return new_html

@click.command(help="Process OneNote ZIP export for Trilium import")
@click.argument("zip_path", required=True)
@click.option('--keep-filelist', is_flag=True, help='Keep filelist.xml files (removed by default)')
@click.option('--debug', is_flag=True, help='Show debug information')
def process_zip(zip_path: str, keep_filelist: bool = False, debug: bool = False) -> str:
    """Process OneNote ZIP export and prepare for Trilium import.
    
    Args:
        zip_path: Path to OneNote ZIP export
        keep_filelist: If True, keep filelist.xml files, otherwise remove them
        debug: If True, show additional debug information
        
    Returns:
        Path to processed ZIP file
    """
    os.chdir('./out')
    output_zip_path = 'fixed_' + os.path.basename(zip_path)
    
    with open(zip_path, 'rb') as f:
        with zipfile.ZipFile(f) as input_zip:
            # Debug: List all files in zip
            if debug:
                print("\nFiles in ZIP:")
                for file_info in input_zip.filelist:
                    print(f"  {file_info.filename} ({file_info.file_size:,} bytes)")
                print()
            
            with zipfile.ZipFile(output_zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as output_zip:
                for file_info in input_zip.filelist:
                    filename = file_info.filename
                    
                    # Skip filelist.xml files unless explicitly kept
                    if 'filelist.xml' in filename and not keep_filelist:
                        print(f'Skipping: {filename}')
                        continue
                    
                    with input_zip.open(filename) as source:
                        if filename.endswith('.htm'):
                            fixed_html = convert_page_title_to_h1(source.read())
                            output_zip.writestr(filename, fixed_html)
                            if debug:
                                print(f'Processed HTML in: {filename} ({file_info.file_size:,} bytes)')
                            else:
                                print(f'Processed HTML in: {filename}')
                        else:
                            output_zip.writestr(filename, source.read())
                            if debug:
                                print(f'Copied: {filename} ({file_info.file_size:,} bytes)')
                            elif filename.endswith('/'):  # Only print directory entries in non-debug mode
                                print(f'Copied: {filename}')
    
    print(f'\nCreated processed ZIP file: {output_zip_path}')
    return output_zip_path

# Alias for backward compatibility
get_zip = process_zip

if __name__ == '__main__':
    process_zip()
