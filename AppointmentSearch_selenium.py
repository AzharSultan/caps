import re
from datetime import datetime
import base64
import time
import os
from glob import glob
from mechanize import Browser
import matplotlib.pyplot as plt
from skimage.io import imread,imsave
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

def date_to_number(text):
    match = re.search(r'\d{2}.\d{2}.\d{4}', text)
    t = datetime.strptime(match.group(), "%d.%m.%Y").date()
    return time.mktime(t.timetuple())

import re
def removeNonAscii(s):
    return re.sub(r'\\u\w{4}','',s)

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
        self.br = Browser()
        self.br.set_handle_robots(False)
        self.br.addheaders = [("User-agent", "Firefox")]
        self.wrong_cap_dir = params.get('wrong_cap_dir')

        self.cap_fail_msg = params.get('cap_fail_msg')
        self.no_app_msg = params.get('no_app_msg')
        self.other_month_msg = params.get('other_month_msg')
        self.app_available_msg = params.get('app_available_msg')
        self.odd_path = params.get('odd_path')
        self.now = None
        self.br = webdriver.Firefox(executable_path="/home/azhar/Downloads/geckodriver")

        self.dcap = dict(DesiredCapabilities.PHANTOMJS)
        self.dcap["phantomjs.page.settings.userAgent"] = (
            "Firefox"
        )

        self.odd = open(self.odd_path,'wb')

        if not os.path.exists(self.txt_file):
            fp = open(self.txt_file,'wb')
            fp.write(' ')
            fp.close()


    def captcha_solver(self,content):
        my_file = content
        index = my_file.find("url(\'data:image")
        b = my_file[index:].split(')')
        a = b[0]
        imgdata = base64.b64decode(a[27:-1])

        with open(self.img_path+'.jpg', 'wb') as fp:
            fp.write(imgdata)
        with open(self.img_path+'2.jpg', 'wb') as fp:
            fp.write(imgdata)
        img = imread(self.img_path+'.jpg')
        imsave(self.img_path + '.png', img)
        imsave(self.img_path + '2.png', img)
        while not(os.path.exists(self.txt_file)):
            pass
        time.sleep(0.5)
        with open(self.txt_file,'rb') as fp:
            cap = fp.readline()[:-1]
        print cap
        os.remove(self.img_path+'.png')
        # os.remove(self.img_path + '.jpg')
        os.remove(self.img_path + '2.png')
        plt.subplot(1,2,1)
        plt.imshow(img)
        return cap


    def wrong_captcha(self):
        img  = imread(self.img_path+'2.jpg')
        files = glob(self.wrong_cap_dir+'*.jpg')
        d = len(files)+1
        imsave(self.wrong_cap_dir+str(d)+'.jpg',img)

    def date_select(self):
        response = None
        result = False

        ## select day for appointment
        for link in self.br.find_elements_by_link_text("Appointments are available"):
            d = date_to_number(link.get_attribute('href'))
            if self.lower_date <= d <= self.upper_date:
                link.click()
                break
        time.sleep(0.8)
        response = removeNonAscii(self.br.page_source)
        if "Please select an appointment" in response:
            response2 = None

            ## select appointment time
            for link in self.br.find_elements_by_link_text("Book this appointment"):
                link.click()
                break

            time.sleep(0.8)
            response2 = removeNonAscii(self.br.page_source)
            ## fill appointment form
            if "appointment_newAppointmentForm" in response2:
                print time.time() - self.now
                ##solve captcha
                cap = self.captcha_solver(self.br.page_source)
                a = self.br.find_element_by_name("captchaText")
                a.send_keys(cap)
                print time.time() - self.now
                a = self.br.find_element_by_name("lastname")
                a.send_keys(self.last_name)
                a = self.br.find_element_by_name("firstname")
                a.send_keys(self.first_name)
                a = self.br.find_element_by_name("email")
                a.send_keys(self.email)
                a = self.br.find_element_by_name("emailrepeat")
                a.send_keys(self.repeat_email)
                a = self.br.find_element_by_name("fields[0].content")
                a.send_keys(self.repeat_email)
                print time.time() - self.now
                # self.br['passnummer'] = 'ALAN71954'
                time.sleep(15)

    def search_bot(self):
        while 1:
            time.sleep(0.5)
            # try:
            self.now = time.time()
            # self.br = webdriver.PhantomJS(desired_capabilities=self.dcap)
            # self.br = webdriver.Firefox(executable_path="/home/azhar/Downloads/geckodriver")
            self.br.get(self.app_link)
            print time.time()-self.now
            # cap = self.captcha_solver(contents)
            # c = contents.get_data()

            cap = self.captcha_solver(self.br.page_source)
            print time.time()-self.now
            a = self.br.find_element_by_name("captchaText")

            # print cap2
            # time.sleep(1)
            a.send_keys(cap)
            # time.sleep(0.5)
            # contents1 = removeNonAscii(self.br.page_source)
            a.send_keys(Keys.RETURN)
            # contents1 = removeNonAscii(self.br.page_source)
            print time.time() - self.now
            im2 = imread(self.img_path+'.jpg')
            os.remove(self.img_path+'.jpg')
            time.sleep(0.8)
            print time.time() - self.now
            contents = removeNonAscii(self.br.page_source)
            # while contents == contents1:
            #     time.sleep(0.1)
            #     contents = removeNonAscii(self.br.page_source)

            if self.cap_fail_msg in contents:
                plt.subplot(1, 2, 2)
                # plt.imshow(im2)
                # plt.show()
                self.wrong_captcha()

            elif self.no_app_msg in contents:
                continue

            elif self.other_month_msg in contents:
                continue

            elif self.app_available_msg in contents:
                print "found date"
                self.date_select()

            else:
                cap = self.captcha_solver(self.br.page_source)
                self.odd.write(contents)
                self.odd.write('\n\n\n\n')
            self.br.close()
            # except:
            #     continue