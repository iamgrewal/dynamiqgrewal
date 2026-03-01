#!/usr/bin/env python3
"""
Stack Detection Script

Analyzes a codebase to detect programming languages, frameworks, test frameworks,
build systems, and security tools. Used by the PR code reviewer skill to load
appropriate reference checklists.

Usage:
    python3 detect-stack.py [directory]

If no directory is specified, uses current working directory.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict


def find_files(directory: Path, extensions: Set[str]) -> List[Path]:
    """Find all files with given extensions, excluding common ignore patterns."""
    ignore_dirs = {
        'node_modules', '.git', '__pycache__', 'venv', '.venv', 'env',
        'dist', 'build', 'target', '.idea', '.vscode', 'vendor',
        'coverage', '.next', '.nuxt', 'out', 'bin', 'obj'
    }

    files = []
    for root, dirs, filenames in os.walk(directory):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for filename in filenames:
            filepath = Path(root) / filename
            if filepath.suffix.lower() in extensions:
                files.append(filepath)

    return files


def detect_languages(directory: Path) -> Dict[str, Any]:
    """Detect programming languages based on file extensions."""
    extension_map = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.jsx': 'JavaScript',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript',
        '.go': 'Go',
        '.rs': 'Rust',
        '.java': 'Java',
        '.kt': 'Kotlin',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.cs': 'C#',
        '.cpp': 'C++',
        '.c': 'C',
        '.swift': 'Swift',
        '.m': 'Objective-C',
        '.scala': 'Scala',
        '.ex': 'Elixir',
        '.exs': 'Elixir',
        '.erl': 'Erlang',
        '.hs': 'Haskell',
        '.clj': 'Clojure',
        '.lua': 'Lua',
        '.r': 'R',
        '.sql': 'SQL',
    }

    extensions = set(extension_map.keys())
    files = find_files(directory, extensions)

    language_counts = defaultdict(int)
    for filepath in files:
        lang = extension_map.get(filepath.suffix.lower())
        if lang:
            language_counts[lang] += 1

    # Sort by count, return languages with any presence
    sorted_languages = sorted(language_counts.items(), key=lambda x: -x[1])
    languages = [lang for lang, count in sorted_languages if count > 0]

    return {
        'languages': languages,
        'primary': languages[0] if languages else None,
        'file_counts': dict(language_counts)
    }


def detect_frameworks(directory: Path) -> Dict[str, List[str]]:
    """Detect frameworks based on config files and imports."""
    frameworks = {
        'web': [],
        'testing': [],
        'build': [],
        'database': [],
        'security': []
    }

    # Check for package files
    package_json = directory / 'package.json'
    requirements_txt = directory / 'requirements.txt'
    pyproject_toml = directory / 'pyproject.toml'
    go_mod = directory / 'go.mod'
    cargo_toml = directory / 'Cargo.toml'
    gemfile = directory / 'Gemfile'
    composer_json = directory / 'composer.json'
    pom_xml = directory / 'pom.xml'
    build_gradle = directory / 'build.gradle'

    # JavaScript/TypeScript frameworks
    if package_json.exists():
        try:
            import json
            with open(package_json) as f:
                pkg = json.load(f)

            deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}

            # Web frameworks
            if 'react' in deps or 'react-dom' in deps:
                frameworks['web'].append('React')
            if 'next' in deps:
                frameworks['web'].append('Next.js')
            if 'vue' in deps:
                frameworks['web'].append('Vue')
            if 'nuxt' in deps:
                frameworks['web'].append('Nuxt')
            if 'angular' in deps or '@angular/core' in deps:
                frameworks['web'].append('Angular')
            if 'svelte' in deps:
                frameworks['web'].append('Svelte')
            if 'express' in deps:
                frameworks['web'].append('Express')
            if 'fastify' in deps:
                frameworks['web'].append('Fastify')
            if 'nestjs' in deps or '@nestjs/core' in deps:
                frameworks['web'].append('NestJS')
            if 'koa' in deps:
                frameworks['web'].append('Koa')
            if 'hapi' in deps or '@hapi/hapi' in deps:
                frameworks['web'].append('Hapi')

            # Testing frameworks
            if 'jest' in deps:
                frameworks['testing'].append('Jest')
            if 'vitest' in deps:
                frameworks['testing'].append('Vitest')
            if 'mocha' in deps:
                frameworks['testing'].append('Mocha')
            if 'cypress' in deps:
                frameworks['testing'].append('Cypress')
            if 'playwright' in deps:
                frameworks['testing'].append('Playwright')
            if '@testing-library/react' in deps:
                frameworks['testing'].append('React Testing Library')

            # Build tools
            if 'webpack' in deps:
                frameworks['build'].append('Webpack')
            if 'vite' in deps:
                frameworks['build'].append('Vite')
            if 'rollup' in deps:
                frameworks['build'].append('Rollup')
            if 'esbuild' in deps:
                frameworks['build'].append('esbuild')
            if 'parcel' in deps:
                frameworks['build'].append('Parcel')
            if 'turbo' in deps or 'turbo.json' in os.listdir(directory):
                frameworks['build'].append('Turborepo')

            # Database
            if 'prisma' in deps or '@prisma/client' in deps:
                frameworks['database'].append('Prisma')
            if 'mongoose' in deps:
                frameworks['database'].append('Mongoose')
            if 'sequelize' in deps:
                frameworks['database'].append('Sequelize')
            if 'typeorm' in deps:
                frameworks['database'].append('TypeORM')
            if 'drizzle-orm' in deps:
                frameworks['database'].append('Drizzle')
            if 'pg' in deps:
                frameworks['database'].append('PostgreSQL')

            # Security
            if 'helmet' in deps:
                frameworks['security'].append('Helmet')
            if 'cors' in deps:
                frameworks['security'].append('CORS')
            if 'bcrypt' in deps or 'bcryptjs' in deps:
                frameworks['security'].append('bcrypt')
            if 'jsonwebtoken' in deps:
                frameworks['security'].append('JWT')
            if 'passport' in deps:
                frameworks['security'].append('Passport')

        except Exception:
            pass

    # Python frameworks
    python_files = set()
    if requirements_txt.exists():
        try:
            with open(requirements_txt) as f:
                python_files = set(line.lower() for line in f if line.strip())
        except Exception:
            pass

    if pyproject_toml.exists():
        python_files.add('pyproject.toml')

    # Check for common Python framework indicators
    python_code_patterns = {
        'django': ['django', 'settings.py', 'urls.py'],
        'flask': ['flask'],
        'fastapi': ['fastapi'],
        'pytest': ['pytest', 'py.test'],
        'unittest': ['unittest'],
        'sqlalchemy': ['sqlalchemy'],
        'pandas': ['pandas'],
        'numpy': ['numpy'],
    }

    for framework, indicators in python_code_patterns.items():
        for indicator in indicators:
            if any(indicator in pf for pf in python_files):
                if framework in ['django', 'flask', 'fastapi']:
                    frameworks['web'].append(framework.capitalize())
                elif framework in ['pytest', 'unittest']:
                    frameworks['testing'].append(framework.capitalize() if framework == 'pytest' else 'unittest')
                elif framework in ['sqlalchemy']:
                    frameworks['database'].append('SQLAlchemy')
                break

    # Go frameworks
    if go_mod.exists():
        frameworks['build'].append('Go Modules')
        frameworks['testing'].append('go test')

    # Rust frameworks
    if cargo_toml.exists():
        frameworks['build'].append('Cargo')
        frameworks['testing'].append('cargo test')

    # Ruby frameworks
    if gemfile.exists():
        frameworks['build'].append('Bundler')
        try:
            with open(gemfile) as f:
                content = f.read().lower()
                if 'rails' in content:
                    frameworks['web'].append('Rails')
                if 'rspec' in content:
                    frameworks['testing'].append('RSpec')
                if 'minitest' in content:
                    frameworks['testing'].append('Minitest')
        except Exception:
            pass

    # Java frameworks
    if pom_xml.exists() or build_gradle.exists():
        frameworks['build'].append('Maven' if pom_xml.exists() else 'Gradle')
        frameworks['testing'].append('JUnit')

    return frameworks


def detect_security_tools(directory: Path) -> List[str]:
    """Detect security scanning tools in the project."""
    tools = []

    # Check for security config files
    security_indicators = {
        '.snyk': 'Snyk',
        '.github/workflows': 'GitHub Actions (security scans)',
        'security.md': 'Security Policy',
        '.gitguardian': 'GitGuardian',
        '.pre-commit-config.yaml': 'Pre-commit hooks',
    }

    for indicator, tool in security_indicators.items():
        if (directory / indicator).exists():
            tools.append(tool)

    # Check package.json for security tools
    package_json = directory / 'package.json'
    if package_json.exists():
        try:
            with open(package_json) as f:
                pkg = json.load(f)
            deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}

            if 'npm-audit' in str(deps) or 'audit' in str(deps):
                tools.append('npm audit')
            if 'snyk' in deps:
                tools.append('Snyk')
            if 'helmet' in deps:
                tools.append('Helmet (security headers)')
        except Exception:
            pass

    # Check requirements.txt for security tools
    requirements_txt = directory / 'requirements.txt'
    if requirements_txt.exists():
        try:
            with open(requirements_txt) as f:
                content = f.read().lower()
                if 'bandit' in content:
                    tools.append('Bandit')
                if 'safety' in content:
                    tools.append('Safety')
                if 'pip-audit' in content:
                    tools.append('pip-audit')
        except Exception:
            pass

    return tools


def analyze_directory(directory: Path) -> Dict[str, Any]:
    """Perform full stack analysis of a directory."""
    return {
        'languages': detect_languages(directory),
        'frameworks': detect_frameworks(directory),
        'security_tools': detect_security_tools(directory),
        'directory': str(directory)
    }


def main():
    if len(sys.argv) > 1:
        directory = Path(sys.argv[1])
    else:
        directory = Path.cwd()

    if not directory.exists():
        print(f"Error: Directory '{directory}' does not exist", file=sys.stderr)
        sys.exit(1)

    result = analyze_directory(directory)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
