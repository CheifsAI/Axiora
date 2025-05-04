# System Patterns

## Architecture Overview
Axiora follows a modular architecture with clear separation of concerns:

1. Core Components
   - Main Application (`Axiora.py`)
   - Database Manager (`DatabaseManager.py`)
   - Data Analyzer (`DataAnalyzer.py`)
   - Visualizer (`Visualizer.py`)

2. UI Components
   - Main Window (`main_ui.py`)
   - Custom Widgets (`widgets/`)
   - Theme System (`themes/`)
   - Login System (`uiEXT/login/`)

3. Data Processing
   - Time Series Forecasting (`time_series_forecaster.py`)
   - Data Analysis Functions (`Functions.py`)
   - Database Operations (`Axioradb.py`)

## Design Patterns
1. Model-View-Controller (MVC)
   - Model: Database and data processing
   - View: UI components and visualizations
   - Controller: Main application logic

2. Factory Pattern
   - Widget creation
   - Report generation
   - Theme management

3. Observer Pattern
   - UI updates
   - Data changes
   - Event handling

4. Strategy Pattern
   - Analysis algorithms
   - Visualization methods
   - Export formats

## Component Relationships
1. Data Flow
   ```
   User Input -> UI Layer -> Controller -> Model -> Database
   Database -> Model -> Controller -> UI Layer -> Visualization
   ```

2. Module Dependencies
   ```
   Axiora.py
   ├── DatabaseManager.py
   ├── DataAnalyzer.py
   ├── Visualizer.py
   └── UI Components
       ├── main_ui.py
       ├── widgets/
       └── themes/
   ```

## Key Technical Decisions
1. UI Framework
   - PySide6 for modern UI
   - Custom widgets for specialized functionality
   - Theme system for customization

2. Data Storage
   - SQLite for local storage
   - Structured data organization
   - Efficient querying

3. Analysis Engine
   - Python-based processing
   - Integration with ML libraries
   - Extensible analysis framework

4. Security
   - Secure authentication
   - Data encryption
   - Access control 