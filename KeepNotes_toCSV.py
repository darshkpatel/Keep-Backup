import csv
import re
import sys
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.webdriver import FirefoxProfile
from optparse import OptionParser


parser = OptionParser()
parser.add_option("-p", "--profile", dest="profile", type="string", action="store",
                  help="Absolute path to Firefox Profile", metavar="-p [Path to Profile]")
parser.add_option("-t", "--pause", dest="delay", type="int", action="store",
                  help="Delay before scrolling page", metavar="-t [Delay]", default=4.5)
parser.add_option("-o", "--output", dest="output", type="string", action="store",
                  help="Relative path to output file and its name eg. saves/googlekeep.csv", metavar="-o [Output file name]")

parser.add_option("-s", "--separateLinks",
                  action="store_true", dest="separate", default=True,
                  help="Separate Links")
(options, args) = parser.parse_args()
if not options.output:   # if filename is not given
    parser.error('output file destination not given')
if not options.profile:
    parser.error("Path to firefox profile not given")
if not options.delay:
    SCROLL_PAUSE_TIME = 4.5


profile = FirefoxProfile(options.profile)
driver = webdriver.Firefox(profile)
driver.get('http://keep.google.com')

reload(sys)
sys.setdefaultencoding('utf-8')

# Note - IZ65Hb-WsjYwc-nUpftc  / IZ65Hb-TBnied
# Title - r4nke-YPqjbf
# list-text - rymPhb-IZ65Hb-gkA7Yd
# links - h1U9Be-YPqjbf
# TAG - XPtOyb-fmcmS






def getNote(xnote, seperate_links):
    content =xnote.find_element_by_class_name('IZ65Hb-s2gQvd')
    title = content.find_element_by_class_name('r4nke-YPqjbf').text
    text=""
    link=""
    try:
        if seperate_links:
            text = re.sub(r'^https?:\/\/.*[\r\n]*', '', content.find_element_by_class_name('h1U9Be-YPqjbf').text,
                          flags=re.MULTILINE)
            link = content.find_element_by_tag_name('a').text
        else:
            text = content.find_element_by_class_name('h1U9Be-YPqjbf').text
            link = ''
    except NoSuchElementException:
        print "No Title In Note"

    note_list={'Title':title, 'Text':text,'Link':link}
    return note_list


# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")
notes = driver.find_elements_by_class_name('IZ65Hb-TBnied')
final_notes=[]
while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    print "Waiting for page to load"
    time.sleep(options.delay)

    notes = driver.find_elements_by_class_name('IZ65Hb-TBnied')
    for note in notes:
        final_notes.append(getNote(note, options.separate))
        print "Appending Note"
    print "Scrolling Down The Page"
    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height


keys = final_notes[0].keys()
with open('GoogleKeepNotes.csv', 'wb') as f:
    w=csv.DictWriter(f,keys)
    w.writeheader()
    w.writerows(final_notes)
    f.close()


driver.close()
