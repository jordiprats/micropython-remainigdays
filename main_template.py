
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
sta_if.connect("_SSID_", "_PASSWORD_")
   
import utime
print('sleep 10')
utime.sleep(10)

print('ok')

goal_day, goal_month, goal_hour, goal_minute = (17, 7, 22, 0)
    
    
    
if sta_if.isconnected():
    print('connected')
    while True:
        try:
            import ntptime
            import utime
            year, month, day, hour, minute, second, weekday, yearday = utime.localtime(ntptime.time())

            ts_goal = utime.mktime((year, goal_month, goal_day, goal_hour, goal_minute, 0, 0, 0))

            if ts_goal-ntptime.time() < 0:
                ts_goal = utime.mktime((year+1, goal_month, goal_day, goal_hour, goal_minute, 0, 0, 0))

            ts_diff = ts_goal-ntptime.time()

            days_left = ts_diff/60/60/24

            tm.number(int(days_left))

            utime.sleep(300)
            print('updated days remaining')
        except:
            print('timeout')
            utime.sleep(5)

print('aborting')
