# Sensor
GAME_WINDOW_TITLE = "Super Hexagon"
GAME_WINDOW_WITHOUT_MARGIN = (0, 32, 769, 519)
SCREEN_OFFSET: (int, int) = (-1980 + 50, 957)

EXPECTED_PLAYER_AREA = (155, 305, 325, 475)
EXPECTED_CENTER = (240, 383)
PLAYER_MIN_SIZE = 30
PLAYER_MAX_SIZE = 72

SCREENSHOT_LOGGER_LOGS_PATH = "logs"
SCREENSHOT_LOGGER_ENABLED = True
SCREENSHOT_LOGGER_IMAGE_NAME: None | str = None
SCREENSHOT_LOGGER_TRANSFORMATION_ENABLED = True
SCREENSHOT_LOGGER_ROLLING_IMAGE_AMOUNT = 50
SCREENSHOT_LOGGER_PLAYER_COLOR = (0, 255, 255)
SCREENSHOT_LOGGER_RAYS_COLOR = (255, 0, 255)

SENSOR_RAY_AMOUNT = 48
SENSOR_BLUR_RATIO = 12
SENSOR_RAY_PIXEL_SKIP = 5
SENSOR_RAY_START_ITERATION = 15
SENSOR_RAY_MAX_ITERATION = 70
SENSOR_APPLY_BLUR = True

MOTOR_MIN_ROTATION = 0.025
# The distance moved around the circle in 1 second (in rad/pi)
MOTOR_SPEED = 2
MOTOR_MAX_SLEEP = 0.01

BRAIN_CATEGORIZING = 4

# Loop
MOVEMENT_ENABLED = True
