import re
from datetime import datetime
import base64
import time
import os
import signal
from glob import glob
# import matplotlib.pyplot as plt
from skimage.io import imread,imsave
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome import service

def date_to_number(text):
    match = re.search(r'\d{2}.\d{2}.\d{4}', text)
    t = datetime.strptime(match.group(), "%d.%m.%Y").date()
    return time.mktime(t.timetuple())

import re
def removeNonAscii(s):
    return re.sub(r'\\u\w{4}','',s)

def wait_for(condition_function):
    start_time = time.time()
    while time.time() < start_time + 3:
        if condition_function():
            return True
        else:
            time.sleep(0.1)
    raise Exception(
        'Timeout waiting for {}'.format(condition_function.__name__)
    )
#
# class wait_for_page_load(object):
def wait_for_page_load(br, old_page,timeout=30):
    old_page = br.find_element_by_tag_name('html')
    yield
    WebDriverWait(br, timeout).until(staleness_of(old_page))


class AppointmentSearch():

    def __init__(self, params):
        """

        :param first_name:
        :param last_name:
        :param email:
        :param repeat_email:
        :param passnummer:
        :param lower_date: format 'dd.mm.yyyy'
        :param upper_date:
        """

        self.app_link = params.get('app_link')
        self.first_name = params.get('first_name')
        self.last_name = params.get('last_name')
        self.email = params.get('email')
        self.repeat_email = params.get('repeat_email')
        assert self.email == self.repeat_email

        self.passnummer = params.get('passnummer')
        self.lower_date = date_to_number(params.get('lower_date'))
        self.upper_date = date_to_number(params.get('upper_date'))
        self.img_path = params.get('img_path')
        self.txt_file = params.get('txt_file')
        self.iter_id = params.get('iter_id')
        # self.br = Browser()
        # self.br.set_handle_robots(False)
        # self.br.addheaders = [("User-agent", "Firefox")]
        self.wrong_cap_dir = params.get('wrong_cap_dir')

        self.cap_fail_msg = params.get('cap_fail_msg')
        self.no_app_msg = params.get('no_app_msg')
        self.other_month_msg = params.get('other_month_msg')
        self.app_available_msg = params.get('app_available_msg')
        self.odd_path = params.get('odd_path')
        self.now = None
        self.long_term = params.get('long_term')
        self.timed = params.get('timed')
        # self.br = webdriver.Firefox(executable_path="data/geckodriver")
        self.br = webdriver.PhantomJS()
        # webdriver_service = service.Service('/home/azhar/Downloads/operadriver_linux64/operadriver')
        # webdriver_service.start()
        # self.br = webdriver.Remote(webdriver_service.service_url, webdriver.DesiredCapabilities.OPERA)

        # options = webdriver.ChromeOptions()
        # options.binary_location = "/usr/bin/opera"
        # self.br = webdriver.Opera(opera_options=options,executable_path='/home/azhar/Downloads/operadriver_linux64/operadriver')

        self.br.implicitly_wait(1)


        self.odd = open(self.odd_path,'wb')

        if not os.path.exists(self.txt_file):
            fp = open(self.txt_file,'wb')
            fp.write(' ')
            fp.close()


    def get_captcha_text(self,content):
        my_file = content
        index = my_file.find("url(\'data:image")
        b = my_file[index:].split(')')
        a = b[0]
        return a[27:-1]

    def captcha_solver(self,content):
        try:
            os.remove(self.img_path+'.png')
            # os.remove(self.img_path + '.jpg')
            os.remove(self.img_path + '2.png')
        except:
            pass

        imgdata = base64.b64decode(self.get_captcha_text(content))

        with open(self.img_path+'.jpg', 'wb') as fp:
            fp.write(imgdata)
        with open(self.img_path+'2.jpg', 'wb') as fp:
            fp.write(imgdata)
        img = imread(self.img_path+'.jpg')
        imsave(self.img_path + '.png', img)
        imsave(self.img_path + '2.png', img)
        while not(os.path.exists(self.img_path+'2.txt')):
            pass
        time.sleep(0.5)

        with open(self.img_path+'.txt','rb') as fp:
            cap = fp.readline()[:-1]
        print cap
        try:
            os.remove(self.img_path+'.png')
            # os.remove(self.img_path + '.jpg')
            os.remove(self.img_path + '2.png')
        except:
            pass
