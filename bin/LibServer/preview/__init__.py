import os
import urllib
from LibServer import app
from flask import safe_join

"""
The preview engine

This was adapted from the preview engine in 9track by Morgan Gangwere.

This gives LibServ a means to preview some files, specifically images, text files and other content which is possibly interesting.
One specific use of this is to provide EXIF metadata for pictures, as well as some metadata about ebooks later on.
"""

def get_extension(filename):
    return os.path.splitext(filename)[1][1:]

class ObjectPreview(object):
    """
    The base of all previews. This preview base is purely a placeholder, and if you end up not overriding one of its parts,
    you'll end up with a broken preview.
    """
    name = "Unknown"
    content = "No preview!"
    icon = "question"
    id = "unknown"
    js = []
    css = []
    def __init__(self, name="(none)", content="", icon="unknown", id="unknown", js=[], css=[]):
        self.name = name
        self.content = content
        self.icon = icon
        self.id=id
        self.js = js
        self.css = css

def get_file_path(path):
    """
    Gets the real filepath of a file within the Alexandria environment
    """
    return safe_join(app.config.get('storage','location',None),path)

class PreviewBase(object):
    
    @staticmethod
    def can_preview(file_path):
        return False
    
    @staticmethod
    def generate_preview(file_path):
        """
        """
        return ObjectPreview() 

from .image import ImagePreview,ExifPreview
from .code import  CodePreview
from .document import MarkdownPreview

__previewers = ( ImagePreview, ExifPreview, MarkdownPreview, CodePreview, PreviewBase )

def get_previews(path):
    previews = []
    for previewer in __previewers:
        if previewer.can_preview(path):
            previews.append(previewer.generate_preview(path))
    return previews

