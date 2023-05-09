import time

print("home affairs")
import scrapers.home_affairs

time.sleep(2)

print("treasury")
import scrapers.treasury

time.sleep(2)

print("finance")
import scrapers.finance

time.sleep(2)

print("environment")
import scrapers.environment

time.sleep(2)

import feed_generator