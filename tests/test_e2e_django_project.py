"""E2E test that verifies django-model-changes works in a fresh Django project.

Creates a real Django project using django-admin startproject, adds a model
that uses ChangesMixin, and verifies the change tracking functionality works.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def test_fresh_django_project():
    """Create a fresh Django project and verify django-model-changes works."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)
        project_name = "testproject"

        # Create Django project using django-admin (same pattern as djb e2e tests)
        result = subprocess.run(
            ["django-admin", "startproject", project_name, str(project_dir)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"django-admin startproject failed: {result.stderr}")

        # Create a test app
        result = subprocess.run(
            ["django-admin", "startapp", "testapp"],
            cwd=project_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"django-admin startapp failed: {result.stderr}")

        # Write a model that uses ChangesMixin
        models_py = project_dir / "testapp" / "models.py"
        models_py.write_text(
            """\
from django.db import models

from django_model_changes import ChangesMixin


class TestModel(ChangesMixin, models.Model):
    name = models.CharField(max_length=100)
    value = models.IntegerField(default=0)

    class Meta:
        app_label = "testapp"
"""
        )

        # Update settings to include testapp
        settings_py = project_dir / project_name / "settings.py"
        settings_content = settings_py.read_text()
        settings_content = settings_content.replace(
            "INSTALLED_APPS = [",
            "INSTALLED_APPS = [\n    'testapp',",
        )
        settings_py.write_text(settings_content)

        # Write a test script that exercises ChangesMixin
        test_script = project_dir / "test_changes.py"
        test_script.write_text(
            f"""\
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{project_name}.settings")
sys.path.insert(0, "{project_dir}")

import django
django.setup()

from django.db import connection
from testapp.models import TestModel

# Create the table
with connection.schema_editor() as schema_editor:
    schema_editor.create_model(TestModel)

# Test ChangesMixin functionality
obj = TestModel(name="test", value=1)
assert obj.changes() == {{}}, f"New instance should have no changes, got {{obj.changes()}}"

obj.name = "changed"
changes = obj.changes()
assert "name" in changes, f"Should detect name change, got {{changes}}"
assert changes["name"] == ("test", "changed"), f"Wrong change values: {{changes}}"

obj.save()
assert obj.changes() == {{}}, f"After save should have no changes, got {{obj.changes()}}"
assert obj.previous_changes() != {{}}, "Should have previous_changes after save"

print("All ChangesMixin tests passed!")
"""
        )

        # Run the test script with a clean environment (no inherited DJANGO_SETTINGS_MODULE)
        env = {k: v for k, v in os.environ.items() if k != "DJANGO_SETTINGS_MODULE"}
        result = subprocess.run(
            [sys.executable, str(test_script)],
            cwd=project_dir,
            capture_output=True,
            text=True,
            env=env,
        )

        if result.returncode != 0:
            raise AssertionError(
                f"E2E test failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
            )