#        plt.subplot(1,2,1)
#        plt.imshow(img)
        return cap


    def wrong_captcha(self):
        img  = imread(self.img_path+'2.jpg')
        files = glob(self.wrong_cap_dir+'*.jpg')
        d = len(files)+1
        imsave(self.wrong_cap_dir+str(d)+'.jpg',img)


    def search_bot(self):
        
        while 1:
            if self.timed:
                hms = datetime.now()
                hr = hms.hour
                mint = hms.minute
                sec = hms.second
                while not (hr == 22 and mint >= 15 and mint <20):
                    hms = datetime.now()
                    hr = hms.hour
                    mint = hms.minute
                    sec = hms.second
                    print hr, mint, sec
                    time.sleep(15)
                print hr,mint
            if self.long_term:
                self.br = webdriver.PhantomJS()
                # self.br = webdriver.Firefox(executable_path="data/geckodriver")
            self.br.get(self.app_link)
            start_time = time.time()
            self.now = time.time()
            
                
            while time.time()-start_time < 120:
                # print time.time()-self.now
                # if self.long_term:
                #     self.br = webdriver.Firefox(executable_path="data/geckodriver")
                #     self.br.get(self.app_link)

                contents = removeNonAscii(self.br.page_source)

                if "url(\'data:image" in contents:
                    if self.cap_fail_msg in contents:
                        print self.cap_fail_msg + " was wrong"

                    print "in captcha"
                    print "before captcha: ",time.time() - self.now, datetime.now().minute, datetime.now().second
                    cap_start = time.time()
                    # time.sleep(1.5)
                    cap_text = self.get_captcha_text(self.br.page_source)
                    cap = self.captcha_solver(self.br.page_source)

                    a = self.br.find_element_by_name("captchaText")
                    # cap = 'a'
                    a.clear()
                    # a.
                    a.send_keys(Keys.CONTROL,'a')

                    for k in range(0,6):
                        a.send_keys(cap[k])
                        # time.sleep(0.13)

                    while time.time() - cap_start < 3.7:
                        time.sleep(0.01)
                    try:
                        a = self.br.find_element_by_name("action:appointment_showMonth")
                    except:
                        a = self.br.find_element_by_name("action:appointment_addAppointment")
                    a.click()
                    print "after captcha: ",time.time() - self.now, datetime.now().minute, datetime.now().second
                    #  a.send_keys(Keys.ENTER)

                    t = time.time()
                    while time.time() - t < 5:
                        try:
                            #a.send_keys(Keys.RETURN)
                            a.click()
                            time.sleep(0.01)
                        except StaleElementReferenceException:
                            break

                    print "finidshed load after captcha: ", time.time() - self.now,  datetime.now().minute, datetime.now().second
                    im2 = imread(self.img_path+'.jpg')
                    os.remove(self.img_path+'2.jpg')
                    # wait_for_page_load(self.br)
                    # time.sleep(0.8)
                    # print time.time() - self.now
                    contents = removeNonAscii(self.br.page_source)
                    cap_text1 = str(cap_text)


                    while "url(\'data:image" in contents and cap_text1 == cap_text:
                        try:
                            contents = removeNonAscii(self.br.page_source)
                            cap_text1 = self.get_captcha_text(self.br.page_source)
                        except:
                            continue

                elif self.no_app_msg in contents or self.other_month_msg in contents:
                    if self.other_month_msg in contents:
                        print "other months"
                    else:
                        print "no app"
                    hr = datetime.now().hour
                    mint = datetime.now().minute
                    if not self.long_term or (hr == 22 and mint >= 15 and mint < 17):
                        if mint==15 and datetime.now().second < 50:
                            time.sleep(4)
                        else:
                            time.sleep(0.3)
                    else:
                        time.sleep(4)

                    while 1:
                        nowt = datetime.now().day
                        try:
                            try:
                                a = self.br.find_element_by_xpath("//a[contains(@href,'?locationCode=isla&realmId=108&categoryId=203&dateStr=%0.2d.04.2018')]"%(nowt+1))
                            except:
                                a = self.br.find_element_by_xpath("//a[contains(@href,'?locationCode=isla&realmId=108&categoryId=203&dateStr=%0.2d.04.2018')]"%(nowt+2))
                            a.click()
                            break
                        except:
                            continue
                    t = time.time()
                    while time.time() - t < 5:
                        try:
                            a.click()
                            time.sleep(0.01)
                        except StaleElementReferenceException:
                            break

                elif self.app_available_msg in contents:
                    print "found date"
                    print time.time()-self.now, datetime.now().minute, datetime.now().second
                    self.date_select()
                    # break

                else:
                    print "some shit"
                    # cap = self.captcha_solver(self.br.page_source)
                    print contents
                    self.odd.write(contents)
                    self.odd.write('\n\n\n\n')
                    if self.long_term:
                        time.sleep(5)
            self.br.service.process.send_signal(signal.SIGTERM) # kill the specific phantomjs child proc
            self.br.quit() 
