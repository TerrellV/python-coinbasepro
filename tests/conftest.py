import logging
import pytest
import time

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
TEST_PAUSE_TIME = 0.33


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    """Fixture to execute asserts before and after a test is run"""
    # Setup:

    yield  # this is where the testing happens

    # Teardown
    time.sleep(TEST_PAUSE_TIME)
