from ebooklib import epub

class EpubWrapper:
    def __init__(self, file_path):
        self.book = epub.read_epub(file_path)

    def read_title(self):
        title = self.book.get_metadata('DC', 'title')
        if title:
            return f"Modified Title: {title[0][0]}"
        return "Title not found."

    def add_chapter(self, title, content):
        chapter = epub.EpubHtml(title=title, file_name=f'{title}.xhtml', lang='en')
        chapter.set_body_content(content)
        self.book.add_item(chapter)
        self.book.spine.append(chapter)

    def save(self, output_path):
        epub.write_epub(output_path, self.book, {})

class InternalFileError(EpubException):

    def __init__(self, code, message, filename):

        super().__init__(code, message)

        self.filename = filename



    def __repr__(self):

        return "<InternalFileError: %s -> %s>"  % (self.filename, self.msg)