import base64
from io import BytesIO
import time

import requests
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By

from applitools import logger, _viewport_size
from applitools.errors import EyesError, OutOfBoundsError
from applitools.geometry import Point
from applitools.utils import _image_utils
from .geometry import Region
from .utils import general_utils


class _ScreenshotTaker(object):
    """
    A wrapper class for taking screenshots from a remote web driver.
    """

    def __init__(self, driver_server_uri, driver_session_id):
        self._endpoint_uri = "%s/session/%s/screenshot" % (driver_server_uri.rstrip('/'),
                                                           driver_session_id)

    def get_screenshot_as_base64(self):
        """
        Returns a base64 encoded screenshot from the web driver.
        """
        response = requests.get(self._endpoint_uri)
        response.raise_for_status()
        return response.json()['value']


class EyesScreenshot(object):
    @staticmethod
    def create_from_base64(screenshot64, driver, location=None):
        """
        Creates an instance from the base64 data.
        Args:
            screenshot64: (str) The base64 representation of the png bytes.
            driver: (EyesWebDriver) The webdriver for the session.
            (Optional) location: (Point) The location of the image represented by the screenshot
                                 in the current frame.
        """
        return EyesScreenshot(driver, screenshot64=screenshot64,
                              frame_location_in_screenshot=location)

    @staticmethod
    def create_from_image(screenshot, driver, location=None):
        """
        Creates an instance from the base64 data.
        Args:
            screenshot: (PngImage) The screenshot image.
            driver: (EyesWebDriver) The webdriver for the session.
            (Optional) location: (Point) The location of the image represented by the screenshot
                                 in the current frame.
        """
        return EyesScreenshot(driver, screenshot=screenshot, frame_location_in_screenshot=location)

    def __init__(self, driver, screenshot=None, screenshot64=None,
                 is_viewport_screenshot=None, frame_location_in_screenshot=None):
        """
        Initializes a Screenshot instance. Either screenshot or screenshot64 must NOT be None.
        Should not be used directly. Use create_from_image/create_from_base64 instead.

        Args:
            driver: EyesWebDriver instance which handles the session from which the screenshot
                    was retrieved.
            (Optional) screenshot: (PngImage) image instance. If screenshot64 is None,
                                    this variable must NOT be none.
            (Optional) screenshot64: (str) The base64 representation of a png image. If screenshot
                                     is None, this variable must NOT be none.
            (Optional) frame_location_in_screenshot: (Point) The location of the frame relative
                                                    to the top,left of the screenshot.
            (Optional) is_viewport_screenshot: (boolean) Whether the screenshot object represents a
                                                viewport screenshot or a full screenshot.
        """
        self._screenshot64 = screenshot64
        if screenshot:
            self._screenshot = screenshot
        elif screenshot64:
            self._screenshot = _image_utils.png_image_from_bytes(base64.b64decode(screenshot64))
        else:
            raise EyesError("both screenshot and screenshot64 are None!")
        self._driver = driver
        self._viewport_size = driver.get_default_content_viewport_size()

        self._frame_chain = driver.get_frame_chain()
        if self._frame_chain:
            chain_len = len(self._frame_chain)
            self._frame_size = self._frame_chain[chain_len - 1].size
        else:
            self._frame_size = self._viewport_size

        try:
            self._scroll_position = driver.get_current_scroll_position()
        except WebDriverException:
            self._scroll_position = Point(0, 0)
        if is_viewport_screenshot is None:
            is_viewport_screenshot = self._screenshot.width <= self._viewport_size['width'] \
                and self._screenshot.height <= self._viewport_size['height']
        self._is_viewport_screenshot = is_viewport_screenshot
        if frame_location_in_screenshot is None:
            if self._frame_chain:
                frame_location_in_screenshot = EyesScreenshot \
                    .calc_frame_location_in_screenshot(self._frame_chain, is_viewport_screenshot)
            else:
                # The frame is the default content
                frame_location_in_screenshot = Point(0, 0)
                if self._is_viewport_screenshot:
                    frame_location_in_screenshot.offset(-self._scroll_position.x,
                                                        -self._scroll_position.y)
        self._frame_location_in_screenshot = frame_location_in_screenshot
        self._frame_screenshot_intersect = Region(frame_location_in_screenshot.x,
                                                  frame_location_in_screenshot.y,
                                                  self._frame_size['width'],
                                                  self._frame_size['height'])
        self._frame_screenshot_intersect.intersect(Region(width=self._screenshot.width,
                                                          height=self._screenshot.height))

    @staticmethod
    def calc_frame_location_in_screenshot(frame_chain, is_viewport_screenshot):
        """
        Returns:
            (Point) The frame location as it would be on the screenshot. Notice that this value
            might actually be OUTSIDE the screenshot (e.g, if this is a viewport screenshot and
            the frame is located outside the viewport). This is not an error. The value can also
            be negative.
        """
        first_frame = frame_chain[0]
        location_in_screenshot = Point(first_frame.location['x'], first_frame.location['y'])
        # We only need to consider the scroll of the default content if the screenshot is a
        # viewport screenshot. If this is a full page screenshot, the frame location will not
        # change anyway.
        if is_viewport_screenshot:
            location_in_screenshot.x -= first_frame.parent_scroll_position.x
            location_in_screenshot.y -= first_frame.parent_scroll_position.y
        # For inner frames we must calculate the scroll
        inner_frames = frame_chain[1:]
        for frame in inner_frames:
            location_in_screenshot.x += frame.location['x'] - frame.parent_scroll_position.x
            location_in_screenshot.y += frame.location['y'] - frame.parent_scroll_position.y
        return location_in_screenshot

    def get_frame_chain(self):
        """
        Returns:
            (list) A copy of the frame chain, as received by the driver when the screenshot was
            created.
        """
        return [frame.clone() for frame in self._frame_chain]

    def get_base64(self):
        """
        Returns:
            (str) The base64 representation of the png.
        """
        if not self._screenshot64:
            screenshot_bytes = BytesIO()
            self._screenshot.write(screenshot_bytes)
            self._screenshot64 = base64.b64encode(screenshot_bytes.getvalue()).decode('UTF-8')
        return self._screenshot64

    def get_element_region_in_frame_viewport(self, element):
        """
        Returns:
            (Region) The element's region in the frame with scroll considered if necessary
        """
        location, size = element.location, element.size
        # Avoiding negative position of elements (yea, happens sometimes)
        location['x'], location['y'] = max(location['x'], 0), max(location['y'], 0)
        region = Region(location['x'], location['y'], size['width'], size['height'])
        # Frame offset is (0, 0) for default content
        if self._frame_chain or self._is_viewport_screenshot:
            region.left -= self._scroll_position.x
            region.top -= self._scroll_position.y
        return region

    def get_intersected_region(self, region):
        """
        Returns:
            (Region) The part of the region which intersects with
            the screenshot image.
        """
        region_in_screenshot = region.clone()
        region_in_screenshot.left += self._frame_location_in_screenshot.x
        region_in_screenshot.top += self._frame_location_in_screenshot.y
        region_in_screenshot.intersect(self._frame_screenshot_intersect)
        return region_in_screenshot

    def get_intersected_region_by_element(self, element):
        """
        Returns:
            (Region) The part of the element's region which intersects with
            the screenshot image.
        """
        element_region = self.get_element_region_in_frame_viewport(element)
        return self.get_intersected_region(element_region)

    def get_sub_screenshot_by_region(self, region):
        """
        Returns:
            (EyesScreenshot) A screenshot object representing the given region part of the image.
        """
        sub_screenshot_region = self.get_intersected_region(region)
        if not region.is_same_size(sub_screenshot_region):
            raise OutOfBoundsError("Region {0} is out of bounds!".format(region))
        sub_screenshot_frame_location = Point(
            self._frame_location_in_screenshot.x - sub_screenshot_region.left,
            self._frame_location_in_screenshot.y - sub_screenshot_region.top)
        screenshot = self._screenshot.get_subimage(sub_screenshot_region)
        return EyesScreenshot(self._driver, screenshot,
                              is_viewport_screenshot=self._is_viewport_screenshot,
                              frame_location_in_screenshot=sub_screenshot_frame_location)

    def get_sub_screenshot_by_element(self, element):
        """
        Returns:
            (EyesScreenshot) A screenshot object representing the element's region part of the
            image.
        """
        element_region = self.get_element_region_in_frame_viewport(element)
        return self.get_sub_screenshot_by_region(element_region)


