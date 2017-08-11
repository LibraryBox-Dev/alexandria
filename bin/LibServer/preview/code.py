from LibServer.preview import PreviewBase, ObjectPreview, get_file_path, get_extension
import os.path
import markdown


class MarkdownPreview(PreviewBase):
    @staticmethod
    def can_preview(file_path):
        return file_path.endswith(".md")
    @staticmethod
    def generate_preview(file_path):
        ff = codecs.open(get_file_path(file_path), mode='r', encoding="utf-8")
        text = ff.read()
        ff.close()
        content = markdown.markdown(text)
        return ObjectPreview(name="Markdown", icon="toggle-down", content=content, id="markdown")

class CodePreview(PreviewBase):

    extensions = ( 'txt',
     'py', 'js', 'css', 'html', 'less', 'sass', 'cs','csproj','vb', 'vbproj', 'vcxproj',
     'c', 'h', 'cpp', 'hpp', 'm', 'sh', 'zsh', 'java', 'xml', 'json', 'htm', 'php',
     'smali', 'ino', 'bat', 'mrc', 'rc', 'gcode', 'md', 'rst', 'pl', 'pm', 'inc', 'cc', 
     'tcl', 'coffee', 'ml', 'ps1', 'conf', 'twig', 'tpl', 'el', 'cl', 'vim', 'fs','scala',
     'tex','rb', 's' )

    @staticmethod
    def can_preview(file_path):

        ext = get_extension(file_path)
        return ext in CodePreview.extensions

    @staticmethod
    def generate_preview(file_path):
        file_contents = ""
        file = open(get_file_path(file_path), 'r')
        file_contents = file.read()
        file.close()
        result = "<pre><code>"+file_contents+"</pre></code>"
        
        return ObjectPreview(name="Code", icon="code", content=result, id="code-preview")
