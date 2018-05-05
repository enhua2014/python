from datetime import date
import datetime
import tushare as ts
import pandas as pd

def interval_increase(code, date_str_start, interval):
    date_start = datetime.datetime.strptime(date_str_start, '%Y-%m-%d')
    date_end = date_start + datetime.timedelta(days = interval)
    date_str_start = date_start.strftime('%Y-%m-%d')
    date_str_end = date_end.strftime('%Y-%m-%d')
    
    k_data = ts.get_k_data(code, date_str_start, date_str_end)
    interval_end = k_data.iat[len(k_data) - 1, 2]
    interval_start = k_data.iat[0, 2]
    
    #print(interval_start, '/', interval_end, '/', len(k_data), '/', date_str_start, '/', date_str_end)
    
    return str(round((interval_end - interval_start) * 100 / interval_start, 2)) + "%"


# ∏˘æ›»’∆⁄µƒø™ º∫ÕΩ· ¯£¨ªÒ»°»’∆⁄∑∂Œß
def get_date_list(date_str_start, date_str_end):
    date_start = datetime.datetime.strptime(date_str_start, '%Y-%m-%d')
    date_end = datetime.datetime.strptime(date_str_end, '%Y-%m-%d')
    
    dates = []
    
    while date_start <= date_end:
        dates.append(date_start.strftime('%Y-%m-%d'))
        date_start += datetime.timedelta(days=1)
    
    return dates


# ƒ¨»œVOL
def get_default_vol(code):
    if code.startswith('002'):
        vol = 500
    elif code.startswith('300'):
        vol = 500
    elif code.startswith('6'):
        vol = 1000
    elif code.startswith('0'):
        vol = 1000
    
    return vol


# π…∆±∑∂Œß
def get_stock_range(market):
    cyb = range(300001, 300999)
    sha = range(600000, 604999)
    zxb = [ '00' + str(zx) for zx in range(2001, 3000) ]
    sza = [ str(sz).zfill(6) for sz in range (1, 2000) ]
    
    if market == 'cy':
        stock_range = cyb
    elif market == 'sh':
        stock_range = sha
    elif market == 'sz':
        stock_range = xza
    elif market == 'zx':
        stock_range = zxb
    elif market == 'all':
        stock_range = list(cyb) + list(sha) + zxb + sza
    
    return stock_range


# ∏˘æ›π…∆±¥˙¬ÎªÒ»°¥Ûµ• ˝æ›
def dd(stock_code, date_val = date.today(), vol = 0):
    if vol == 0:
        vol = get_default_vol(stock_code)
    
    result = ts.get_sina_dd(stock_code, date_val, vol)

    return result


# ªÒ»°À˘”–µƒ¥Ûµ• ˝æ›
def dd_all(market = 'all', date_val = date.today()):
    result = []
    stock_range = get_stock_range(market)
    
    for stock in stock_range:
        result.append(dd(str(stock), date_val))

    date_str = str(date_val)
    result = pd.concat(result)
    #result.to_excel("C:\\Users\\enhua\\Desktop\\python_script\\dd(" + date_str + ").xlsx", sheet_name=date_str)

    return result


# ¥Ûµ•æª∂Ó
def dd_net(stock_code, date_val = date.today(), vol = 0):
    if vol == 0:
        vol = get_default_vol(stock_code)

    try:
        dd = ts.get_sina_dd(stock_code, date_val, vol)
        
        if dd is not None:
            buy = dd[dd["type"] == "\u4e70\u76d8"]
            sell = dd[dd["type"] == "\u5356\u76d8"]
            
            buy_amount = (buy["price"] * buy["volume"]).sum() / 10000
            sell_amount = (sell["price"] * sell["volume"]).sum() / 10000
            
            stock_name = dd.head(1)["name"].sum()
            
            result = stock_code + "|" + stock_name.rjust(7) + ": "
            result += str(round(buy_amount)).rjust(7) + " - " # ¬ÚΩ∂Ó (\u4e70)
            result += str(round(sell_amount)).rjust(7) + " = " # ¬ÙΩ∂Ó (\u5356)
            result += str(round(buy_amount - sell_amount)).rjust(7) + "(\u51c0\u989d, \u4e07\u5143)" # æª∂Ó
            result += " " + date_val
            
            #print(result)
            
            result_list = []
            result_list.append(stock_code)
            result_list.append(stock_name)
            result_list.append(round(buy_amount))
            result_list.append(round(sell_amount))
            result_list.append(round(buy_amount - sell_amount))
            
            return result_list
# else:
#    print("\u6570\u636e\u83b7\u53d6\u5931\u8d25!")
    except:
        print("dd_net exception occur!")