class EyesWebElement(object):
    """
    A wrapper for selenium web element. This enables eyes to be notified about actions/events for
    this element.
    """
    _METHODS_TO_REPLACE = ['find_element', 'find_elements']

    # Properties require special handling since even testing if they're callable "activates"
    # them, which makes copying them automatically a problem.
    _READONLY_PROPERTIES = ['tag_name', 'text', 'location_once_scrolled_into_view', 'size',
                            'location', 'parent', 'id']

    def __init__(self, element, eyes, driver):
        self.element = element
        self._eyes = eyes
        self._driver = driver
        # Replacing implementation of the underlying driver with ours. We'll put the original
        # methods back before destruction.
        self._original_methods = {}
        for method_name in self._METHODS_TO_REPLACE:
            self._original_methods[method_name] = getattr(element, method_name)
            setattr(element, method_name, getattr(self, method_name))

        # Copies the web element's interface
        general_utils.create_proxy_interface(self, element, self._READONLY_PROPERTIES)
        # Setting properties
        for attr in self._READONLY_PROPERTIES:
            setattr(self.__class__, attr, general_utils.create_proxy_property(attr, 'element'))

    @property
    def bounds(self):
        # noinspection PyUnresolvedReferences
        location = self.location
        left, top = location['x'], location['y']
        width = height = 0  # Default

        # noinspection PyBroadException
        try:
            size = self.element.size
            width, height = size['width'], size['height']
        except:
            # Not implemented on all platforms.
            pass
        if left < 0:
            left, width = 0, max(0, width + left)
        if top < 0:
            top, height = 0, max(0, height + top)
        return Region(left, top, width, height)

    def find_element(self, by=By.ID, value=None):
        """
        Returns a WebElement denoted by "By".
        """
        # Get result from the original implementation of the underlying driver.
        result = self._original_methods['find_element'](by, value)
        # Wrap the element.
        if result:
            result = EyesWebElement(result, self._eyes, self._driver)
        return result

    def find_elements(self, by=By.ID, value=None):
        """
        Returns a list of web elements denoted by "By".
        """
        # Get result from the original implementation of the underlying driver.
        results = self._original_methods['find_elements'](by, value)
        # Wrap all returned elements.
        if results:
            updated_results = []
            for element in results:
                updated_results.append(EyesWebElement(element, self._eyes, self._driver))
            results = updated_results
        return results

    def click(self):
        self._eyes.add_mouse_trigger_by_element('click', self)
        self.element.click()

    def send_keys(self, *value):
        text = u''.join(map(str, value))
        self._eyes.add_text_trigger_by_element(self, text)
        self.element.send_keys(*value)


