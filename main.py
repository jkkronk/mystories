import argparse
import generate

def main():
    parser = argparse.ArgumentParser(description='Create your own story using gpt-4!')
    parser.add_argument('plot', type=str, help='The content of the story')
    parser.add_argument('language_level', type=str, default="A1", help='The content of the story')
    parser.add_argument('length', type=int, default=3000, help='The content of the story')

    args = parser.parse_args()

    print("------------Generate Story Outline------------")
    story = generate.story_outline(args.plot, args.length, args.language_level)
    print("Number of chapters: " + str(len(story.chapter_outlines)))
    chapters = []
    for chapter_outline in story.chapter_outlines:
        print("------------Generate Chapter------------")
        chapter = generate.write_chapter(chapter_outline, args.language_level)
        chapters.append(chapter)

    print("Title: " + story.title)
    print("Short Summary: " + story.short_summary)
    for chapter in chapters:
        print("Chapter: " + chapter.title)
        print("Content: " + chapter.content)
        print("Hard Words: " + str(chapter.hard_words))
        image = generate.create_image(story.chapter_image_prompt)
        image.show()
    image = generate.create_image(story.cover_image_prompt)
    image.show()



if __name__ == "__main__":
    main()


