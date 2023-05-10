import datetime
import pytz


### headers and stuff

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
'Accept-Language': "en-GB,en-US;q=0.9,en;q=0.8",
"Referer": 'https://www.google.com',
"DNT":'1'}

## Times and dates

yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
bris_yest = yesterday.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%d/%m/%Y')
col_yest = yesterday.astimezone(pytz.timezone("Asia/Colombo")).strftime('%d/%m/%Y')
bris_reverse_yes = yesterday.astimezone(pytz.timezone("Asia/Colombo")).strftime('%Y/%m/%d')
col_reverse_yes = yesterday.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y/%m/%d')

utc_now = pytz.utc.localize(datetime.datetime.utcnow())
col_now = utc_now.astimezone(pytz.timezone("Asia/Colombo"))
bris_now = utc_now.astimezone(pytz.timezone("Australia/Brisbane"))
utc_yest = utc_now - datetime.timedelta(days=1)

utc_reverse_date = datetime.date.strftime(utc_now, '%Y/%m/%d')
col_reverse_date = utc_now.astimezone(pytz.timezone("Asia/Colombo")).strftime('%Y/%m/%d')
bris_reverse_date = utc_now.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y/%m/%d')

utc_date = datetime.date.strftime(utc_now, '%d/%m/%Y')
col_date = utc_now.astimezone(pytz.timezone("Asia/Colombo")).strftime('%d/%m/%Y')
bris_date = utc_now.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%d/%m/%Y')

utc_weekday = utc_now.weekday()
col_weekday = col_now.weekday()
bris_weekday = bris_now.weekday()

utc_ordinal = utc_now.toordinal()
col_ordinal = col_now.toordinal()
bris_ordinal = bris_now.toordinal()

utc_month = datetime.date.strftime(utc_yest, '%m')
utc_year = datetime.date.strftime(utc_yest, '%Y')
utc_day = datetime.date.strftime(utc_yest, '%d')