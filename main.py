import gc

from config import wifi_config
from config import utelegram_config

import tm1637
from machine import Pin
tm = tm1637.TM1637(clk=Pin(5), dio=Pin(4))
tm.brightness(1)
tm.write([0, 0, 0, 0])
tm.write([127, 255, 127, 127])

print('leds init')

import network

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.scan()
sta_if.connect(wifi_config['ssid'], wifi_config['password'])

import utime
print('sleep 10')
utime.sleep(10)

print('ok')

goal_day, goal_month, goal_year, goal_hour, goal_minute = (8, 9, 2020, 22, 0)

updated = False

def set_countdown_date(message):
    global updated, utelegram_config

    print(message)

    if str(message['message']['from']['id']) in utelegram_config['masters']:
        print('== SET ==')
        try:
            message_parts = message['message']['text'].split(' ')

            print(str(message_parts))

            if message_parts[1]:
                message_date = message_parts[1].split('/')
                print(str(message_date))

                if message_date[0] and message_date[1] and message_date[2]:
                    goal_day = message_date[0]
                    goal_month = message_date[1]
                    goal_year = message_date[2]
                    updated = True

                    bot.send(message['message']['chat']['id'], 'date set to '+str(goal_day)+'/'+str(goal_month)+'/'+str(goal_year))

                    print('date set to '+str(goal_day)+'/'+str(goal_month)+'/'+str(goal_year))
        except:
            print('invalid command: '+str(message))


try:
    if sta_if.isconnected():
        print('connected')

        import utelegram

        bot = utelegram.ubot(utelegram_config['token'])

        bot.register('/set', set_countdown_date)

        for master in utelegram_config['masters']:
            bot.send(int(master), 'bot starting up')

        while True:
            try:

                for i in range(60):
                    print('read telegram')
                    bot.read_once()
                    if updated:
                        print('date updated')
                        updated = False
                        break
                    print('sleeping')
                    utime.sleep(5)
                    gc.collect()

                import ntptime
                import utime

                print('GOAL: '+str(goal_day)+'/'+str(goal_month)+'/'+str(goal_year))

                year, month, day, hour, minute, second, weekday, yearday = utime.localtime(ntptime.time())

                ts_goal = utime.mktime((goal_year, goal_month, goal_day, goal_hour, goal_minute, 0, 0, 0))

                if ts_goal-ntptime.time() < 0:
                    ts_goal = utime.mktime((year+1, goal_month, goal_day, goal_hour, goal_minute, 0, 0, 0))

                ts_diff = ts_goal-ntptime.time()

                days_left = ts_diff/60/60/24

                if days_left > 9999:
                    raise Exception('days left too big')

                tm.number(int(days_left))

                print('updated days remaining')
            except Exception as e:
                print('runtime exception')
                print(str(e))
                utime.sleep(5)
except Exception as e:
    print('unhandled exception')
    print(str(e))

print('aborting')
