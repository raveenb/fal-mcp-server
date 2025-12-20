"""Tests for documentation site"""

import os
import re

import yaml


def test_docs_directory_exists():
    """Test that docs directory exists"""
    assert os.path.exists("docs")
    assert os.path.isdir("docs")


def test_jekyll_config_exists():
    """Test that Jekyll configuration exists"""
    config_path = "docs/_config.yml"
    assert os.path.exists(config_path)

    # Validate YAML syntax
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        assert config is not None
        assert "title" in config
        assert "description" in config
        assert "url" in config
        assert "baseurl" in config


def test_required_pages_exist():
    """Test that all required pages exist"""
    required_pages = [
        "docs/index.md",
        "docs/installation.md",
        "docs/api.md",
        "docs/examples.md",
    ]

    for page in required_pages:
        assert os.path.exists(page), f"Required page {page} does not exist"


def test_gemfile_exists():
    """Test that Gemfile exists for Jekyll dependencies"""
    gemfile_path = "docs/Gemfile"
    assert os.path.exists(gemfile_path)

    with open(gemfile_path, "r") as f:
        content = f.read()
        # Check for required gems
        assert "jekyll" in content
        assert "jekyll-sitemap" in content
        assert "jekyll-seo-tag" in content
        assert "jekyll-feed" in content


def test_github_pages_workflow():
    """Test that GitHub Pages workflow exists and is valid"""
    workflow_path = ".github/workflows/pages.yml"
    assert os.path.exists(workflow_path)

    with open(workflow_path, "r") as f:
        workflow = yaml.safe_load(f)
        assert workflow is not None
        assert "name" in workflow
        # 'on' is a reserved word in YAML, it gets parsed as True
        assert True in workflow or "on" in workflow
        assert "jobs" in workflow
        assert "build" in workflow["jobs"]
        assert "deploy" in workflow["jobs"]


def test_seo_files_exist():
    """Test that SEO files exist"""
    seo_files = [
        "docs/robots.txt",
        "docs/_includes/seo.html",
    ]

    for file in seo_files:
        assert os.path.exists(file), f"SEO file {file} does not exist"


def test_robots_txt_valid():
    """Test that robots.txt is properly formatted"""
    with open("docs/robots.txt", "r") as f:
        content = f.read()
        # Check for required directives
        assert "User-agent:" in content
        assert "Allow:" in content
        assert "Sitemap:" in content
        assert "fal-mcp-server/sitemap.xml" in content


def test_page_front_matter():
    """Test that all markdown pages have proper front matter"""
    pages = [
        "docs/index.md",
        "docs/installation.md",
        "docs/api.md",
        "docs/examples.md",
    ]

    front_matter_regex = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL | re.MULTILINE)

    for page in pages:
        with open(page, "r") as f:
            content = f.read()

            # Check for front matter
            match = front_matter_regex.match(content)
            assert match is not None, f"Page {page} missing front matter"

            # Parse front matter
            front_matter = yaml.safe_load(match.group(1))

            # Check required fields
            assert "title" in front_matter, f"Page {page} missing title"
            assert "description" in front_matter, f"Page {page} missing description"

            # SEO checks
            assert (
                len(front_matter["description"]) > 50
            ), f"Page {page} description too short for SEO"
            assert (
                len(front_matter["description"]) <= 160
            ), f"Page {page} description too long for SEO"


def test_structured_data_valid():
    """Test that structured data in SEO include is valid JSON-LD"""
    seo_path = "docs/_includes/seo.html"

    with open(seo_path, "r") as f:
        content = f.read()

        # Extract JSON-LD scripts
        json_ld_regex = re.compile(
            r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL
        )
        matches = json_ld_regex.findall(content)

        assert len(matches) > 0, "No JSON-LD structured data found"

        # Note: We can't fully validate the JSON because it contains Liquid template tags
        # But we can check for required schema.org properties
        for json_content in matches:
            assert '"@context"' in json_content
            assert '"@type"' in json_content
            assert "schema.org" in json_content


def test_api_documentation_complete():
    """Test that API documentation covers all tools"""
    with open("docs/api.md", "r") as f:
        content = f.read()

        # Check for all three main tools
        assert "generate_image" in content
        assert "generate_video" in content
        assert "generate_music" in content

        # Check for parameter documentation
        assert "Parameters" in content
        assert "Required" in content
        assert "Default" in content

        # Check for examples
        assert "Example Usage" in content
        assert "Response" in content


def test_installation_guide_complete():
    """Test that installation guide covers all methods"""
    with open("docs/installation.md", "r") as f:
        content = f.read()

        # Check installation methods
        assert "pip install" in content
        assert "docker" in content.lower()
        assert "from source" in content.lower()

        # Check configuration sections
        assert "Claude Desktop" in content
        assert "FAL_KEY" in content
        assert "claude_desktop_config.json" in content

        # Check transport modes
        assert "STDIO" in content
        assert "HTTP" in content
        assert "SSE" in content


def test_examples_page_has_code():
    """Test that examples page contains actual code examples"""
    with open("docs/examples.md", "r") as f:
        content = f.read()

        # Check for code blocks
        assert "```" in content, "No code blocks found in examples"

        # Check for different types of examples
        assert "image" in content.lower()
        assert "video" in content.lower()
        assert "music" in content.lower() or "audio" in content.lower()

        # Check for prompts
        assert "prompt" in content.lower()


def test_internal_links():
    """Test that internal links use proper Jekyll/Liquid syntax"""
    pages = [
        "docs/index.md",
        "docs/installation.md",
        "docs/api.md",
        "docs/examples.md",
    ]

    # Pattern for Jekyll relative URLs
    jekyll_link_pattern = re.compile(r"{{\s*['\"]/(.*?)['\"].*?\|\s*relative_url\s*}}")

    for page in pages:
        with open(page, "r") as f:
            content = f.read()

            # Check if page has navigation links
            if "nav-buttons" in content or "→" in content:
                # Should use Jekyll relative_url filter for internal links
                links = jekyll_link_pattern.findall(content)
                assert (
                    len(links) > 0 or "github.com" in content
                ), f"Page {page} should have proper internal links"


def test_assets_directory_structure():
    """Test that assets directory has proper structure"""
    assert os.path.exists("docs/assets")
    assert os.path.exists("docs/assets/main.scss")  # Main stylesheet for minima theme
    assert os.path.exists("docs/assets/js")
    assert os.path.exists("docs/assets/img")


def test_keywords_in_pages():
    """Test that pages have SEO keywords"""
    pages = [
        "docs/index.md",
        "docs/installation.md",
        "docs/api.md",
        "docs/examples.md",
    ]

    important_keywords = ["MCP", "Fal", "Claude", "AI", "generation"]

    for page in pages:
        with open(page, "r") as f:
            content = f.read().lower()

            # Check for presence of important keywords
            keyword_count = sum(
                1 for keyword in important_keywords if keyword.lower() in content
            )
            assert keyword_count >= 3, f"Page {page} lacks important keywords for SEO"


def test_mobile_responsive_meta():
    """Test that mobile responsive viewport meta would be included"""
    # This would typically be in a layout file, but we can check config
    with open("docs/_config.yml", "r") as f:
        config = yaml.safe_load(f)
        # Jekyll's minima theme includes mobile viewport by default
        assert config.get("theme") == "minima" or "viewport" in str(config)
