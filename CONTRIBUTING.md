# Contributing to Sonar System

Thank you for your interest in contributing to Sonar System! 🎉

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - A clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, etc.)

### Suggesting Features

1. Open a new issue with the `enhancement` label
2. Describe the feature and its use case
3. Explain why it would be valuable

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests: `pytest`
5. Format code: `black sonar_system/`
6. Commit: `git commit -m "Add my feature"`
7. Push: `git push origin feature/my-feature`
8. Open a Pull Request

## Code Style

- Follow PEP 8 guidelines
- Use Black for formatting
- Add docstrings to functions and classes
- Write meaningful commit messages

## Adding New Radar Types

1. Create a new file in `sonar_system/radars/`
2. Extend `BaseRadar` class
3. Implement required methods
4. Register in `radars/__init__.py`

Example:

```python
from ..core.base_radar import BaseRadar

class MyRadar(BaseRadar):
    NAME = "My Radar"
    DESCRIPTION = "Description here"
    ICON = "🔮"
    
    def create_widget(self):
        # Your implementation
        pass
    
    def update_data(self, angle, distance):
        # Your implementation
        pass
    
    def clear(self):
        # Your implementation
        pass
```

## Questions?

Feel free to open an issue or reach out!
