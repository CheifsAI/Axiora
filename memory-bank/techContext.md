# Technical Context

## Core Technologies
1. Python
   - Version: 3.x
   - Key libraries:
     - PySide6 (UI framework)
     - pandas (data analysis)
     - SQLAlchemy (database ORM)
     - matplotlib (visualization)
     - langchain (AI integration)

2. Database
   - SQLite (Axioradb)
   - SQLAlchemy ORM
   - Custom database manager

3. UI Framework
   - PySide6
   - Custom widgets
   - Theme system
   - Qt Designer for UI files

## Development Setup
1. Environment
   - Python virtual environment
   - Dependencies managed via requirements.txt
   - Development tools:
     - IDE: Cursor
     - Version control: Git
     - UI design: Qt Designer

2. Build Process
   - cx_Freeze for packaging
   - Custom setup.py
   - Resource compilation (resources.qrc)

3. Testing
   - Unit tests
   - UI testing
   - Data analysis validation
   - Performance testing

## Technical Constraints
1. Platform Support
   - Windows 10/11
   - High DPI support
   - Multi-monitor support

2. Performance
   - Large dataset handling
   - Real-time visualization
   - Efficient database operations

3. Security
   - User authentication
   - Data encryption
   - Access control

## Dependencies
1. Core Dependencies
   ```
   protobuf
   cx_Freeze
   langchain_core
   QT-PyQt-PySide-Custom-Widgets
   PySide6
   pandas
   langchain
   langchain_ollama
   markdown
   python-docx
   bcrypt
   passlib
   SQLAlchemy
   pygal
   openpyxl
   ```

2. Development Dependencies
   - Git
   - Qt Designer
   - Python development tools

3. Optional Dependencies
   - Additional visualization libraries
   - Machine learning frameworks
   - Export format libraries 