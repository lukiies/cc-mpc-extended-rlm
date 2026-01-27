"""Tests for knowledge base structure and conventions.

These tests verify that knowledge bases follow the Enhanced RLM conventions
for any project type (Python, C#, TypeScript, Harbour/xBase, etc.).
"""

import pytest
from pathlib import Path
import re

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from enhanced_rlm.config import Config, KnowledgeBaseConfig, SearchConfig
from enhanced_rlm.search import KnowledgeSearch
from enhanced_rlm.chunker import Chunker


# Required scope header pattern
SCOPE_HEADER_PATTERN = re.compile(
    r"^#\s+Project Rules\s*-?\s*Scope Definition",
    re.IGNORECASE | re.MULTILINE
)

SCOPE_IMPORTANT_PATTERN = re.compile(
    r"\*\*IMPORTANT:.*These rules apply ONLY when",
    re.IGNORECASE | re.DOTALL
)


class TestScopeHeader:
    """Tests for CLAUDE.md scope header requirement."""

    def test_valid_scope_header(self, tmp_path):
        """Test that a proper scope header is recognized."""
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("""# Project Rules - Scope Definition

**IMPORTANT: These rules apply ONLY when the user's question or task relates to:**
- Files in this workspace (Test Project codebase)
- Code in the test-project repository
- Development tasks for Test Project
- Python, or project-specific patterns
- Test automation

**These rules DO NOT apply to general questions unrelated to this project.**

---

## Build Commands

```bash
pytest
```
""")

        content = claude_md.read_text()
        assert SCOPE_HEADER_PATTERN.search(content) is not None
        assert SCOPE_IMPORTANT_PATTERN.search(content) is not None

    def test_missing_scope_header(self, tmp_path):
        """Test detection of missing scope header."""
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("""# Test Project - Rules

## Build Commands

```bash
pytest
```
""")

        content = claude_md.read_text()
        assert SCOPE_HEADER_PATTERN.search(content) is None

    def test_scope_header_variations(self, tmp_path):
        """Test that scope header variations are accepted."""
        valid_headers = [
            "# Project Rules - Scope Definition",
            "# Project Rules-Scope Definition",
            "# Project Rules  -  Scope Definition",
            "#  Project Rules - Scope Definition",
        ]

        for header in valid_headers:
            assert SCOPE_HEADER_PATTERN.search(header) is not None, f"Should match: {header}"


class TestCodeExamplesStructure:
    """Tests for code_examples folder organization."""

    def test_language_subfolders_structure(self, tmp_path):
        """Test that code_examples uses language-specific subfolders."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        code_examples = claude_dir / "code_examples"
        code_examples.mkdir()

        # Create language-specific subfolders
        (code_examples / "python").mkdir()
        (code_examples / "csharp").mkdir()
        (code_examples / "typescript").mkdir()

        # Add example files
        (code_examples / "python" / "api_patterns.py").write_text("# Python example")
        (code_examples / "csharp" / "db_patterns.cs").write_text("// C# example")
        (code_examples / "typescript" / "api_client.ts").write_text("// TypeScript example")

        # Verify structure
        assert (code_examples / "python").is_dir()
        assert (code_examples / "csharp").is_dir()
        assert (code_examples / "typescript").is_dir()
        assert (code_examples / "python" / "api_patterns.py").exists()
        assert (code_examples / "csharp" / "db_patterns.cs").exists()
        assert (code_examples / "typescript" / "api_client.ts").exists()

    def test_flat_structure_detected(self, tmp_path):
        """Test that flat code_examples structure is detectable."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        code_examples = claude_dir / "code_examples"
        code_examples.mkdir()

        # Create files directly (not recommended)
        (code_examples / "example.py").write_text("# Python")
        (code_examples / "example.cs").write_text("// C#")

        # Check if any files are directly in code_examples (not in subfolders)
        direct_files = [f for f in code_examples.iterdir() if f.is_file()]
        subdirs = [d for d in code_examples.iterdir() if d.is_dir()]

        # This would indicate flat structure (not recommended)
        assert len(direct_files) > 0  # Files exist directly
        assert len(subdirs) == 0  # No subdirectories