# ªÒ»°À˘”–µƒ¥Ûµ•æª∂Ó
def dd_net_all(market = "all", date_val = date.today()):
    stock_range = get_stock_range(market)
    
    code_list, name_list, buy_list, sell_list, net_list, date_list, week_increase_list, month_increase_list = [], [], [], [], [], [], [], []

    try:
        for stock in stock_range:
            dd_net_list = dd_net(str(stock), date_val)
            if dd_net_list is not None:
                code_list.append(dd_net_list[0])
                name_list.append(dd_net_list[1])
                buy_list.append(dd_net_list[2])
                sell_list.append(dd_net_list[3])
                net_list.append(dd_net_list[4])
                date_list.append(date_val)
                week_increase = interval_increase(str(stock), date_val, 7)
                month_increase = interval_increase(str(stock), date_val, 30)
                week_increase_list.append(week_increase)
                month_increase_list.append(month_increase)

        net_all_data = { "code": code_list, "name": name_list, "buy": buy_list, "sell": sell_list, "net": net_list, "date": date_list, "week_incr": week_increase_list, "month_incr": month_increase_list }
    
        net_all_df = pd.DataFrame(net_all_data)

        real_time_all = ts.get_today_all()
        result = pd.merge(net_all_df, real_time_all, how="inner", on="code")
        
        date_str = str(date_val)
        #result[["code", "name_x", "buy", "date", "sell", "net", "changepercent", "trade", "open", "high", "low", "volume", "turnoverratio", "amount", "per", "pb", "mktcap", "nmc"]].sort_values(["net"], ascending=False).to_excel("C:\\Users\\enhua\\Desktop\\python_script\\dd_net(" + date_str + ").xlsx", sheet_name=date_str)
        
        #print(result[["code", "name_x", "buy", "sell", "net", "changepercent", "date", "week_incr", "month_incr"]].sort_values(["net"], ascending=False))
        
        return result[["code", "name_x", "buy", "sell", "net", "changepercent", "date", "week_incr", "month_incr"]].sort_values(["net"], ascending=False)
    
    except:
        print("dd_net_all exception occur!")


# ªÒ»°“ª∏ˆ ±º‰∂Œƒ⁄£¨¥Ûµ•æª¡˜»Î«∞ num √˚µƒπ…∆±«Èøˆ
def dd_net_in_dates(date_start_str, date_end_str, num = "5", market = "all"):
    dd_net_list = []
    
    for date_str in get_date_list(date_start_str, date_end_str):
        dd_net_one_day = dd_net_all(market, date_str)
        if dd_net_one_day is not None:
            print(dd_net_one_day.head(num))
            dd_net_list.append(dd_net_one_day.tail(num))
            dd_net_list.append(dd_net_one_day.head(numan))

    result = pd.concat(dd_net_list)

    return result

def dd_ana():
    return dd_net_in_dates("2018-4-12", "2018-4-13")

# ∑µªÿ…œ“ª∏ˆºæ∂»£¨”√listµƒ–Œ Ω±Ì æ
def pre_season():
    d = date.today()
    y = d.year
    m = d.month
    
    if m == 1 or m == 2 or m == 3:
        s = 1
    elif m == 4 or m == 5 or m == 6:
        s = 2
    elif m == 7 or m == 8 or m == 9:
        s = 3
    elif m == 10 or m == 11 or m == 12:
        s = 4
    
    if s == 1:
        return [ y - 1, 4 ]
    else:
        return [ y, s - 1 ]


# ◊€∫œROE, √´¿˚¬  - gross_profit_rate£¨æª¿˚¬ —°π… - net_profits
def roe(year = 2017, season = 4):
    r = ts.get_profit_data(year, season)
    result = r.loc[(r['roe'] > 15) & (r['gross_profit_rate'] > 50) & (r['net_profits'] > 20), ['code', 'name', 'roe', 'gross_profit_rate', 'net_profit_ratio', 'net_profits', 'business_income']]
        
    print(result)
                   
    date_str = str(date.today())
    #result.to_excel("C:\\Users\\enhua\\Desktop\\python_script\\roe(" + date_str + ").xlsx", sheet_name=date_str)
                   
    return result


# ”™“µ≤ø - ¡˙ª¢∞Ò
def broker(days=5):
    b = ts.broker_tops()
    print(b)
    
    date_str = str(date.today())
    #b.to_excel("C:\\Users\\enhua\\Desktop\\python_script\\broker(" + date_str + ").xlsx", sheet_name=date_str)
    
    return b


# Õ≥º∆¿˙ ∑’«µ¯ÃÏ ˝
def change_statistics(code):
    list = []
    up = 0
    down = 0
    
    k_data = ts.get_k_data(code)
    
    for index, row in k_data.iterrows():
        if index == 0:
            prow = row
        else:
            if row['close'] > prow['close']:
                if down != 0:
                    list.append(-down)
                    down = 0
                up = up + 1
            else:
                if up != 0:
                    list.append(up)
                    up = 0
                down = down + 1
            print(prow['close'], " - ", row['close'], " / ", up, " - ", down)
            prow = row

    if down != 0:
        list.append(-down)
    elif up != 0:
        list.append(up)

    return list


