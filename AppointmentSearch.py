import re
from datetime import datetime
import base64
import time
import os
from glob import glob
from mechanize import Browser
import matplotlib.pyplot as plt
from skimage.io import imread,imsave


def date_to_number(text):
    match = re.search(r'\d{2}.\d{2}.\d{4}', text)
    t = datetime.strptime(match.group(), "%d.%m.%Y").date()
    return time.mktime(t.timetuple())


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

        self.odd = open(self.odd_path,'wb')

        if not os.path.exists(self.txt_file):
            fp = open(self.txt_file,'wb')
            fp.write(' ')
            fp.close()


    def captcha_solver(self,content):
        my_file = content.get_data()
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
        img  = imread(self.img_path+'.jpg')
        files = glob(self.wrong_cap_dir+'*.jpg')
        d = len(files)+1
        imsave(self.wrong_cap_dir+str(d)+'.jpg',img)

    def date_select(self):
        response = None
        result = False

        ## select day for appointment
        for link in self.br.links():
            if "Appointments are available" in link.text:
                d = date_to_number(link.url)
                if self.lower_date <= d <= self.upper_date:
                    response = self.br.follow_link(link)
                    break


        if response is not None and "Please select an appointment" in response.get_data():
            response2 = None

            ## select appointment time
            for link in self.br.links():
                if "Book this appointment" in link:
                    response2 = self.br.follow_link(link)
                    break

            ## fill appointment form
            if response2 is not None and "appointment_newAppointmentForm" in response2.get_data():
                self.br.select_form(name='appointment_newAppointmentForm')

                ## Disable all submit controls except for the right one
                for control in self.br.form.controls:
                    if control.type == "submit":
                        control.disabled = True
                control = self.br.form.find_control("action:appointment_addAppointment=Submit")
                control.disabled = False

                ##solve captcha
                cap = self.captcha_solver(response2)
                cap = ''
                self.br['captchaText'] = cap
                self.br['lastname'] = 'turing'
                self.br['firstname'] = 'aalan'
                self.br['email'] = 'turing.aalan@gmail.com'
                self.br['repeat_email'] = 'turing.aalan@gmail.com'
                # self.br['passnummer'] = 'ALAN71954'
                self.br.submit()

    def search_bot(self):
        while 1:
            time.sleep(0.5)
            try:
                self.br = Browser()
                self.br.set_handle_robots(False)
                self.br.addheaders = [("User-agent", "Firefox")]
                contents = self.br.open(self.app_link)
                # cap = self.captcha_solver(contents)
                # c = contents.get_data()

                self.br.select_form(name='appointment_captcha_month')
                for control in self.br.form.controls:
                    if control.type == "submit":
                        control.disabled = True
                control = self.br.form.find_control("action:appointment_showMonth")
                control.disabled = False

                cap = self.captcha_solver(contents)
                # print cap2
                time.sleep(1)
                self.br['captchaText'] = cap
                contents = self.br.submit()
                im2 = imread(self.img_path+'.jpg')
                os.remove(self.img_path+'.jpg')

                if self.cap_fail_msg in contents.get_data():
                    plt.subplot(1, 2, 2)
                    plt.imshow(im2)
                    plt.show()
                    self.wrong_captcha()

                elif self.no_app_msg in contents.get_data():
                    continue

                elif self.other_month_msg in contents.get_data():
                    continue

                elif self.app_available_msg in contents.get_data():
                    print "found date"
                    self.date_select()

                else:
                    self.odd.write(contents.get_data())
                    self.odd.write('\n\n\n\n')
            except:
                continue