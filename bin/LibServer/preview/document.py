from LibServer.preview import ObjectPreview
from LibServer.preview import PreviewBase
from LibServer.preview import get_file_path
import markdown

class MarkdownPreview(PreviewBase):
    @staticmethod
    def can_preview(filename):
        return filename.endswith(".md")
    @staticmethod
    def generate_preview(filename):
        doc = open(get_file_path(filename), 'r')
        doc_contents = doc.read()
        doc.close()
        doc_md = markdown.markdown(doc_contents)
        return ObjectPreview(
            "Markdown",
            doc_md,
            "file-text",
            "markdown"
        )