class TestMultiProjectTypes:
    """Tests for different project type support."""

    @pytest.fixture
    def create_project(self, tmp_path):
        """Factory to create test projects."""
        def _create(project_type: str, tech_stack: str):
            # Create CLAUDE.md with proper scope header
            claude_md = tmp_path / "CLAUDE.md"
            claude_md.write_text(f"""# Project Rules - Scope Definition

**IMPORTANT: These rules apply ONLY when the user's question or task relates to:**
- Files in this workspace ({project_type} codebase)
- Code in the {project_type.lower().replace(' ', '-')} repository
- Development tasks for {project_type}
- {tech_stack}, or project-specific patterns

**These rules DO NOT apply to general questions unrelated to this project.**

---

## Build Commands

Build the project using standard tooling.

## Key Rules

1. Follow coding conventions
2. Write tests for new features
3. Document changes
""")

            # Create .claude folder
            claude_dir = tmp_path / ".claude"
            claude_dir.mkdir(exist_ok=True)

            (claude_dir / "REFERENCE.md").write_text(f"""# {project_type} Reference

## Architecture

This document describes the {project_type} architecture.

## Code Conventions

Follow {tech_stack} best practices.
""")

            return tmp_path

        return _create

    def test_dotnet_project(self, create_project):
        """Test .NET/C# project structure."""
        project_path = create_project("eFakt2", "ASP.NET Core, React/TypeScript")

        config = Config(
            workspace_path=project_path,
            knowledge_base=KnowledgeBaseConfig(),
            search=SearchConfig(),
        )

        assert config.has_knowledge_base()
        assert config.root_file_path.exists()

        content = config.root_file_path.read_text()
        assert "ASP.NET Core" in content
        assert "eFakt2" in content

    def test_harbour_project(self, create_project):
        """Test Harbour/xBase project structure."""
        project_path = create_project("SoftWork Professional", "ITK-Clip/Harbour, Sybase")

        config = Config(
            workspace_path=project_path,
            knowledge_base=KnowledgeBaseConfig(),
            search=SearchConfig(),
        )

        assert config.has_knowledge_base()

        content = config.root_file_path.read_text()
        assert "ITK-Clip/Harbour" in content
        assert "SoftWork Professional" in content

    def test_python_project(self, create_project):
        """Test Python project structure."""
        project_path = create_project("DataProcessor", "Python, pandas, FastAPI")

        config = Config(
            workspace_path=project_path,
            knowledge_base=KnowledgeBaseConfig(),
            search=SearchConfig(),
        )

        assert config.has_knowledge_base()

        content = config.root_file_path.read_text()
        assert "Python" in content
        assert "DataProcessor" in content

    def test_typescript_project(self, create_project):
        """Test TypeScript/Node.js project structure."""
        project_path = create_project("WebApp", "TypeScript, React, Node.js")

        config = Config(
            workspace_path=project_path,
            knowledge_base=KnowledgeBaseConfig(),
            search=SearchConfig(),
        )

        assert config.has_knowledge_base()

        content = config.root_file_path.read_text()
        assert "TypeScript" in content
        assert "WebApp" in content


class TestSearchAcrossProjectTypes:
    """Tests for search functionality across different project types."""

    @pytest.fixture
    def multi_lang_knowledge_base(self, tmp_path):
        """Create a knowledge base with multiple language examples."""
        # CLAUDE.md
        claude_md = tmp_path / "CLAUDE.md"
        claude_md.write_text("""# Project Rules - Scope Definition

**IMPORTANT: These rules apply ONLY when the user's question or task relates to:**
- Files in this workspace (Multi-Lang Project codebase)
- Development tasks for Multi-Lang Project
- C#, TypeScript, Python patterns

**These rules DO NOT apply to general questions unrelated to this project.**

---

## Build Commands

Build: `dotnet build && npm run build`

## Key Rules

1. Never hardcode URLs
2. All tests must pass
3. Use dependency injection
""")

        # .claude folder
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()

        # REFERENCE.md
        (claude_dir / "REFERENCE.md").write_text("""# Reference Documentation

## API Patterns

Use the centralized API client for all HTTP calls.

## Database Patterns

Use Entity Framework Core for database access.
Use prepared statements to prevent SQL injection.

## Testing

All tests must pass before deployment.
Run tests with: `dotnet test && npm test`
""")

        # Code examples with language subfolders
        code_examples = claude_dir / "code_examples"
        code_examples.mkdir()

        (code_examples / "csharp").mkdir()
        (code_examples / "csharp" / "db_patterns.cs").write_text("""// Database Patterns
// Use dependency injection for DbContext

public class InvoiceService
{
    private readonly AppDbContext _db;

    public InvoiceService(AppDbContext db)
    {
        _db = db;
    }

    public async Task<Invoice> GetById(int id)
    {
        return await _db.Invoices.FindAsync(id);
    }
}
""")

        (code_examples / "typescript").mkdir()
        (code_examples / "typescript" / "api_client.ts").write_text("""// API Client Patterns
// ALWAYS use the centralized api module

import { api } from '../api';

export const invoiceAPI = {
    getAll: () => api.get('/invoices'),
    getById: (id: number) => api.get(`/invoices/${id}`),
    create: (data: Invoice) => api.post('/invoices', data),
};

// WRONG: Never hardcode URLs!
// const response = await axios.get('http://localhost:5000/invoices');
""")

        (code_examples / "python").mkdir()
        (code_examples / "python" / "test_patterns.py").write_text("""# Test Patterns
# All tests must pass before deployment

import pytest

class TestInvoiceService:
    def test_create_invoice(self, db_session):
        '''Test invoice creation.'''
        service = InvoiceService(db_session)
        invoice = service.create({"amount": 100})
        assert invoice.id is not None
        assert invoice.amount == 100
""")

        return tmp_path

    def test_search_finds_csharp_patterns(self, multi_lang_knowledge_base):
        """Test that search finds C# patterns."""
        config = Config(
            workspace_path=multi_lang_knowledge_base,
            knowledge_base=KnowledgeBaseConfig(),
            search=SearchConfig(max_results=50),
        )

        search = KnowledgeSearch(config)
        results = search.search("database dependency injection")

        assert len(results) > 0
        file_names = [str(r.file_path) for r in results]
        assert any("db_patterns.cs" in f or "REFERENCE.md" in f for f in file_names)

    def test_search_finds_typescript_patterns(self, multi_lang_knowledge_base):
        """Test that search finds TypeScript patterns."""
        config = Config(
            workspace_path=multi_lang_knowledge_base,
            knowledge_base=KnowledgeBaseConfig(),
            search=SearchConfig(max_results=50),
        )

        search = KnowledgeSearch(config)
        results = search.search("API client centralized")

        assert len(results) > 0
        file_names = [str(r.file_path) for r in results]
        assert any("api_client.ts" in f for f in file_names)

    def test_search_finds_test_patterns(self, multi_lang_knowledge_base):
        """Test that search finds test patterns across languages."""
        config = Config(
            workspace_path=multi_lang_knowledge_base,
            knowledge_base=KnowledgeBaseConfig(),
            search=SearchConfig(max_results=50),
        )

        search = KnowledgeSearch(config)
        results = search.search("tests must pass deployment")

        assert len(results) > 0
        # Should find content in multiple files
        file_names = [str(r.file_path) for r in results]
        assert any("REFERENCE.md" in f or "CLAUDE.md" in f or "test_patterns.py" in f for f in file_names)


