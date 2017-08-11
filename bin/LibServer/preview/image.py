from LibServer.preview import PreviewBase, get_extension, get_file_path, ObjectPreview
from flask import url_for
import os
import os.path
import exifread

image_exts = ('jpg', 'jpe','jpeg','png','gif')

class ImagePreview(PreviewBase):
    @staticmethod
    def can_preview(filename):
        # first order pass: see if it looks like a picture
        end = get_extension(filename)
        if end.lower() in image_exts:
            return True
        return False

    @staticmethod
    def generate_preview(path):
        preview = ObjectPreview("Image", "(placeholder content)", "picture-o", "image")
        preview.content = '<img src="'+url_for('browser.fetch_file',
            name=path)+'" class="img-responsive" />'
        return preview

class ExifPreview(PreviewBase):
    @staticmethod
    def get_tags(filepath):
        f = open(filepath, 'rb')
        tags = exifread.process_file(f, details=False)
        f.close()
        return tags
    
    @staticmethod
    def can_preview(path):
        return len(ExifPreview.get_tags(get_file_path(path))) > 0
    @staticmethod
    def generate_preview(path):
        tags = ExifPreview.get_tags(get_file_path(path))
        content = '<table class="table">'
        for tag in tags:
            content += '\n<tr><td>'+str(tag)+'</td><td>'+str(tags[tag])+'</td></tr>'
        content += '</table>'
        return ObjectPreview("EXIF", content, "camera-retro", "exif")
