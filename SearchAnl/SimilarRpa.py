import rpa as r

def SimRPA(customURL):
    r.init(chrome_browser=True, headless_mode=False, visual_automation=True)
    r.click(500, 200)
    r.url('https://www.similarweb.com')
    r.click('hm-hero-search')
    r.keyboard(customURL + '[enter]')
    #r.wait(2)  # Wait for the page to load properly
    clicks = r.read('engagement-list__item-value')
    if (len(clicks)==0):
        clicks=0

    if (clicks[-1]=='K'):
        clicks = float(clicks[:-1])*(10**3)
    elif (clicks[-1]=='M'):
        clicks = float(clicks[:-1])*(10**6)
    elif (clicks[-1]=='B'):
        clicks = float(clicks[:-1])*(10**9)  
    else:
        clicks=float(clicks)
     
    return int(clicks)

result = SimRPA("www.fb.com")
print("Number of clicks:", result)
