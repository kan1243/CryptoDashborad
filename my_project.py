import tkinter as tk
from tkinter import ttk
import websocket
import json
import threading
import time
from time import strftime

class DashBoard:
    def __init__(self, root):
        self.root = root
        self.root.title('Crypto Dashboard')
        self.root.geometry('800x400')
        self.current_tracker = None
        self.expanded = False

        #create frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill='both', expand=True, padx = 10, pady = 10)

        #separate into left and right frame
        left_frame = ttk.Frame(main_frame, width = 200)
        left_frame.pack(side = tk.LEFT, fill = 'y')

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side = tk.LEFT, fill = 'both', expand = True)

        #create button on the left side frame
        ttk.Button(left_frame, text = 'BTC/USDT', 
                   command = lambda:self.select_coin('BTC/USDT')).pack(fill = 'x',pady = 10)
        ttk.Button(left_frame, text = 'ETH/USDT',
                   command = lambda:self.select_coin('ETH/USDT')).pack(fill = 'x', pady = 10)
        ttk.Button(left_frame, text = 'SOL/USDT',
                   command = lambda:self.select_coin('SOL/USDT')).pack(fill = 'x', pady = 10)
        #expand button
        self.button_show = ttk.Button(left_frame, text = 'show more',
                   command = lambda:self.show_more_less())
        self.button_show.pack(fill = 'x', pady = 20)
        #create hidden button
        self.coin_D = ttk.Button(left_frame, text = 'BNB/USDT',
                                 command = lambda:self.select_coin('BNB/USDT'))
        self.coin_E = ttk.Button(left_frame, text = 'XRP/USDT',
                                 command = lambda:self.select_coin('XRP/USDT'))
        
        #create data border
        self.data_border = tk.Frame(right_frame, bg = '#e5e7eb', padx = 2, pady = 2)
        self.data_border.pack(pady = 20)
        #create data frame in data border
        data_frame = ttk.Frame(self.data_border, padding = 20)
        data_frame.pack()

        #create label to display text in right side
        self.title_label = ttk.Label(data_frame, text = 'Select a coin.', font = ('Arial', 30))
        self.title_label.pack(pady = 20)

        self.price_label = ttk.Label(data_frame, text = 'Price: -', font = ('Arial', 20))
        self.price_label.pack()

        self.change_label = ttk.Label(data_frame, text = 'Change: --(-%)', font = ('Arial', 16))
        self.change_label.pack(pady = 5)

        self.volume_label = ttk.Label(data_frame, text = 'Volume (24 hr): -', font = ('Arial', 16), foreground = 'blue')
        self.volume_label.pack(pady = 5)

        self.update_time_label = ttk.Label(data_frame, text = 'Last Update: -', font = ('Arial', 15), foreground = '#6b7280')
        self.update_time_label.pack(pady = 5)

        #create crypto tracker
        self.BTC_tracker = CryptoTicker(self.price_label, self.change_label,
                                        self.volume_label, self.update_time_label,
                                          'btcusdt', self.data_border)
        self.ETH_ticker = CryptoTicker(self.price_label, self.change_label,
                                       self.volume_label, self.update_time_label,
                                          'ethusdt', self.data_border)
        self.SOL_ticker = CryptoTicker(self.price_label, self.change_label,
                                       self.volume_label, self.update_time_label,
                                         'solusdt', self.data_border)
        self.BNB_ticker = CryptoTicker(self.price_label, self.change_label,
                                       self.volume_label, self.update_time_label,
                                          'bnbusdt', self.data_border)
        self.XRP_ticker = CryptoTicker(self.price_label, self.change_label,
                                       self.volume_label, self.update_time_label,
                                          'xrpusdt', self.data_border)

    def select_coin(self, coin):
        #close opened tracker that open when clicked
        if self.current_tracker:
            self.current_tracker.stop()
            self.current_tracker = None
        #recheck that now tracker did not opened
        if not self.current_tracker:
            self.title_label.config(text = f'{coin}')
            #check which button clicked
            if coin == 'BTC/USDT':
                self.BTC_tracker.start()
                self.current_tracker = self.BTC_tracker

            elif coin == 'ETH/USDT':
                self.ETH_ticker.start()
                self.current_tracker = self.ETH_ticker

            elif coin == 'SOL/USDT':
                self.SOL_ticker.start()
                self.current_tracker = self.SOL_ticker

            elif coin == 'BNB/USDT':
                self.BNB_ticker.start()
                self.current_tracker = self.BNB_ticker

            elif coin == 'XRP/USDT':
                self.XRP_ticker.start()
                self.current_tracker = self.XRP_ticker        

    def show_more_less(self):
        if self.expanded == False:
            self.button_show.pack_forget()
            self.coin_D.pack(fill = 'x', pady = 10)
            self.coin_E.pack(fill = 'x', pady = 10)
            self.button_show.config(text = 'show less')
            self.button_show.pack(fill = 'x', pady = 20)
            self.expanded = True
        else:
            self.coin_D.pack_forget()
            self.coin_E.pack_forget()
            self.button_show.pack_forget()
            self.button_show.config(text = 'show more')
            self.button_show.pack(fill = 'x', pady = 20)
            self.expanded = False


#class update price from web
class CryptoTicker:
    def __init__(self, price_label, change_label, volume_label, update_time_label, coin_sym, data_border):
        self.change_label = change_label
        self.price_label = price_label
        self.volume_label = volume_label
        self.update_time_label = update_time_label
        self.coin = coin_sym
        self.data_border = data_border
        self.is_active = False
        self.ws = None

    def start(self):
        #block error from multi open
        if self.is_active:
            return
        
        self.is_active = True
        url = f"wss://stream.binance.com:9443/ws/{self.coin}@ticker"

        self.ws = websocket.WebSocketApp(url, on_message = self.message_control,
                                         on_error = lambda ws, error:print(f'{self.coin} error: {error}'),
                                         on_open = lambda ws:print(f'{self.coin} connected.'),
                                         on_close = lambda ws, code, msg:print(f'{self.coin} closed'))
        
        threading.Thread(target=self.ws.run_forever, daemon=True).start() #to run websocket along with the app

    def stop(self):
        self.is_active = False
        if self.ws:
            self.ws.close()
            self.ws = None

    #function for handle message from webstock    
    def message_control(self, ws, message):
        #block when try to get message without active
        if not self.is_active:
            return
        
        #collect data
        data = json.loads(message)
        price = float(data['c']) #current price
        change = float(data['p']) #change from previous price
        percent = float(data['P']) #percent change
        volume = float(data['v']) #24hr amount of buy-sell 

        self.price_label.after(0, self.update_display, price, change, percent, volume) 
        '''to output the following variable but not bugging the code'''

    def update_display(self, price, change, percent, volume):
        if not self.is_active:
            return
        
        #set color up to change
        color = "green" if change >= 0 else "red"
        self.price_label.config(text = f"Price: {price:,.2f}", foreground=color)

        #set color border up to change
        border_color = '#d1fae5' if change >= 0 else '#fee2e2'
        self.data_border.config(bg = border_color)

        #apply + or - up to change
        sign = "+" if change >= 0 else ""
        self.change_label.config(
            text=f"{sign}{change:,.2f} ({sign}{percent:.2f}%)",
            foreground=color
        )
        #change Volume
        self.volume_label.config(text = f"Volume (24hr): {volume:,.0f}")

        #change update time
        self.update_time_label.config(text = f"Last Update: {strftime('%H:%M:%S')}")

#create window
root = tk.Tk()
app = DashBoard(root)
root.mainloop()