#             self.br.close()
            if not self.long_term:
                break
            # except:
            #     continue

    def date_select(self):
        response = None
        result = False

        ## select day for appointment
        valid_links = []
        count = 0
        for link in self.br.find_elements_by_link_text("Appointments are available"):
            d = date_to_number(link.get_attribute('href'))
            if self.lower_date <= d <= self.upper_date:
                valid_links.append(link)
                count += 1
            if count >= int(self.iter_id):
                break
        print len(valid_links), self.iter_id
        valid_links[-1].click()
        # time.sleep(0.8)
        contents = removeNonAscii(self.br.page_source)
        while self.app_available_msg in contents:
            contents = removeNonAscii(self.br.page_source)

        # response = removeNonAscii(self.br.page_source)
        if "Please select an appointment" in contents:
            response2 = None

            ## select appointment time
            for link in self.br.find_elements_by_link_text("Book this appointment"):
                link.click()
                break

            t = time.time()
            while time.time() - t < 3:
                try:
                    link.click()
                    time.sleep(0.01)
                except StaleElementReferenceException:
                    break


            # time.sleep(0.8)
            contents = removeNonAscii(self.br.page_source)
            while "Please select an appointment" in contents:
                contents = removeNonAscii(self.br.page_source)

            # response2 = removeNonAscii(self.br.page_source)
            ## fill appointment form
            if "appointment_newAppointmentForm" in contents:
                print time.time() - self.now, datetime.now().minute, datetime.now().second
                ##solve captcha
                cap_time = time.time()
                print time.time() - self.now, datetime.now().minute, datetime.now().second
                a = self.br.find_element_by_name("lastname")
                a.send_keys(self.last_name)
                a = self.br.find_element_by_name("firstname")
                a.send_keys(self.first_name)
                a = self.br.find_element_by_name("email")
                a.send_keys(self.email)
                a = self.br.find_element_by_name("emailrepeat")
                a.send_keys(self.repeat_email)
                a = self.br.find_element_by_name("fields[0].content")
                a.send_keys(self.passnummer)
                print time.time() - self.now, datetime.now().minute
                # self.br['passnummer'] = 'ALAN71954'
                # time.sleep(1.5)
                cap = self.captcha_solver(self.br.page_source)
                u = self.br.find_element_by_name("captchaText")
                u.clear()
                for k in range(0, 6):
                    u.send_keys(cap[k])
                    # time.sleep(0.15)
                # time.sleep(0.5)
                while time.time() - cap_time < 3.7:
                    time.sleep(0.01)
                os.remove(self.img_path + '.jpg')
                a = self.br.find_element_by_name("action:appointment_addAppointment")
                a.click()
                #u.send_keys(Keys.RETURN)
                t = time.time()
                while time.time() - t < 5:
                    try:
                        a.click()
                        time.sleep(0.01)
                    except StaleElementReferenceException:
                        break
                print time.time()-self.now, datetime.now().minute, datetime.now().second
                time.sleep(6)
