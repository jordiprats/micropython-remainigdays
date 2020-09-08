import gc

debug = False

from config import wifi_config
from config import utelegram_config

import tm1637
from machine import Pin
tm = tm1637.TM1637(clk=Pin(5), dio=Pin(4))
tm.brightness(1)
tm.write([0, 0, 0, 0])
tm.write([127, 255, 127, 127])

if debug: print('leds init')

import network

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.scan()
sta_if.connect(wifi_config['ssid'], wifi_config['password'])

import utime
if debug: print('sleep 10')
utime.sleep(20)

if debug: print('ok')

goal_day, goal_month, goal_year, goal_hour, goal_minute = (8, 9, 2020, 22, 0)

updated = False
display_value = False

def set_countdown_date(message):
    global updated, utelegram_config, goal_day, goal_month, goal_year, display_value

    if debug: print(message)

    if str(message['message']['from']['id']) in utelegram_config['masters']:
        if debug: print('== SET ==')
        try:
            message_parts = message['message']['text'].split(' ')

            if debug: print(str(message_parts))

            if message_parts[1]:
                message_date = message_parts[1].split('/')
                if debug: print(str(message_date))

                if message_date[0] and message_date[1] and message_date[2]:
                    goal_day = int(message_date[0])
                    goal_month = int(message_date[1])
                    goal_year = int(message_date[2])
                    updated = True

                    bot.send(message['message']['chat']['id'], 'date set to '+str(goal_day)+'/'+str(goal_month)+'/'+str(goal_year))

                    if debug: print('date set to '+str(goal_day)+'/'+str(goal_month)+'/'+str(goal_year))

                    display_value = True
        except Exception as e:
            if debug: print('invalid command: '+str(message)+' exception: '+str(e))


try:
    if sta_if.isconnected():
        if debug: print('connected')

        import utelegram

        bot = utelegram.ubot(utelegram_config['token'])

        bot.register('/set', set_countdown_date)

        for master in utelegram_config['masters']:
            bot.send(int(master), 'bot starting up')

        while True:
            try:

                for i in range(60):
                    if debug: print('read telegram')
                    bot.read_once()
                    if updated:
                        if debug: print('date updated')
                        updated = False
                        break
                    if debug: print('sleeping')
                    utime.sleep(5)
                    gc.collect()

                import ntptime
                import utime

                if debug: print('GOAL: '+str(goal_day)+'/'+str(goal_month)+'/'+str(goal_year))

                year, month, day, hour, minute, second, weekday, yearday = utime.localtime(ntptime.time())

                ts_goal = utime.mktime((goal_year, goal_month, goal_day, goal_hour, goal_minute, 0, 0, 0))

                if ts_goal-ntptime.time() < 0:
                    ts_goal = utime.mktime((year+1, goal_month, goal_day, goal_hour, goal_minute, 0, 0, 0))

                ts_diff = ts_goal-ntptime.time()

                days_left = ts_diff/60/60/24

                if days_left > 9999:
                    raise Exception('days left too big')

                if debug: print('days_left: '+str(days_left))

                if display_value:
                    tm.number(int(days_left))

                if debug: print('updated days remaining')
            except Exception as e:
                if debug: print('runtime exception')
                if debug: print(str(e))
                utime.sleep(5)
except Exception as e:
    if debug: print('unhandled exception')
    if debug: print(str(e))

if debug: print('aborting')
