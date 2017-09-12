import click
from AppointmentSearch_1min import  AppointmentSearch


@click.command()
@click.argument('i')
# @click.option('--model-weights')
@click.option("--long_term", default=0)
@click.option("--timed", default=0)
# @click.option("--n_gpu", type=int, default=1, help='Specify the number of GPUs to be used '
#                                                    'If both n_gpus and gpus are set, then gpus flag will take priority')
def main(i,long_term,timed):

    params = {
        'long_term': long_term,
        'timed': timed,
        'app_link': 'https://service2.diplo.de/rktermin/extern/appointment_showMonth.do?locationCode=isla&request_locale=en&realmId=108&categoryId=205&dateStr=01.09.2017',
        'first_name': 'Muhammad',
        'last_name': 'Jehanzeb',
        'email': '13beesjaved@seecs.edu.pk',
        'repeat_email': '13beesjaved@seecs.edu.pk',
        'passnummer': 'BS0917491',
        'lower_date': '07.08.2017',
        'upper_date': '15.10.2017',
        'img_path': 'data/bot_testing/'+i+'/1',
        'wrong_cap_dir': 'data/bot_testing/wrong_caps/',
        'cap_fail_msg': 'entered text was',
        'no_app_msg': 'New appointments will be made available',
        'other_month_msg': 'Please select another month',
        'app_available_msg': 'Please select a date',
        'odd_path': 'data/bot_testing/curious_case_of_benjamin_button.txt',
        'txt_file': 'data/bot_testing/1.txt',
        'iter_id': 1

    }

    a = AppointmentSearch(params)
    a.search_bot()

if __name__ == '__main__':
    main()
