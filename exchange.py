from datetime import datetime, timedelta
import asyncio
import aiohttp
import platform
import sys

currency = ['USD', 'EUR']


def check_input():
    if len(sys.argv) == 1:
        return 1
    if len(sys.argv) == 2:
        count_days = int(sys.argv[-1])
        if 0 <= count_days <= 10:
            return count_days
        raise ValueError('you can watch only 10 days')
    if len(sys.argv) == 3:
        new_currency = sys.argv[-1]
        currency.append(new_currency)
        count_days = int(sys.argv[-2])
        if 0 <= count_days <= 10:
            return count_days
        raise ValueError('you can watch only 10 days')
    raise ValueError('invalid input')


def args_today():
    today = datetime.today()
    delta = check_input()
    list_days = []
    if delta > 1:
        start = today - timedelta(delta)
        while start < today:
            start += timedelta(1)
            list_days.append(start.strftime('%d.%m.%Y'))
        return list_days
    return [today.strftime('%d.%m.%Y')]


def list_generator():
    return [f'https://api.privatbank.ua/p24api/exchange_rates?json&date={day}' for day in args_today()]


async def exchange(days=None):
    result_list = []
    for url in list_generator():
        async with aiohttp.ClientSession() as session:
            async with await session.get(url, ssl=False) as response:
                result = await response.json()
                date = result['date']
                rates_day = {}
                for el in result['exchangeRate']:
                    if el['currency'] in currency:
                        rates_day[el['currency']] = {'sale': el['saleRateNB'], 'purchase': el['purchaseRateNB']}
                result_list.append({date: rates_day})
    return result_list


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        rate = asyncio.run(exchange())
        print(rate)
