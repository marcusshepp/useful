import glob
import os
import argparse
import subprocess
from typing import Set, Dict
from collections import defaultdict

def parse_args():
    parser = argparse.ArgumentParser(description='Analyze Angular component dependencies')
    parser.add_argument('--project-path', '-p', required=True, 
                       help='Path to the Angular project root directory')
    parser.add_argument('--from-commit', required=True,
                       help='Starting commit hash')
    parser.add_argument('--to-commit', required=True,
                       help='Ending commit hash')
    return parser.parse_args()

def get_file_content_at_commit(project_path: str, file_path: str, commit_hash: str) -> str:
    """Get content of a file at a specific commit"""
    try:
        result = subprocess.run(
            ['git', 'show', f'{commit_hash}:{file_path}'],
            capture_output=True,
            text=True,
            cwd=project_path
        )
        if result.returncode == 0:
            return result.stdout
        return None
    except:
        return None

def get_changed_files(project_path: str, from_commit: str, to_commit: str) -> Dict[str, str]:
    """Get list of changed files with their status (A=Added, M=Modified, D=Deleted)"""
    result = subprocess.run(
        ['git', 'diff', '--name-status', f'{from_commit}..{to_commit}'],
        capture_output=True, 
        text=True,
        cwd=project_path
    )
    if result.returncode != 0:
        print(f"Error getting git diff: {result.stderr}")
        exit(1)
    
    changes = {}
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        status, file_path = line.split(maxsplit=1)
        changes[file_path] = status
    return changes

def find_component_references(component_name: str, project_path: str) -> Set[str]:
    references = set()
    search_pattern = os.path.join(project_path, "src/**/*.ts")
    for file_path in glob.glob(search_pattern, recursive=True):
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                if component_name in content:
                    relative_path = os.path.relpath(file_path, project_path)
                    references.add(relative_path)
        except Exception as e:
            print(f"Warning: Could not read file {file_path}: {e}")
    return references

def find_service_dependencies(file_content: str) -> Set[str]:
    """Find services used by a component from its content"""
    services = set()
    if not file_content:
        return services
        
    import re
    service_matches = re.findall(r'constructor\((.*?)\)', file_content)
    for match in service_matches:
        services.update(re.findall(r'private (\w+Service)', match))
    return services

def analyze_impact(project_path: str, from_commit: str, to_commit: str) -> Dict:
    changed_files = get_changed_files(project_path, from_commit, to_commit)
    results = {
        'changed_components': [],
        'service_dependencies': defaultdict(list),
        'impacted_areas': set(),
        'deleted_components': []
    }
    
    for file_path, status in changed_files.items():
        if not file_path.endswith('.component.ts'):
            continue
            
        component_name = os.path.basename(file_path).replace('.component.ts', '')
        
        if status == 'D':
            results['deleted_components'].append(file_path)
            # For deleted components, check content at the old commit
            content = get_file_content_at_commit(project_path, file_path, from_commit)
        else:
            results['changed_components'].append(file_path)
            if status == 'A':
                # For new components, check current content
                content = get_file_content_at_commit(project_path, file_path, to_commit)
            else:
                # For modified components, check both old and new content
                content = get_file_content_at_commit(project_path, file_path, to_commit)
        
        if content:
            # Find direct component usage
            references = find_component_references(component_name, project_path)
            results['impacted_areas'].update(references)
            
            # Find service dependencies
            services = find_service_dependencies(content)
            if services:
                results['service_dependencies'][component_name].extend(services)
                for service in services:
                    service_usages = find_component_references(service, project_path)
                    results['impacted_areas'].update(service_usages)
    
    # Remove the originally changed files
    results['impacted_areas'] = results['impacted_areas'] - set(changed_files.keys())
    return results

def write_report(results: Dict, from_commit: str, to_commit: str):
    with open('output.txt', 'w') as f:
        f.write("Angular Component Impact Analysis Report\n")
        f.write("=====================================\n\n")
        
        f.write(f"Commit Range: {from_commit[:7]} -> {to_commit[:7]}\n\n")
        
        if results['changed_components']:
            f.write("Modified/Added Components:\n")
            f.write("------------------------\n")
            for component in results['changed_components']:
                f.write(f"• {component}\n")
            f.write("\n")
        
        if results['deleted_components']:
            f.write("Deleted Components:\n")
            f.write("------------------\n")
            for component in results['deleted_components']:
                f.write(f"• {component}\n")
            f.write("\n")
        
        if results['service_dependencies']:
            f.write("Service Dependencies:\n")
            f.write("--------------------\n")
            for component, services in results['service_dependencies'].items():
                if services:
                    f.write(f"• {component} uses: {', '.join(services)}\n")
            f.write("\n")
        
        f.write("Areas Requiring Regression Testing:\n")
        f.write("--------------------------------\n")
        for area in sorted(results['impacted_areas']):
            f.write(f"• {area}\n")

if __name__ == "__main__":
    args = parse_args()
    project_path = os.path.abspath(args.project_path)
    
    if not os.path.exists(project_path):
        print(f"Error: Project path {project_path} does not exist")
        exit(1)
        
    print(f"Analyzing project at: {project_path}")
    results = analyze_impact(project_path, args.from_commit, args.to_commit)
    write_report(results, args.from_commit, args.to_commit)
    print("\nAnalysis complete. Results written to output.txt")
