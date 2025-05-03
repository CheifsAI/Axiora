class Settings():
    # APP SETTINGS
    # ///////////////////////////////////////////////////////////////
    ENABLE_CUSTOM_TITLE_BAR = True
    MENU_WIDTH = 240
    LEFT_BOX_WIDTH = 240
    RIGHT_BOX_WIDTH = 240
    TIME_ANIMATION = 300  # Reduced from 500 for snappier animations
    
    # Enable hardware acceleration
    ENABLE_HARDWARE_ACCELERATION = True
    
    # Optimize rendering
    ENABLE_SMOOTH_SCROLLING = True
    ENABLE_ANIMATIONS = True  # Can be toggled for low-end devices
    
    # Cache settings
    ENABLE_CACHING = True
    MAX_CACHE_SIZE = 100  # Maximum number of items to cache
    
    # Performance settings
    BATCH_SIZE = 100  # For loading data in chunks
    LAZY_LOAD_THRESHOLD = 1000  # Row count threshold for lazy loading
    
    # BTNS LEFT AND RIGHT BOX COLORS
    BTN_LEFT_BOX_COLOR = "background-color: rgb(44, 49, 58);"
    BTN_RIGHT_BOX_COLOR = "background-color: rgb(44, 49, 58);"

    # MENU SELECTED STYLESHEET
    MENU_SELECTED_STYLESHEET = """
    border-left: 22px solid qlineargradient(spread:pad, x1:0.034, y1:0, x2:0.216, y2:0, stop:0.499 rgba(255, 121, 198, 255), stop:0.5 rgba(85, 170, 255, 0));
    background-color: rgb(40, 44, 52);
    """

    # Default paths with forward slashes
    ICONS_PATH = "images/icons/"
    IMAGES_PATH = "images/images/"
