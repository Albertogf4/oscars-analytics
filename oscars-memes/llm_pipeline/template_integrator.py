"""Template Integrator - Safely modifies pipeline files to add new templates."""

import ast
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from .template_agents.models import TemplateProcessingResult


class TemplateIntegrator:
    """Integrates processed templates into the pipeline files.

    Handles:
    - Adding to MEME_TEMPLATES in templates.py
    - Adding to TEMPLATE_SPECIFIC_PROMPTS in prompts.py
    - Adding Pydantic model to models.py
    - Adding generator function to meme_generator.py
    - Updating mappings in generator.py and pipeline.py
    """

    def __init__(
        self,
        llm_pipeline_dir: Optional[Path] = None,
        meme_generator_path: Optional[Path] = None,
        backup_dir: Optional[Path] = None,
    ):
        """Initialize the integrator.

        Args:
            llm_pipeline_dir: Path to llm_pipeline directory.
            meme_generator_path: Path to meme_generator.py.
            backup_dir: Directory for backups before modifications.
        """
        base_dir = Path(__file__).parent.parent
        self.llm_pipeline_dir = llm_pipeline_dir or base_dir / "llm_pipeline"
        self.meme_generator_path = meme_generator_path or base_dir / "meme_generator.py"
        self.backup_dir = backup_dir or base_dir / "backups"

        # File paths
        self.templates_path = self.llm_pipeline_dir / "templates.py"
        self.prompts_path = self.llm_pipeline_dir / "prompts.py"
        self.models_path = self.llm_pipeline_dir / "models.py"
        self.generator_path = self.llm_pipeline_dir / "generator.py"
        self.pipeline_path = self.llm_pipeline_dir / "pipeline.py"

    def create_backup(self, file_path: Path) -> Path:
        """Create a backup of a file before modification.

        Args:
            file_path: Path to the file to backup.

        Returns:
            Path to the backup file.
        """
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{file_path.stem}_{timestamp}{file_path.suffix}"
        shutil.copy2(file_path, backup_path)
        return backup_path

    def validate_python_syntax(self, code: str) -> bool:
        """Check if Python code is syntactically valid.

        Args:
            code: Python code string to validate.

        Returns:
            True if valid, False otherwise.
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def add_to_templates(self, result: TemplateProcessingResult) -> None:
        """Add new template to MEME_TEMPLATES in templates.py.

        Args:
            result: The processed template result.
        """
        self.create_backup(self.templates_path)

        content = self.templates_path.read_text()

        # Build the template entry
        entry = result.template_registry_entry
        template_str = f'''
    "{entry['id']}": {{
        "id": "{entry['id']}",
        "name": "{entry['name']}",
        "filename": "{entry['filename']}",
        "text_slots": {entry['text_slots']},
        "slot_names": {entry['slot_names']},
        "irony_type": "{entry['irony_type']}",
        "description": "{entry['description']}",
        "tone": "{entry['tone']}",
        "max_chars_per_slot": {entry['max_chars_per_slot']},
        "example": {entry['example']},
        "generator_function": "{entry['generator_function']}",
    }},
'''

        # Find the closing brace of MEME_TEMPLATES
        # Look for the pattern: last closing brace before helper functions
        pattern = r"(MEME_TEMPLATES\s*=\s*\{.*?)(^\})"
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

        if match:
            insert_pos = match.end(1)
            new_content = content[:insert_pos] + template_str + content[insert_pos:]

            if self.validate_python_syntax(new_content):
                self.templates_path.write_text(new_content)
            else:
                raise ValueError("Generated template entry creates invalid Python syntax")
        else:
            raise ValueError("Could not find MEME_TEMPLATES dict in templates.py")

    def add_to_prompts(self, result: TemplateProcessingResult) -> None:
        """Add new prompt to TEMPLATE_SPECIFIC_PROMPTS in prompts.py.

        Args:
            result: The processed template result.
        """
        self.create_backup(self.prompts_path)

        content = self.prompts_path.read_text()

        template_id = result.metadata.id
        prompt_text = result.prompt.template_prompt.replace('"""', '\\"\\"\\"')

        # Build the prompt entry
        prompt_str = f'''
    "{template_id}": """{result.prompt.template_prompt}""",
'''

        # Find the closing brace of TEMPLATE_SPECIFIC_PROMPTS
        pattern = r"(TEMPLATE_SPECIFIC_PROMPTS\s*=\s*\{.*?)(^\})"
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

        if match:
            insert_pos = match.end(1)
            new_content = content[:insert_pos] + prompt_str + content[insert_pos:]

            if self.validate_python_syntax(new_content):
                self.prompts_path.write_text(new_content)
            else:
                raise ValueError("Generated prompt entry creates invalid Python syntax")
        else:
            raise ValueError("Could not find TEMPLATE_SPECIFIC_PROMPTS dict in prompts.py")

    def add_to_models(self, result: TemplateProcessingResult) -> None:
        """Add new Pydantic model to models.py.

        Args:
            result: The processed template result.
        """
        self.create_backup(self.models_path)

        content = self.models_path.read_text()

        # Add the new model class before the batch generation section
        model_code = result.code.pydantic_model

        # Find the batch generation section marker
        marker = "# === Batch Generation Models ==="
        if marker in content:
            insert_pos = content.index(marker)
            new_content = content[:insert_pos] + f"\n{model_code}\n\n\n" + content[insert_pos:]

            if self.validate_python_syntax(new_content):
                self.models_path.write_text(new_content)
            else:
                raise ValueError("Generated Pydantic model creates invalid Python syntax")
        else:
            # Fallback: append to end of file
            new_content = content + f"\n\n{model_code}\n"
            if self.validate_python_syntax(new_content):
                self.models_path.write_text(new_content)
            else:
                raise ValueError("Generated Pydantic model creates invalid Python syntax")

    def add_to_meme_generator(self, result: TemplateProcessingResult) -> None:
        """Add new generator function to meme_generator.py.

        Args:
            result: The processed template result.
        """
        self.create_backup(self.meme_generator_path)

        content = self.meme_generator_path.read_text()

        # Add the new function before generate_all_memes
        function_code = result.code.generator_function

        marker = "def generate_all_memes():"
        if marker in content:
            insert_pos = content.index(marker)
            new_content = content[:insert_pos] + f"\n{function_code}\n\n\n" + content[insert_pos:]

            if self.validate_python_syntax(new_content):
                self.meme_generator_path.write_text(new_content)
            else:
                raise ValueError("Generated function creates invalid Python syntax")
        else:
            # Fallback: append to end of file before if __name__ block
            if_main = 'if __name__ == "__main__":'
            if if_main in content:
                insert_pos = content.index(if_main)
                new_content = content[:insert_pos] + f"\n{function_code}\n\n\n" + content[insert_pos:]
            else:
                new_content = content + f"\n\n{function_code}\n"

            if self.validate_python_syntax(new_content):
                self.meme_generator_path.write_text(new_content)
            else:
                raise ValueError("Generated function creates invalid Python syntax")

    def update_generator_mapping(self, result: TemplateProcessingResult) -> None:
        """Update TEMPLATE_GENERATORS in generator.py.

        Also adds the generator function to the import statement.

        Args:
            result: The processed template result.
        """
        if not self.generator_path.exists():
            return

        self.create_backup(self.generator_path)

        content = self.generator_path.read_text()

        # Build the entry
        entry = result.code.template_generators_entry

        # Extract the function name from the entry
        func_name = result.metadata.generator_function

        # First, add the import for the generator function
        # Find the meme_generator import block ending with OUTPUT_DIR,\n)
        import_pattern = r"(from meme_generator import \([^)]+)(OUTPUT_DIR,\n\))"
        import_match = re.search(import_pattern, content, re.DOTALL)

        if import_match:
            # Add the new function import before OUTPUT_DIR
            new_import_content = (
                content[:import_match.end(1)]
                + f"    {func_name},\n    "
                + content[import_match.start(2):]
            )
            content = new_import_content

        # Find TEMPLATE_GENERATORS dict
        pattern = r"(TEMPLATE_GENERATORS\s*=\s*\{.*?)(^\})"
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

        if match:
            insert_pos = match.end(1)
            new_content = content[:insert_pos] + f"    {entry}\n" + content[insert_pos:]

            if self.validate_python_syntax(new_content):
                self.generator_path.write_text(new_content)

    def update_pipeline_mapping(self, result: TemplateProcessingResult) -> None:
        """Update TEMPLATE_OUTPUT_MODELS in pipeline.py.

        Also adds the output model to the import statement.

        Args:
            result: The processed template result.
        """
        if not self.pipeline_path.exists():
            return

        self.create_backup(self.pipeline_path)

        content = self.pipeline_path.read_text()

        # Build the entry
        entry = result.code.output_models_entry

        # Extract the model name from the entry (e.g., '"stonked": StonkedOutput,' -> 'StonkedOutput')
        # Parse the output_models_entry to get the class name
        model_match = re.search(r':\s*(\w+Output)', entry)
        model_name = model_match.group(1) if model_match else None

        # First, add the import for the output model (if we could extract the name)
        if model_name:
            # Find the .models import block - look for the last model import before the closing )
            import_pattern = r"(from \.models import \([^)]+?)(\n\))"
            import_match = re.search(import_pattern, content, re.DOTALL)

            if import_match:
                # Add the new model import before the closing parenthesis
                new_import_content = (
                    content[:import_match.end(1)]
                    + f",\n    {model_name}"
                    + content[import_match.start(2):]
                )
                content = new_import_content

        # Find TEMPLATE_OUTPUT_MODELS dict
        pattern = r"(TEMPLATE_OUTPUT_MODELS\s*=\s*\{.*?)(^\})"
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

        if match:
            insert_pos = match.end(1)
            new_content = content[:insert_pos] + f"    {entry}\n" + content[insert_pos:]

            if self.validate_python_syntax(new_content):
                self.pipeline_path.write_text(new_content)

    def integrate(
        self,
        result: TemplateProcessingResult,
        copy_image: bool = True,
        template_dir: Optional[Path] = None,
    ) -> dict:
        """Integrate a processed template into all pipeline files.

        Args:
            result: The processed template result.
            copy_image: Whether to copy the template image to MemeTemplate dir.
            template_dir: Directory containing meme template images.

        Returns:
            Dict with integration status for each file.
        """
        status = {
            "templates.py": False,
            "prompts.py": False,
            "models.py": False,
            "meme_generator.py": False,
            "generator.py": False,
            "pipeline.py": False,
            "image_copy": False,
        }

        try:
            self.add_to_templates(result)
            status["templates.py"] = True
        except Exception as e:
            status["templates.py"] = str(e)

        try:
            self.add_to_prompts(result)
            status["prompts.py"] = True
        except Exception as e:
            status["prompts.py"] = str(e)

        try:
            self.add_to_models(result)
            status["models.py"] = True
        except Exception as e:
            status["models.py"] = str(e)

        try:
            self.add_to_meme_generator(result)
            status["meme_generator.py"] = True
        except Exception as e:
            status["meme_generator.py"] = str(e)

        try:
            self.update_generator_mapping(result)
            status["generator.py"] = True
        except Exception as e:
            status["generator.py"] = str(e)

        try:
            self.update_pipeline_mapping(result)
            status["pipeline.py"] = True
        except Exception as e:
            status["pipeline.py"] = str(e)

        return status

    def rollback(self, file_path: Path, backup_path: Path) -> None:
        """Restore a file from backup.

        Args:
            file_path: Path to the file to restore.
            backup_path: Path to the backup file.
        """
        if backup_path.exists():
            shutil.copy2(backup_path, file_path)
