import os
from anthropic import Anthropic

"""
HTML Template to angular app
This could work 

break the html into sections 
each section gets its own component

use the entire template as an input to the python script
the python script will break the template into sections
each section will be a component
the python script will generate the angular components using claude as a model
each section could write to a file and talk to each other with a config

The components should well named and organized as much as they can. 

We will need to start with a prompt that names the file for that specific component

###
### Think smaller components of prompts
### these give the code a dash of personality
###

The first will take in the entire html template and break it into sections

`
You are helping convert a HTML template into an Angular app
Break the html into sections
only output a list of sections
These sections will be used to create Angular components
`

SECTIONS = html chucks

What is a good name for this component? Consider:
    [[ Small description of the project ]]

    -> Input: Section of HTML
    -> Output: [[ Angular Component ]]  Name



What is the structure or common elements of the entire project?
What is the common parent components that will hold all the other components?

header
navigation
footer


Create a new Angular component named [[ Angular Component ]]

"""

client = Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)


def read_file(file):
    with open(file, 'r') as f:
        return f.read()

def ask_anthropic(question):
    message = client.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": question,
            },
        ],
        model="claude-3-5-sonnet-latest",
    )
    return message;

def extract_sections(response):
    content = response.content[0].text
    sections = []
    for line in content.split('\n'):
        if any(line.strip().startswith(f"{i}.") for i in range(1, 20)):
            section = line.split('.', 1)[1].strip()
            sections.append(section)
    return sections


if __name__ == "__main__":

    html = read_file("index-3-dark.html")

    print('html', html[0:150])

    # GOAL THEME VISION
    goal_prompt = f"""
    You are helping convert a HTML template into an Angular app
    We're breaking the html into sections
    and creating angular components from each section
    Assume all sections are equal in importance

    create a two sentence goal for the project
    this goal will be used as context for all the components.

    Only output one string of text such that I can use the text in the rest of the prompts i'm going to write.

    this will be creating names for the components
    what the component structure will look like
    and what the common elements of the project are

    """

    prompt1 = f"""

            {goal_prompt}

            You are helping convert a HTML template into an Angular app
            Break the html into sections
            only output a list of sections
            These sections will be used to create Angular components

            the code that uses your output will be iterating over the dictionary that you output

            for example: 
            {
                "name": "header",
            }

            it will use the name key to create a file for the component


            here is the html:

            {html}
            """

    print('prompt1', prompt1[0:150])
    first_impression = ask_anthropic(prompt1)
    sections = extract_sections(first_impression)
    print('sections', )
    for section in sections:
        html = f"""
        We're creating an angular app from an HTML template

        Your job is to create the HTML file only for your component.
        You will output just html
        The html will work and make sense for what it needs to do in the larger scheme of things
        with no comments.

        your output with be used to create a file that should work in the larger scheme of things

        Your component is:
        {section}

        You output should also contain a summary of whats been done so far
        """
        css = f"""
        We're creating an angular app from an HTML template

        Your job is to create the HTML file only for your component.
        You will output just html
        The html will work and make sense for what it needs to do in the larger scheme of things
        with no comments.

        your output with be used to create a file that should work in the larger scheme of things

        Your component is:
        {section}

        You output should also contain a summary of whats been done so far
        """
        js = f"""
        We're creating an angular app from an HTML template

        Your job is to create the HTML file only for your component.
        You will output just html
        The html will work and make sense for what it needs to do in the larger scheme of things
        with no comments.

        your output with be used to create a file that should work in the larger scheme of things

        Your component is:
        {section}

        You output should also contain a summary of whats been done so far
        """

        f = ask_anthropic(js)
        a = ask_anthropic(css)
        h = ask_anthropic(html)

        open(f"{section}.html", "w").write(f.content[0].text)
                                           )







