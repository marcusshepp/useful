import os
from typing import List, Optional
from anthropic import Anthropic
from pathlib import Path

class Component:
    def __init__(self, name: str, html: str, css: str, ts: str):
        self.name = name
        self.html = html
        self.css = css
        self.ts = ts

class AngularGenerator:
    def __init__(self, api_key: str, output_dir: str = "generated_components"):
        self.client = Anthropic(api_key=api_key)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def read_file(self, filepath: str) -> str:
        try:
            with open(filepath, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise Exception(f"Template file not found: {filepath}")
            
    def ask_anthropic(self, prompt: str) -> str:
        try:
            message = self.client.messages.create(
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
                model="claude-3-5-sonnet-latest"
            )
            # Get the content directly from the message response
            return message.content[0].text if message.content else ""
        except Exception as e:
            print(f"API Error: {str(e)}")
            return ""

    def extract_sections(self, response: str) -> List[str]:
        sections = []
        for line in response.split('\n'):
            if any(line.strip().startswith(f"{i}.") for i in range(1, 20)):
                section = line.split('.', 1)[1].strip()
                sections.append(self._sanitize_component_name(section))
        return sections

    def _sanitize_component_name(self, name: str) -> str:
        """Convert section names to valid Angular component names"""
        return name.lower().replace(' ', '-').replace('/', '-').replace('(', '').replace(')', '')

    def _generate_prompts(self, section: str) -> dict:
        base_context = """We're creating an Angular app from an HTML template. 
        Output only the necessary code with no comments or explanations."""
        
        prompts = {
            'html': f"{base_context} Create the HTML template for the {section} component.",
            'css': f"{base_context} Create the SCSS styles for the {section} component.",
            'ts': f"{base_context} Create the TypeScript code for the {section} component."
        }

        for key, value in prompts.items():
            prompts[key] =  f"""
            {value}

            Output only the necessary code with no comments or explanations
            Do not ouput ```typescript``` or ```html``` code blocks.
            your output will be used to directly
            pipe into the creation on a new Angular component.
            """
        return prompts

    def generate_component(self, section: str) -> Component:
        """Generate a complete Angular component"""
        prompts = self._generate_prompts(section)
        
        component = Component(
            name=section,
            html=self.ask_anthropic(prompts['html']),
            css=self.ask_anthropic(prompts['css']),
            ts=self.ask_anthropic(prompts['ts'])
        )
        
        self._write_component_files(component)
        return component

    def _write_component_files(self, component: Component):
        """Write component files to disk"""
        component_dir = self.output_dir / component.name
        component_dir.mkdir(exist_ok=True)
        
        file_mapping = {
            'html': f"{component.name}.component.html",
            'css': f"{component.name}.component.scss",
            'ts': f"{component.name}.component.ts"
        }
        
        for content_type, filename in file_mapping.items():
            print('Writing:', filename, content_type)
            content = getattr(component, content_type)
            with open(component_dir / filename, 'w') as f:
                f.write(content)

    def generate_project_structure(self, html_template: str) -> None:
        """Main method to generate the entire project structure"""
        try:
            # Get project goal/context
            goal_prompt = """Create a two-sentence goal for converting this HTML template 
            to Angular components. Be specific and concise."""
            project_goal = self.ask_anthropic(goal_prompt)
            
            # Get sections
            sections_prompt = f"""
            {project_goal}
            Break this HTML template into logical Angular components.
            Output only a numbered list of component names:
            {html_template}
            """
            sections_response = self.ask_anthropic(sections_prompt)
            sections = self.extract_sections(sections_response)
            
            for section in sections[0]:
                try:
                    print(f"Generating component: {section}")
                    self.generate_component(section)
                    print(f"Generated component: {section}")
                except Exception as e:
                    print(f"Error generating {section}: {str(e)}")
        except Exception as e:
            print(f"Error in project structure generation: {str(e)}")

def main():
    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise Exception("ANTHROPIC_API_KEY environment variable not set")
            
        generator = AngularGenerator(api_key)
        template = generator.read_file("index-3-dark.html")
        generator.generate_project_structure(template)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