class TestChunkerMultipleLanguages:
    """Tests for chunker with different file types."""

    def test_chunk_csharp_file(self, tmp_path):
        """Test chunking of C# files."""
        cs_file = tmp_path / "test.cs"
        cs_file.write_text("""using System;

public class InvoiceService
{
    public void CreateInvoice()
    {
        // Create logic
    }

    public void DeleteInvoice()
    {
        // Delete logic
    }
}
""")

        chunker = Chunker()
        chunks = chunker.chunk_file(cs_file)

        # C files use C pattern (similar structure)
        assert len(chunks) >= 1

    def test_chunk_typescript_file(self, tmp_path):
        """Test chunking of TypeScript files."""
        ts_file = tmp_path / "test.ts"
        ts_file.write_text("""export function createInvoice(data: Invoice): Invoice {
    return { ...data, id: generateId() };
}

export function deleteInvoice(id: number): void {
    // Delete logic
}

export class InvoiceService {
    async getAll(): Promise<Invoice[]> {
        return [];
    }
}
""")

        chunker = Chunker()
        chunks = chunker.chunk_file(ts_file)

        # Should return at least one chunk
        assert len(chunks) >= 1

    def test_chunk_python_file(self, tmp_path):
        """Test chunking of Python files."""
        py_file = tmp_path / "test.py"
        py_file.write_text("""def create_invoice(data: dict) -> dict:
    '''Create a new invoice.'''
    return {"id": generate_id(), **data}


def delete_invoice(invoice_id: int) -> None:
    '''Delete an invoice.'''
    pass


async def get_all_invoices() -> list:
    '''Get all invoices.'''
    return []
""")

        chunker = Chunker()
        chunks = chunker.chunk_file(py_file)

        # Should chunk by function
        assert len(chunks) >= 2

        # Check function names in headers
        headers = [c.header for c in chunks if c.header]
        assert any("create_invoice" in h for h in headers)
        assert any("delete_invoice" in h for h in headers)

    def test_chunk_prg_file(self, tmp_path):
        """Test chunking of Harbour/xBase PRG files."""
        prg_file = tmp_path / "test.prg"
        prg_file.write_text("""// Invoice module
#include "common.ch"

function CreateInvoice(cCustomer, nAmount)
local oInvoice
oInvoice := Invoice():New()
oInvoice:Customer := cCustomer
oInvoice:Amount := nAmount
return oInvoice

static function ValidateAmount(nAmount)
if nAmount <= 0
    return .F.
endif
return .T.
""")

        chunker = Chunker()
        chunks = chunker.chunk_file(prg_file)

        # Should chunk by function
        assert len(chunks) >= 2

        # Check function names in headers
        headers = [c.header for c in chunks if c.header]
        assert any("CreateInvoice" in h for h in headers)
        assert any("ValidateAmount" in h for h in headers)
