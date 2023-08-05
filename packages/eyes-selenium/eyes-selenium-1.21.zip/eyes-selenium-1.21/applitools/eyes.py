import uuid
from datetime import datetime

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

from applitools import logger, _viewport_size
from ._agent_connector import AgentConnector
from ._webdriver import EyesWebDriver
from ._match_window_task import MatchWindowTask
from ._triggers import TextTrigger, MouseTrigger
from applitools._webdriver import EyesFrame
from .errors import EyesError, NewTestError, TestFailedError
from .geometry import Region, EMPTY_REGION
from .test_results import TestResults
from .utils import general_utils
from applitools import VERSION


class FailureReports(object):
    """
    Failures are either reported immediately when they are detected, or when the test is closed.
    """
    IMMEDIATE = 0
    ON_CLOSE = 1


class MatchLevel(object):
    """
    The extent in which two images match (or are expected to match).
    """
    NONE = "None"
    LAYOUT = "Layout"
    CONTENT = "Content"
    STRICT = "Strict"
    EXACT = "Exact"


class BatchInfo(object):
    """
    A batch of tests.
    """

    def __init__(self, name=None, started_at=datetime.now(general_utils.UTC)):
        self.name = name
        self.started_at = started_at
        self.id = str(uuid.uuid4())

    def __getstate__(self):
        return dict(name=self.name, startedAt=self.started_at.isoformat(), id=self.id)

    # Required is required in order for jsonpickle to work on this object.
    # noinspection PyMethodMayBeStatic
    def __setstate__(self, state):
        raise EyesError('Cannot create BatchInfo instance from dict!')

    def __str__(self):
        return "%s - %s - %s" % (self.name, self.started_at, self.id)


