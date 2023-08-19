# Sensor
GAME_WINDOW_TITLE = "Super Hexagon"
GAME_WINDOW_WITHOUT_MARGIN = (0, 32, 769, 519)
SCREEN_OFFSET: (int, int) = (-1980 + 50, 957)


EXPECTED_PLAYER_AREA_RADIUS = 90
EXPECTED_CENTER = (240, 383)
EXPECTED_PLAYER_AREA = (
    EXPECTED_CENTER[0] - EXPECTED_PLAYER_AREA_RADIUS,
    EXPECTED_CENTER[1] - EXPECTED_PLAYER_AREA_RADIUS,
    EXPECTED_CENTER[0] + EXPECTED_PLAYER_AREA_RADIUS,
    EXPECTED_CENTER[1] + EXPECTED_PLAYER_AREA_RADIUS,
)
PLAYER_MIN_SIZE = 15
PLAYER_MAX_SIZE = 72

MAX_PLAYER_LOST = 10

SCREENSHOT_LOGGER_LOGS_PATH = "logs"
SCREENSHOT_LOGGER_ENABLED = True
SCREENSHOT_LOGGER_IMAGE_NAME: None | str = None
SCREENSHOT_LOGGER_ROLLING_IMAGE_AMOUNT = 50
SCREENSHOT_LOGGER_EDIT_ENABLED = True
SCREENSHOT_EDIT_PLAYER_COLOR = (0, 255, 255)
SCREENSHOT_EDIT_RAYS_COLOR = (255, 0, 255)
SCREENSHOT_EDIT_UNSAFE_COLOR = (255, 255, 0)

SENSOR_RAY_AMOUNT = 48
SENSOR_BLUR_RATIO = 12
SENSOR_RAY_PIXEL_SKIP = 5
SENSOR_RAY_PLAYER_MARGIN = 5
SENSOR_RAY_MAX_ITERATION = 60
SENSOR_APPLY_BLUR = True
SENSOR_IMPOSSIBLE_WALL = -1

MOTOR_MIN_ROTATION = 0.04
# The distance moved around the circle in 1 second (in rad/pi)
MOTOR_SPEED = 3
MOTOR_LARGE_ROTATION = 0.3
MOTOR_SMALL_SLEEP = 0.01
MOTOR_LONG_SLEEP = MOTOR_LARGE_ROTATION / MOTOR_SPEED

BRAIN_CATEGORIZING = 4
BRAIN_MINIMAL_SPACE_OFFSET = 50
BRAIN_UNSAFE_SPACE_OFFSET = 80
BRAIN_SAFE_MARGIN = 20
BRAIN_REQUIRED_SAFE_SPACE = 3
BRAIN_REQUIRED_WALL = 2

# Loop
MOVEMENT_ENABLED = True
