# Sensor
GAME_WINDOW_TITLE = "Super Hexagon"
GAME_WINDOW_WITHOUT_MARGIN = (0, 32, 769, 519)
SCREEN_OFFSET: (int, int) = (-1980 + 50, 957)


EXPECTED_PLAYER_AREA_RADIUS = 85
EXPECTED_CENTER = (240, 383)
EXPECTED_PLAYER_AREA = (
    EXPECTED_CENTER[0] - EXPECTED_PLAYER_AREA_RADIUS,
    EXPECTED_CENTER[1] - EXPECTED_PLAYER_AREA_RADIUS,
    EXPECTED_CENTER[0] + EXPECTED_PLAYER_AREA_RADIUS,
    EXPECTED_CENTER[1] + EXPECTED_PLAYER_AREA_RADIUS,
)
PLAYER_MIN_SIZE = 25
PLAYER_MAX_SIZE = 72

MAX_PLAYER_LOST = 10

SCREENSHOT_LOGGER_LOGS_PATH = "logs"
SCREENSHOT_LOGGER_ENABLED = True
SCREENSHOT_LOGGER_IMAGE_NAME: None | str = None
SCREENSHOT_LOGGER_TRANSFORMATION_ENABLED = True
SCREENSHOT_LOGGER_ROLLING_IMAGE_AMOUNT = 50
SCREENSHOT_LOGGER_PLAYER_COLOR = (0, 255, 255)
SCREENSHOT_LOGGER_PLAYER_CICLE_COLOR = (255, 0, 255)
SCREENSHOT_LOGGER_RAYS_COLOR = (255, 0, 255)

SENSOR_RAY_AMOUNT = 48
SENSOR_BLUR_RATIO = 12
SENSOR_RAY_PIXEL_SKIP = 5
SENSOR_RAY_START_ITERATION = 16
SENSOR_RAY_MAX_ITERATION = 60
SENSOR_APPLY_BLUR = True

MOTOR_MIN_ROTATION = 0.025
# The distance moved around the circle in 1 second (in rad/pi)
MOTOR_SPEED = 2
MOTOR_MAX_SLEEP = 0.01

BRAIN_CATEGORIZING = 4
BRAIN_MINIMAL_SPACE = 110

# Loop
MOVEMENT_ENABLED = True
