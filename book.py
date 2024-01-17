from ebooklib import epub
import io
import uuid
from PIL import Image as PILImage
from generate import Outline, Chapter


def create_epub_book(outline:Outline, chapters: [Chapter], cover_image: PILImage, chapter_images: [PILImage],
                     author: str, out_path: str) -> epub.EpubBook:
    # Create a new EPUB book
    book = epub.EpubBook()

    # Set the title and author of the book
    book.set_title(outline.title)
    book.add_author(author)

    # Add cover image
    cover_image_bytes = io.BytesIO()
    cover_image.save(cover_image_bytes, format='JPEG')
    cover_image_bytes.seek(0)

    # Set the cover image in the metadata
    book.set_cover("cover.jpg", cover_image_bytes.getvalue())

    # Initialize a list to store the book's spine
    spine = ['nav']

    # Create a separate HTML file for the cover image
    cover_page = epub.EpubHtml(title='Cover', file_name='cover_page.xhtml', lang='en')
    cover_page_content = '<img src="cover.jpg" alt="Cover Image" style="width: 100%;">'
    cover_page.set_content(cover_page_content)
    book.add_item(cover_page)

    # Set the cover page as the first item in the spine
    spine.append(cover_page)

    # Add introduction chapter
    intro_content = f'''
    <html>
    <head>
    <style>
        body {{ 
            text-align: center; 
            margin: 50px; 
            font-family: Arial, sans-serif;
        }}
        hr {{ 
            border: none; 
            border-left: 1px solid hsla(200, 10%, 50%, 100);
            height: 100px; 
            width: 1px; 
        }}
        .author {{ 
            font-style: italic; 
            font-size: 0.8em; 
        }}
    </style>
    </head>
    <body>
        <h1>{outline.title}</h1>
        <hr>
        <div class="author">by {author}</div>
        <hr>
        <h2>Welcome to Your German Learning Journey!</h2>
        <p>This book is designed as a learning tool for beginners in German. It provides a gentle introduction to the language, with each chapter crafted to enhance your understanding and skills progressively.</p>
        <p>As you embark on reading texts in German, start by familiarizing yourself with basic vocabulary and grammar structures. Don't worry about understanding every single word; instead, focus on the context and the general meaning of sentences. Over time, your vocabulary and comprehension will naturally improve. Remember, consistency is key in language learning, so read regularly and patiently.</p>
        <p>Each chapter in this book is accompanied by a list of hard words with explanations, aiding your learning process. Happy reading and learning!</p>
    </body>
    </html>
    '''
    intro_chapter = epub.EpubHtml(title='Introduction', file_name='intro.xhtml', lang='en')
    intro_chapter.set_content(intro_content)
    book.add_item(intro_chapter)
    spine.append(intro_chapter)

    # Add each chapter to the book
    for idx, (chapter, chapter_image) in enumerate(zip(chapters, chapter_images)):
        # Convert chapter image to bytes
        chapter_image_bytes = io.BytesIO()
        chapter_image.save(chapter_image_bytes, format='JPEG')
        chapter_image_bytes.seek(0)

        # Create an EPUB image item for the chapter image
        img_name = f'chapter_{uuid.uuid4().hex[:8]}.jpg'
        img_item = epub.EpubImage()
        img_item.file_name = img_name
        img_item.media_type = 'image/jpeg'
        img_item.content = chapter_image_bytes.read()
        book.add_item(img_item)

        # Prepare the list of hard words
        hard_words_list = "<ul>"
        for word in chapter.hard_words:
            hard_words_list += f"<li>{word}</li>"
        hard_words_list += "</ul>"

        chapter_summary = outline.chapter_outlines[idx]
        # Create an EPUB chapter
        chapter_html = f'<img src="{img_name}" alt="Chapter image"/><h1>{chapter.title}</h1><p>{chapter.content}</p>' \
                       f'<h2>Schwierige Wörter</h2>{hard_words_list}<h2>Zusammenfassung</h2><p>{chapter_summary}</p>'
        epub_chapter = epub.EpubHtml(title=chapter.title, file_name=f'{uuid.uuid4().hex[:8]}.xhtml', lang='de')
        epub_chapter.set_content(chapter_html)

        # Add chapter to the book and its spine
        book.add_item(epub_chapter)
        spine.append(epub_chapter)

    # Define the book's spine
    book.spine = spine

    # Add navigation files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Write the EPUB file
    epub.write_epub(out_path + f"{outline.title}.epub", book, {})

    return book