class _EyesSwitchTo(object):
    """
    Wraps a selenium "SwitchTo" object, so we can keep track of switching between frames.
    """
    _READONLY_PROPERTIES = ['alert', 'active_element']
    PARENT_FRAME = 1

    def __init__(self, driver, switch_to):
        self._switch_to = switch_to
        self._driver = driver
        general_utils.create_proxy_interface(self, switch_to, self._READONLY_PROPERTIES)

    def frame(self, frame_reference):
        # Find the frame's location and add it to the current driver offset
        if isinstance(frame_reference, str):
            frame_element = self._driver.find_element_by_name(frame_reference)
        elif isinstance(frame_reference, int):
            frame_elements_list = self._driver.find_elements_by_css_selector('frame, iframe')
            frame_element = frame_elements_list[frame_reference]
        else:
            # It must be a WebElement
            if isinstance(frame_reference, EyesWebElement):
                frame_reference = frame_reference.element
            frame_element = frame_reference
        # Calling the underlying "SwitchTo" object
        # noinspection PyProtectedMember
        self._driver._switched_to_frame(frame_reference, frame_element)
        return self._switch_to.frame(frame_reference)

    def frames(self, frame_chain):
        """
        Switches to the frames one after the other.
        """
        result = None
        for frame in frame_chain:
            self._driver.scroll_to(frame.parent_scroll_position)
            result = self.frame(frame.reference)
        return result

    def default_content(self):
        # This call resets the driver's current frame location
        # noinspection PyProtectedMember
        self._driver._switched_to_frame(None)
        return self._switch_to.default_content()

    def parent_frame(self):
        # Switching to parent frame is defined in the wire protocol, by not yet
        # implemented by the different web drivers, so we implement it ourselves.
        frames = self._driver.get_frame_chain()
        frames.pop()

        # noinspection PyProtectedMember
        self._driver._switched_to_frame(_EyesSwitchTo.PARENT_FRAME)

        self.default_content()
        self.frames(frames)

    def window(self, window_name):
        # noinspection PyProtectedMember
        self._driver._switched_to_frame(None)
        return self._switch_to.window(window_name)


