from appium.webdriver.common.touch_action import TouchAction
from AppiumLibrary import utils
from AppiumLibrary.locators import ElementFinder
from keywordgroup import KeywordGroup

class _ElementKeywords(KeywordGroup):

    def __init__(self):
        self._element_finder = ElementFinder()

    # Public, element lookups
    def click_element_by_name(self, name):
        """ Click element by name """
        self._click_element_by_name(name)

    def click_button(self, id_or_name):
        """ Click button """
        self._click_element_by_tag_name('Button', id_or_name)

    def click_radio_button(self, id_or_name):
        """ Click radio button """
        self._click_element_by_tag_name('radioButton', id_or_name)

    def click_check_box(self, id_or_name):
        """ Click checkbox """
        self._click_element_by_tag_name('checkBox', id_or_name)

    def click_toggle_button(self, id_or_name):
        """ Click toggle button """
        self._click_element_by_tag_name('toggleButton', id_or_name)

    def click_text_view(self, id_or_name):
        """ Click text view """
        self._click_element_by_tag_name('textView', id_or_name)

    def click_spinner(self, id_or_name):
        """ Click spinner """
        self._click_element_by_tag_name('spinner', id_or_name)

    def click_checked_text_view(self, id_or_name):
        """ Click checked text view """
        self._click_element_by_tag_name('checkedTextView', id_or_name)

    def click_image_button(self, id_or_name):
        """ Click image button """
        self._click_element_by_tag_name('imageButton', id_or_name)

    def input_text(self, text):
        """ Input text """
        textfields = self._find_elements_by_tag_name("editText")
        textfields[0].send_keys(text)

    def long_press(self, tag_name, id_or_name):
        """ Long press the element """
        driver = self._current_application()
        element = self._find_element_by_tag_name(tag_name, id_or_name)
        long_press = TouchAction(driver).long_press(element)
        long_press.perform()

    def reset_application(self):
        """ Reset application """
        driver = self._current_application()
        driver.execute_script('mobile: reset')

    def scroll_screen(self, endX, endY, duration='1',
                      tap_count= '1', startX='0.5', startY='0.5'):
        """ Scroll screen """
        driver = self._current_application()
        args = {'startX':float(startX), 'startY':float(startY),
                'startX':float(endX), 'startY':float(endY),
                'tapCount':int(tap_count), 'duration':int(duration)}
        driver.execute_script('mobile: swipe', args)

    def scroll_element(self, tag_name, id_or_name,
                   endX, endY, duration='1', tap_count= '1', startX='0.5', startY='0.5'):
        """ Scroll element """
        driver = self._current_application()
        element = self._find_element_by_tag_name(tag_name, id_or_name)
        args = {'startX':float(startX), 'startY':float(startY),
                'startX':float(endX), 'startY':float(endY),
                'tapCount':int(tap_count), 'duration':int(duration),
                'element':element.ref}
        driver.execute_script('mobile: swipe', args)

    def slide_rating_bar(self, id_or_name, endX, endY,
                     tap_count='1', startX='0.0', startY='0.0'):
        """ Slide rating bar """
        driver = self._current_application()
        element = self._find_element_by_tag_name('ratingBar', id_or_name)
        args = {'startX':float(startX), 'startY':float(startY),
                'endX':float(endX), 'endY':float(endY),
                'tapCount':int(tap_count), 'element':element.id, 'duration':1}
        driver.execute_script('mobile: flick', args)

    def slide_seek_bar(self, id_or_name, endX, endY,
                       tap_count='1', startX='0.0', startY='0.0'):
        """ Slide seek bar """
        driver = self._current_application()
        element = self._find_element_by_tag_name('seekBar', id_or_name)
        args = {'startX':float(startX), 'startY':float(startY),
                'endX':float(endX), 'endY':float(endY),
                'tapCount':int(tap_count), 'element':element.id, 'duration':1}
        driver.execute_script('mobile: flick', args)

    
    # Private

    def _find_elements_by_tag_name(self, tag_name):
        driver = self._current_application()
        elements = driver.find_elements_by_tag_name(tag_name)
        return elements

    def _find_element_by_tag_name(self, tag_name, id_or_name):
        elements = self._find_elements_by_tag_name(tag_name)
    
        if self._is_id(id_or_name):
            try:
                index = int(id_or_name.split('=')[-1])
                element = elements[index]
            except IndexError, TypeError:
                raise Exception, 'Cannot find the element with index "%s"' % id_or_name
        else:
            found = False
            for element in elements:
                if element.text == id_or_name:
                    found = True
                    break
            if not found:
                raise Exception, 'Cannot find the element with name "%s"' % id_or_name

        return element
    
    def _is_id(self, id_or_name):
        if id_or_name.startswith('id='):
            return True
        else:
            return False

    def _click_element_by_tag_name(self, tag_name, id_or_name):
        element = self._find_element_by_tag_name(tag_name, id_or_name)
    
        try:
            element.click()
        except Exception, e:
            raise Exception, 'Cannot click the %s element "%s"' % (tag_name, id_or_name)

    def _click_element_by_name(self, name):
        driver = self._current_application()
        try:
            element = driver.find_element_by_name(name)
        except Exception, e:
            raise Exception, e
    
        try:
            element.click()
        except Exception, e:
            raise Exception, 'Cannot click the element with name "%s"' % name
