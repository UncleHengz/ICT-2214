# Sample script to search on Yahoo, take screenshot of results and visit DuckDuckgo

# RPA for Python's simple and powerful API makes robotic process automation fun!
# pip install rpa to install, pip install rpa --upgrade to get latest version

# to use in Jupyter notebook, Python script or interactive shell
import rpa as r

customurl="www.facebook.com"
# use init() to start TagUI, it auto downloads TagUI on first run
# default init(visual_automation = False, chrome_browser = True)w
r.init(chrome_browser = True,headless_mode=False,visual_automation=True)
r.click(500,200)
# # use url('your_url') to go to web page, url() returns current URL
# r.url('https://ca.yahoo.com')

r.url('https://www.similarweb.com')
r.click('hm-hero-search')#, 'facebook.com[enter]')
r.keyboard(customurl+'[enter]')
# r.type("app-search__input", 'decentralization[enter]')
r.wait(5)
w=r.read("engagement-list__item-value")
print("Total Clicks for: "+customurl+" is " + w)
# use close() to close TagUI process and web browser
# if you forget to close, just close() next time
r.close()

# in above web automation example, web element identifier can be XPath selector, CSS selector or
# attributes id, name, class, title, aria-label, text(), href, in decreasing order of priority
# if you don't mind using ugly and less robust XPath, it can be copied from Chrome inspector
# otherwise recommend googling on writing XPath manually, or simply make use of attributes

# also supports visual element identifier using .png or .bmp image snapshot
# representing the UI element (can be on desktop applications or web browser)
# for eg r.click('start_menu.png'), r.type('username_box.png', 'Sonic')

# if the image file specified does not exist, OCR will be used to search for
# that text on the screen to interact with the UI element containing that text
# for eg r.click('Submit Form.png') clicks on a button with text 'Submit Form'
# this trick also works for hover(), type(), select(), read(), snap() functions

# visual element identifiers can also be x, y coordinates of elements on the screen
# for eg r.click(600, 300), r.type(600, 300, 'Mario'), r.select(600, 300, 600, 400)
# another eg is boundary of area of interest x1, y1, x2, y2 for read() and snap()
# for eg r.read(200, 200, 600, 400), r.snap(200, 200, 600, 400, 'results.png')

# image transparency (0% opacity) is supported, ie images with empty sections
# eg r.read('image_preview_frame.png'), r.snap('application_window_frame.png')
# or an element with transparent background to work with varying backgrounds
# r.click('icon_transparent_background.png'), r.click('button_no_bkgnd.png')