class EyesFrame(object):
    """
    Encapsulates data about frames.
    """

    @staticmethod
    def is_same_frame_chain(frame_chain1, frame_chain2):
        """
        Args:
            frame_chain1: list of _EyesFrame instances, which represents a path to a frame.
            frame_chain2: list of _EyesFrame instances, which represents a path to a frame.
        """
        cl1, cl2 = len(frame_chain1), len(frame_chain2)
        if cl1 != cl2:
            return False
        for i in range(cl1):
            if frame_chain1[i].id != frame_chain2[i].id:
                return False
        return True

    def __init__(self, reference, location, size, id, parent_scroll_position):
        self.reference = reference
        self.location = location
        self.size = size
        self.id = id
        self.parent_scroll_position = parent_scroll_position

    def clone(self):
        return EyesFrame(self.reference, self.location.copy(), self.size.copy(), self.id,
                         self.parent_scroll_position.clone())


class EyesWebDriver(object):
    """
    A wrapper for selenium web driver which creates wrapped elements, and notifies us about
    events / actions.
    """
    # Properties require special handling since even testing if they're callable "activates"
    # them, which makes copying them automatically a problem.
    _READONLY_PROPERTIES = ['application_cache', 'current_url', 'current_window_handle',
                            'desired_capabilities', 'log_types', 'name', 'page_source', 'title',
                            'window_handles', 'switch_to']
    _SETABLE_PROPERTIES = ['orientation']

    _MAX_SCROLL_BAR_SIZE = 20  # This should pretty much cover all scroll bars.

    def __init__(self, driver, eyes):
        self.driver = driver
        self._eyes = eyes
        # List of frames the user switched to, and the current offset, so we can properly
        # calculate elements' coordinates
        self._frames = []
        driver_takes_screenshot = driver.capabilities.get('takesScreenshot', False)
        if driver_takes_screenshot:
            self._screenshot_taker = None
        else:
            logger.debug('Driver can\'t take screenshots, using our own screenshot taker.')
            # noinspection PyProtectedMember
            self._screenshot_taker = _ScreenshotTaker(driver.command_executor._url,
                                                      driver.session_id)

        # Creating the rest of the driver interface by simply forwarding it to the underlying
        # driver.
        general_utils.create_proxy_interface(self, driver,
                                             self._READONLY_PROPERTIES + self._SETABLE_PROPERTIES)

        for attr in self._READONLY_PROPERTIES:
            if not hasattr(self.__class__, attr):
                setattr(self.__class__, attr, general_utils.create_proxy_property(attr, 'driver'))
        for attr in self._SETABLE_PROPERTIES:
            if not hasattr(self.__class__, attr):
                setattr(self.__class__, attr, general_utils.create_proxy_property(attr, 'driver',
                                                                                  True))

    def get(self, url):
        # We're loading a new page, so the frame location resets
        self._switched_to_frame(None)
        return self.driver.get(url)

    def find_element(self, by=By.ID, value=None):
        """
        Returns a WebElement denoted by "By".
        """
        # Get result from the original implementation of the underlying driver.
        result = self.driver.find_element(by, value)
        # Wrap the element.
        if result:
            result = EyesWebElement(result, self._eyes, self)
        return result

    def find_elements(self, by=By.ID, value=None):
        """
        Returns a list of web elements denoted by "By".
        """
        # Get result from the original implementation of the underlying driver.
        results = self.driver.find_elements(by, value)
        # Wrap all returned elements.
        if results:
            updated_results = []
            for element in results:
                updated_results.append(EyesWebElement(element, self._eyes, self))
            results = updated_results
        return results

    def find_element_by_id(self, id_):
        """Finds an element by id.

        :Args:
         - id\_ - The id of the element to be found.

        :Usage:
            driver.find_element_by_id('foo')
        """
        return self.find_element(by=By.ID, value=id_)

    def find_elements_by_id(self, id_):
        """
        Finds multiple elements by id.

        :Args:
         - id\_ - The id of the elements to be found.

        :Usage:
            driver.find_element_by_id('foo')
        """
        return self.find_elements(by=By.ID, value=id_)

    def find_element_by_xpath(self, xpath):
        """
        Finds an element by xpath.

        :Args:
         - xpath - The xpath locator of the element to find.

        :Usage:
            driver.find_element_by_xpath('//div/td[1]')
        """
        return self.find_element(by=By.XPATH, value=xpath)

    def find_elements_by_xpath(self, xpath):
        """
        Finds multiple elements by xpath.

        :Args:
         - xpath - The xpath locator of the elements to be found.

        :Usage:
            driver.find_elements_by_xpath("//div[contains(@class, 'foo')]")
        """
        return self.find_elements(by=By.XPATH, value=xpath)

    def find_element_by_link_text(self, link_text):
        """
        Finds an element by link text.

        :Args:
         - link_text: The text of the element to be found.

        :Usage:
            driver.find_element_by_link_text('Sign In')
        """
        return self.find_element(by=By.LINK_TEXT, value=link_text)

    def find_elements_by_link_text(self, text):
        """
        Finds elements by link text.

        :Args:
         - link_text: The text of the elements to be found.

        :Usage:
            driver.find_elements_by_link_text('Sign In')
        """
        return self.find_elements(by=By.LINK_TEXT, value=text)

    def find_element_by_partial_link_text(self, link_text):
        """
        Finds an element by a partial match of its link text.

        :Args:
         - link_text: The text of the element to partially match on.

        :Usage:
            driver.find_element_by_partial_link_text('Sign')
        """
        return self.find_element(by=By.PARTIAL_LINK_TEXT, value=link_text)

    def find_elements_by_partial_link_text(self, link_text):
        """
        Finds elements by a partial match of their link text.

        :Args:
         - link_text: The text of the element to partial match on.

        :Usage:
            driver.find_element_by_partial_link_text('Sign')
        """
        return self.find_elements(by=By.PARTIAL_LINK_TEXT, value=link_text)

    def find_element_by_name(self, name):
        """
        Finds an element by name.

        :Args:
         - name: The name of the element to find.

        :Usage:
            driver.find_element_by_name('foo')
        """
        return self.find_element(by=By.NAME, value=name)

    def find_elements_by_name(self, name):
        """
        Finds elements by name.

        :Args:
         - name: The name of the elements to find.

        :Usage:
            driver.find_elements_by_name('foo')
        """
        return self.find_elements(by=By.NAME, value=name)

    def find_element_by_tag_name(self, name):
        """
        Finds an element by tag name.

        :Args:
         - name: The tag name of the element to find.

        :Usage:
            driver.find_element_by_tag_name('foo')
        """
        return self.find_element(by=By.TAG_NAME, value=name)

    def find_elements_by_tag_name(self, name):
        """
        Finds elements by tag name.

        :Args:
         - name: The tag name the use when finding elements.

        :Usage:
            driver.find_elements_by_tag_name('foo')
        """
        return self.find_elements(by=By.TAG_NAME, value=name)

    def find_element_by_class_name(self, name):
        """
        Finds an element by class name.

        :Args:
         - name: The class name of the element to find.

        :Usage:
            driver.find_element_by_class_name('foo')
        """
        return self.find_element(by=By.CLASS_NAME, value=name)

    def find_elements_by_class_name(self, name):
        """
        Finds elements by class name.

        :Args:
         - name: The class name of the elements to find.

        :Usage:
            driver.find_elements_by_class_name('foo')
        """
        return self.find_elements(by=By.CLASS_NAME, value=name)

    def find_element_by_css_selector(self, css_selector):
        """
        Finds an element by css selector.

        :Args:
         - css_selector: The css selector to use when finding elements.

        :Usage:
            driver.find_element_by_css_selector('#foo')
        """
        return self.find_element(by=By.CSS_SELECTOR, value=css_selector)

    def find_elements_by_css_selector(self, css_selector):
        """
        Finds elements by css selector.

        :Args:
         - css_selector: The css selector to use when finding elements.

        :Usage:
            driver.find_elements_by_css_selector('.foo')
        """
        return self.find_elements(by=By.CSS_SELECTOR, value=css_selector)

    def get_screenshot_as_base64(self):
        """
        Gets the screenshot of the current window as a base64 encoded string
           which is useful in embedded images in HTML.

        :Usage:
            driver.get_screenshot_as_base64()
        """
        if self._screenshot_taker is None:
            screenshot = self.driver.get_screenshot_as_base64()
        else:
            screenshot = self._screenshot_taker.get_screenshot_as_base64()
        return screenshot

    def extract_full_page_width(self):
        # noinspection PyUnresolvedReferences
        return self.execute_script("return document.documentElement.scrollWidth")

    def extract_full_page_height(self):
        # noinspection PyUnresolvedReferences
        return self.execute_script("return document.documentElement.scrollHeight")

    def get_current_scroll_position(self):
        """
        Extracts the current scroll position from the browser.
        Returns:
            (Point) The scroll position
        """
        # noinspection PyUnresolvedReferences
        x = self.execute_script("return window.scrollX")
        # noinspection PyUnresolvedReferences
        y = self.execute_script("return window.scrollY")
        return Point(x, y)

    def scroll_to(self, p):
        """
        Commands the browser to scroll to a given position using javascript.
        """
        # noinspection PyUnresolvedReferences
        self.execute_script("window.scrollTo({0}, {1})".format(p.x, p.y))

    def get_entire_page_size(self):
        """
        Extracts the size of the current page from the browser using Javascript.
        """
        return {'width': self.extract_full_page_width(),
                'height': self.extract_full_page_height()}

    def get_frame_chain(self):
        """
        Returns:
            (list) A list of EyesFrame instances which represents the path to the current frame.
            This can later be used as an argument to _EyesSwitchTo.frames().
        """
        return [frame.clone() for frame in self._frames]

    def get_viewport_size(self):
        """
        Returns:
            The viewport size of the current frame.
        """
        return _viewport_size.get_viewport_size(self)

    def get_default_content_viewport_size(self):
        """
        Switches to the default content frame, extracts the viewport size, and returns to the 
        current frame.  
        Returns:
            The viewport size of the most outer frame.
        """
        current_frames = self.get_frame_chain()
        self.switch_to.default_content()
        viewport_size = _viewport_size.get_viewport_size(self)
        self.switch_to.frames(current_frames)
        return viewport_size

    def get_full_page_screenshot(self):
        logger.info('getting full page screenshot..')

        # Saving the current frame reference and moving to the outermost frame.
        original_frame = self.get_frame_chain()
        self.switch_to.default_content()

        original_scroll_position = self.get_current_scroll_position()

        self.scroll_to(Point(0, 0))

        entire_page_size = self.get_entire_page_size()

        # Starting with the screenshot at 0,0
        screenshot64 = self.get_screenshot_as_base64()
        screenshot = _image_utils.png_image_from_bytes(base64.b64decode(screenshot64))
        # If the screenshot is the same size as the page size, no stitching is required.
        if (screenshot.width >= self.extract_full_page_width()) and \
                (screenshot.height >= self.extract_full_page_height()):
            self.switch_to.frames(original_frame)
            return screenshot

        # We the fact that we might use a "smaller" viewport size than the actual viewport size
        # doesn't matter, since we'll take a screenshot of the entire page.
        viewport_size = {'width': _viewport_size.extract_viewport_width(self),
                         'height': _viewport_size.extract_viewport_height(self) -
                                   EyesWebDriver._MAX_SCROLL_BAR_SIZE}

        logger.debug("Total size: {0}, Viewport: {1}".format(entire_page_size, viewport_size))

        screenshot_parts = Region(0, 0, entire_page_size['width'], entire_page_size['height']) \
            .get_sub_regions(viewport_size)

        # Starting with the screenshot at 0,0
        stitched_image = screenshot

        for part in screenshot_parts:
            # Since we already took the screenshot for 0,0
            if part.left == 0 and part.top == 0:
                logger.debug('Skipping screenshot for 0,0 (already taken)')
                continue
            logger.debug("Taking screenshot for {0}".format(part))
            self.scroll_to(Point(part.left, part.top))
            # Give it time to scroll
            time.sleep(0.1)
            # Since screen size might cause the scroll to reach only part of the way
            current_scroll_position = self.get_current_scroll_position()
            logger.debug("Scrolled To ({0},{1})".format(current_scroll_position.x,
                                                        current_scroll_position.y))
            screenshot64 = self.get_screenshot_as_base64()
            screenshot = _image_utils.png_image_from_bytes(base64.b64decode(screenshot64))
            stitched_image.paste(current_scroll_position.x, current_scroll_position.y,
                                 screenshot.pixels)

        # Returning the user to the original position
        self.scroll_to(original_scroll_position)

        # Returning to the frame we started at
        self.switch_to.frames(original_frame)

        return stitched_image

    def _switched_to_frame(self, frame_reference, frame_element=None):
        """
        Updates the current webdriver that a switch was made to a frame element
        """
        if frame_element is not None:
            frame_location = frame_element.location
            frame_size = frame_element.size
            frame_id = frame_element.id
            parent_scroll_position = self.get_current_scroll_position()
            # Frame border can affect location calculation for elements.
            # noinspection PyBroadException
            try:
                frame_left_border_width = int(frame_element
                                              .value_of_css_property('border-left-width')
                                              .rstrip('px'))
                frame_top_border_width = int(frame_element.value_of_css_property('border-top-width')
                                             .rstrip('px'))
            except:
                frame_left_border_width = 0
                frame_top_border_width = 0
            frame_location['x'] += frame_left_border_width
            frame_location['y'] += frame_top_border_width
            self._frames.append(EyesFrame(frame_reference, frame_location, frame_size, id,
                                          parent_scroll_position))
        elif frame_reference == _EyesSwitchTo.PARENT_FRAME:
            self._frames.pop()
        else:
            # We moved out of the frames
            self._frames = []

    @property
    def switch_to(self):
        return _EyesSwitchTo(self, self.driver.switch_to)

    @property
    def current_offset(self):
        """
        Return the current offset of the context we're in (e.g., due to switching into frames)
        """
        offset = {'x': 0, 'y': 0}
        for frame in self._frames:
            offset['x'] += frame.location['x']
            offset['y'] += frame.location['y']
        return offset