class Eyes(object):
    """
    Applitools Selenium Eyes API for python.
    """
    _DEFAULT_MATCH_TIMEOUT = 2  # Seconds
    AGENT_ID = "Eyes.Selenium.Python/%s" % VERSION
    DEFAULT_EYES_SERVER = 'https://eyes.applitools.com'

    api_key = None

    def __init__(self, server_url=DEFAULT_EYES_SERVER, disabled=False):
        """
        Creates a new (possibly disabled) Eyes instance that interacts with the Eyes server.

        Args:
            params (dictionary):
                (Optional) server_url (str): The URL of the Eyes server
                (Optional) disabled (boolean): Whether this Eyes instance is disabled (acts as
                                                mock).
        """
        self._is_disabled = disabled
        if disabled:
            return
        self._user_inputs = []
        self._running_session = None
        self._agent_connector = AgentConnector(server_url, Eyes.AGENT_ID, Eyes.api_key)
        self._should_get_title = False
        self._driver = None
        self._match_window_task = None
        self._match_level = None
        self._is_open = False
        self._app_name = None
        self._failure_reports = None
        self._last_screenshot = None
        self._should_match_once_on_timeout = False
        self._start_info = None
        self._test_name = None
        self._viewport_size = None
        self.match_timeout = Eyes._DEFAULT_MATCH_TIMEOUT
        self.batch = None  # (BatchInfo)
        self.host_os = None  # (str)
        self.host_app = None  # (str)
        self.save_new_tests = True
        self.save_failed_tests = False
        self.branch_name = None
        self.parent_branch_name = None
        self.force_full_page_screenshot = False

    def is_open(self):
        """
        Returns:
            (boolean) True if a session is currently running, False otherwise.
        """
        return self._is_open

    def is_disabled(self):
        """
        Returns:
            (boolean) True if the current Eyes instance is disabled, False otherwise.
        """
        return self._is_disabled

    def get_driver(self):
        """
        Returns:
            (selenium.webdriver.remote.webdriver) The web driver currently used by the Eyes
                                                    instance.
        """
        return self._driver

    def get_match_level(self):
        """
        Returns:
            (match_level) The match level used for the current test (if running), or the next test.
        """
        return self._match_level

    def get_viewport_size(self):
        """
        Returns:
            ({width, height}) The size of the viewport of the application under test (e.g,
                                the browser).
        """
        return self._viewport_size

    def get_failure_reports(self):
        """
        Returns:
            (failure_reports) Whether the current test will report failure immediately or when it
                                is finished.
        """
        return self._failure_reports

    def abort_if_not_closed(self):
        """
        If a test is running, aborts it. Otherwise, does nothing.
        """
        if self.is_disabled():
            logger.debug('abort_if_not_closed(): ignored (disabled)')
            return

        self._reset_last_screenshot()

        if self._running_session:
            logger.debug('abort_if_not_closed(): Aborting session...')
            try:
                self._agent_connector.stop_session(self._running_session, True, False)
                logger.info('--- Test aborted.')
            except EyesError as e:
                logger.info("Failed to abort sever session: %s " % e)
                pass
            finally:
                self._running_session = None

    def open(self, driver, app_name, test_name, viewport_size=None,
             match_level=MatchLevel.EXACT, failure_reports=FailureReports.ON_CLOSE):
        """
        Starts a test.

        Args:
            params (dictionary):
                app_name (str): The name of the application under test.
                test_name (str): The test name.
                (Optional) viewport_size ({width, height}): The client's viewport size (i.e.,
                                                            the visible part of the document's
                                                            body) or None to allow any viewport
                                                            size.
                (Optional) match_level (match_level): Test-wide match level to use when comparing
                                                        the application outputs with expected
                                                        outputs.
                (Optional) failure_reports (failure_reports): Specifies how detected failures are
                                                                reported.
        Returns:
            An updated web driver
        Raises:
            EyesError
        """
        if self.is_disabled():
            logger.debug('open(): ignored (disabled)')
            return driver

        if Eyes.api_key is None:
            raise EyesError('API key is missing! Please set it via Eyes.api_key')

        if (driver is None) or (not isinstance(driver, RemoteWebDriver)):
            raise EyesError('driver must be a valid Selenium web driver object')

        logger.info("open(%s, %s, %s, %s)" % (app_name, test_name, viewport_size, failure_reports))

        self._driver = EyesWebDriver(driver, self)

        if self.is_open():
            self.abort_if_not_closed()
            raise EyesError('a test is already running')
        self._app_name = app_name
        self._test_name = test_name
        self._viewport_size = viewport_size
        self._failure_reports = failure_reports
        self._match_level = match_level
        self._is_open = True
        return self._driver

    def _assign_viewport_size(self):
        if self._viewport_size:
            _viewport_size.set_viewport_size(self._driver, self._viewport_size)
        else:
            self._viewport_size = _viewport_size.get_viewport_size(self._driver)

    def _create_start_info(self):
        app_env = {'os': self.host_os, 'hostingApp': self.host_app,
                   'displaySize': self._viewport_size,
                   'inferred': self._get_inferred_environment()}
        self._start_info = {'agentId': Eyes.AGENT_ID, 'appIdOrName': self._app_name,
                            'scenarioIdOrName': self._test_name, 'batchInfo': self.batch,
                            'environment': app_env, 'matchLevel': self._match_level,
                            'verId': None, 'branchName': self.branch_name,
                            'parentBranchName': self.parent_branch_name}

    def _start_session(self):
        self._assign_viewport_size()
        if not self.batch:
            self.batch = BatchInfo()
        self._create_start_info()
        logger.debug("start info: %s" % self._start_info)
        # Actually start the session.
        self._running_session = self._agent_connector.start_session(self._start_info)
        self._should_match_once_on_timeout = self._running_session['is_new_session']

    def get_title(self):
        """
        Returns:
            (str) The title of the window of the AUT, or empty string if the title is not
                    available.
        """
        if self._should_get_title:
            # noinspection PyBroadException
            try:
                return self._driver.title
            except:
                self._should_get_title = False
                # Couldn't get title, return empty string.
        return ''

    def _get_inferred_environment(self):
        try:
            user_agent = self._driver.execute_script('return navigator.userAgent')
        except WebDriverException:
            user_agent = None
        if user_agent:
            return "useragent:%s" % user_agent
        return None

    def _prepare_check(self):
        if not self.is_open():
            raise EyesError('Eyes not open!')

        if not self._running_session:
            self._start_session()
            self._match_window_task = MatchWindowTask(self, self._agent_connector,
                                                      self._running_session, self._driver,
                                                      self.match_timeout)

    def _handle_match_result(self, result, tag):
        self._last_screenshot = result['screenshot']
        as_expected = result['as_expected']
        self._user_inputs = []
        if not as_expected:
            self._should_match_once_on_timeout = True
            if not self._running_session['is_new_session']:
                logger.info("Window mismatch %s" % tag)
                if self._failure_reports == FailureReports.IMMEDIATE:
                    raise TestFailedError("Mismatch found in '%s' of '%s'" %
                                          (self._start_info['scenarioIdOrName'],
                                           self._start_info['appIdOrName']))

    def check_window(self, tag=None):
        """
        Takes a snapshot from the browser using the web driver and matches it with the expected
        output.
        """
        if self.is_disabled():
            logger.info("check_window(%s): ignored (disabled)" % tag)
            return
        logger.info("check_window('%s')" % tag)
        self._prepare_check()
        result = self._match_window_task.match_window(tag, self.force_full_page_screenshot,
                                                      self._user_inputs,
                                                      self._should_match_once_on_timeout)
        self._handle_match_result(result, tag)

    def check_region(self, region, tag=None):
        """
        Takes a snapshot of the given region from the browser using the web driver and matches it
        with the expected output. If the current context is a frame, the region is offsetted
        relative to the frame.
        """
        if self.is_disabled():
            logger.info('check_region(): ignored (disabled)')
            return
        logger.info("check_region([%s], '%s')" % (region, tag))
        if region.is_empty():
            raise EyesError("region cannot be empty!")
        self._prepare_check()
        result = self._match_window_task.match_region(region, tag, self.force_full_page_screenshot,
                                                      self._user_inputs,
                                                      self._should_match_once_on_timeout)
        self._handle_match_result(result, tag)

    def check_region_by_element(self, element, tag=None):
        """
        Takes a snapshot of the region of the given element from the browser using the web driver
        and matches it with the expected output.
        """
        if self.is_disabled():
            logger.info('check_region_by_element(): ignored (disabled)')
            return
        logger.info("check_region_by_element('%s')" % tag)
        self._prepare_check()
        result = self._match_window_task.match_element(element, tag,
                                                       self.force_full_page_screenshot,
                                                       self._user_inputs,
                                                       self._should_match_once_on_timeout)

        self._handle_match_result(result, tag)

    def check_region_by_selector(self, by, value, tag=None):
        """
        Takes a snapshot of the region of the element found by calling find_element(by, value)
        and matches it with the expected output.
        """
        if self.is_disabled():
            logger.info('check_region_by_selector(): ignored (disabled)')
            return
        self.check_region_by_element(self._driver.find_element(by, value), tag)

    def check_region_in_frame_by_selector(self, frame_reference, by, value, tag=None):
        """
        Checks a region within a frame, and returns to the current frame
        """
        # Switching to the relevant frame
        self._driver.switch_to.frame(frame_reference)
        self.check_region_by_selector(by, value, tag)
        # Switching back to our original frame
        self._driver.switch_to.parent_frame()

    def _reset_last_screenshot(self):
        self._last_screenshot = None
        self._user_inputs = []

    def close(self):
        if self.is_disabled():
            logger.debug('close(): ignored (disabled)')
            return

        self._is_open = False

        logger.debug('close()')

        self._reset_last_screenshot()
        self._user_inputs = []

        # If there's no running session, we simply return the default test results.
        if not self._running_session:
            logger.debug('close(): no session is running, returning empty results')
            return TestResults()

        results_url = self._running_session['session_url']
        is_new_session = self._running_session['is_new_session']
        should_save = (is_new_session and self.save_new_tests) or \
                      ((not is_new_session) and self.save_failed_tests)
        logger.debug("close(): automatically save session? %s" % should_save)
        logger.info('close(): Closing session...')
        results = self._agent_connector.stop_session(self._running_session, False, should_save)
        logger.info("close(): %s" % results)
        self._running_session = None
        if is_new_session:
            if should_save:
                instructions = 'Test was automatically accepted. You can review it at %s' % \
                               results_url
            else:
                instructions = "Please approve the new baseline at %s" % results_url
                logger.info("--- New test ended. %s" % instructions)
            message = "'%s' of '%s'. %s" % (self._start_info['scenarioIdOrName'],
                                            self._start_info['appIdOrName'], instructions)
            raise NewTestError(message, results)
        elif 0 < results.mismatches or 0 < results.missing:
            if should_save:
                instructions = "Test was automatically accepted. You can review it at %s" % \
                               results_url
            else:
                instructions = "Test failed. You can review it at %s" % results_url
                logger.info("--- Failed test ended. %s" % instructions)
            message = "'%s' of '%s'. %s" % (self._start_info['scenarioIdOrName'],
                                            self._start_info['appIdOrName'], instructions)
            raise TestFailedError(message, results)
        # Test passed
        logger.info('--- Test passed.')
        return results

    def add_mouse_trigger_by_element(self, action, element):
        """
        Adds a mouse trigger.
        Args:
            action: (string) Mouse action (click, double click etc.)
            element: (WebElement) The element on which the action was performed.
        """
        if self.is_disabled():
            logger.debug("add_mouse_trigger: Ignoring %s (disabled)" % action)
            return
        # Triggers are activated on the last checked window.
        if self._last_screenshot is None:
            logger.debug("add_mouse_trigger: Ignoring %s (no screenshot)" % action)
            return
        if not EyesFrame.is_same_frame_chain(self._driver.get_frame_chain(),
                                             self._last_screenshot.get_frame_chain()):
            logger.debug("add_mouse_trigger: Ignoring %s (invalid frame)" % action)
            return
        control = self._last_screenshot.get_intersected_region_by_element(element)
        # Making sure the trigger is within the last screenshot bounds
        if control.is_empty():
            logger.debug("add_mouse_trigger: Ignoring %s (out of bounds)" % action)
            return
        cursor = control.middle_offset
        trigger = MouseTrigger(action, control, cursor)
        self._user_inputs.append(trigger)
        logger.info("add_mouse_trigger: Added %s" % trigger)

    def add_text_trigger_by_element(self, element, text):
        """
        Adds a text trigger.
        Args:
            element: (WebElement) The element to which the text was sent.
            text: (str) The trigger's text.
        """
        if self.is_disabled():
            logger.debug("add_text_trigger: Ignoring '%s' (disabled)" % text)
            return
        # Triggers are activated on the last checked window.
        if self._last_screenshot is None:
            logger.debug("add_text_trigger: Ignoring '%s' (no screenshot)" % text)
            return
        if not EyesFrame.is_same_frame_chain(self._driver.get_frame_chain(),
                                             self._last_screenshot.get_frame_chain()):
            logger.debug("add_text_trigger: Ignoring %s (invalid frame)" % text)
            return
        control = self._last_screenshot.get_intersected_region_by_element(element)
        # Making sure the trigger is within the last screenshot bounds
        if control.is_empty():
            logger.debug("add_text_trigger: Ignoring %s (out of bounds)" % text)
            return
        trigger = TextTrigger(control, text)
        self._user_inputs.append(trigger)
        logger.info("add_text_trigger: Added %s" % trigger)
