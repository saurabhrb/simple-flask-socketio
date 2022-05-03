import os, sys, traceback, pprint


basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.insert(1, os.path.join(basedir, 'lib','python_binance'))


from binance.client import Client
from binance import ThreadedWebsocketManager

def debug(func=None):
    def wrapper(*args, **kwargs):
        try:
            function_name = func.__func__.__qualname__
        except:
            function_name = func.__qualname__
        print(function_name + '() -->')
        res = func(*args, **kwargs)
        print('<-- ' + function_name + '()')
        return res
    return wrapper

class Futures_position:
    # # default constructor
    # def __init__(self):
    #   self.entryPrice = 0.0
    #   self.isAutoAddMargin = False
    #   self.leverage = 0.0
    #   self.maxNotionalValue = 0.0
    #   self.liquidationPrice = 0.0
    #   self.markPrice = 0.0
    #   self.positionAmt = 0.0
    #   self.symbol = ""
    #   self.unRealizedProfit = 0.0
    #   self.marginType = ""
    #   self.isolatedMargin = 0.0
    #   self.positionSide = ""

    #   self.roe = 0
    #   self.margin_ratio = 0
    
    # copy constructor
    def __init__(self, position):
      self.entryPrice = float(position['entryPrice'])
      self.isAutoAddMargin = bool(position['isAutoAddMargin'])
      self.leverage = int(position['leverage'])
      self.maxNotionalValue = float(position['maxNotionalValue'])
      self.liquidationPrice = float(position['liquidationPrice'])
      self.markPrice = float(position['markPrice'])
      self.positionAmt = float(position['positionAmt'])
      self.symbol = position['symbol']
      self.unRealizedProfit = float(position['unRealizedProfit'])
      self.marginType = position['marginType']
      self.isolatedMargin = float(position['isolatedMargin'])
      self.positionSide = position['positionSide']

      self.roe = 0
      self.margin_ratio = 0
    
    @debug
    def update_mark(self, markPrice):
        self.markPrice = markPrice
        self.unRealizedProfit = self.positionAmt * (self.markPrice - self.entryPrice)
        if self.positionSide == 'SHORT':
          self.unRealizedProfit = -1 * self.unRealizedProfit
        if self.isolatedMargin != 0:
          self.roe = 100 * (self.unRealizedProfit / self.isolatedMargin)

    @debug
    def print(self):
        qty_str = ('%.3f' % self.positionAmt) + self.symbol.upper().split('USDT')[0] + '(' + ('%.3f' % (self.positionAmt * self.markPrice)) + 'USDT)'
        if self.unRealizedProfit > 0:
          PNL = '+' + ('%.3f' % self.unRealizedProfit) + ' USDT '
        else:
          PNL = ('%.3f' % self.unRealizedProfit) + ' USDT '
        if self.roe > 0:
          ROE = '+' + ('%.3f' % self.roe) + '%'
        else:
          ROE = ('%.3f' % self.roe) + '%'

        p = self.positionSide + ' ' + self.symbol.upper() + ' x' + ('%d' % self.leverage) + ' ' + qty_str + ' ' + ('%.3f' % self.entryPrice) + ' ' + ('%.3f' % self.markPrice) + ' ' + ('%.3f' % self.liquidationPrice) + ' ' + ('%.3f' % self.margin_ratio) + '% ' + ('%.3f' % self.isolatedMargin) + '(' + str(self.marginType) + ') ' + PNL + ROE
        return p
        
    @staticmethod
    def html_tabel_head():
        p = '''
        <tr>
            <th>Position</th>
            <th>Symbol</th>
            <th>Leverage</th>
            <th>Size</th>
            <th>Entry Price</th>
            <th>Mark Price</th>
            <th>Liq. Price</th>
            <th>Margin Ratio%</th>
            <th>Margin</th>
            <th>PNL</th>
            <th>ROE%</th>
        </tr>
        '''
        return p

    def html(self):
        qty_str = ('%.3f' % self.positionAmt) + ' ' + self.symbol.upper().split('USDT')[0] + ' (' + ('%.3f' % (self.positionAmt * self.markPrice)) + ' USDT)'
        if self.unRealizedProfit > 0:
          PNL = '+' + ('%.3f' % self.unRealizedProfit) + ' USDT '
        else:
          PNL = ('%.3f' % self.unRealizedProfit) + ' USDT '
        if self.roe > 0:
          ROE = '+' + ('%.3f' % self.roe) + '%'
        else:
          ROE = ('%.3f' % self.roe) + '%'
        p = '''
        <tr>
            <td>''' + self.positionSide + '''</td>
            <td>''' + self.symbol.upper() + '''</td>
            <td>''' + ('%d' % self.leverage) + '''x</td>
            <td>''' + qty_str + '''</td>
            <td>''' + ('%.3f' % self.entryPrice) + ''' USDT</td>
            <td>''' + ('%.3f' % self.markPrice)+ ''' USDT</td>
            <td>''' + ('%.3f' % self.liquidationPrice) + ''' USDT</td>
            <td>''' + ('%.3f' % self.margin_ratio) + '''%</td>
            <td>''' + ('%.3f' % self.isolatedMargin) + ''' USDT (''' + str(self.marginType) + ''')</td>
            <td>''' + PNL  + '''</td>
            <td>''' + ROE + '''</td>
        </tr>
        '''
        return p

class BINANCE:
  def __init__(self, api_key, api_secret, testnet=False):
    self.api_key = api_key
    self.api_secret = api_secret
    self.testnet = testnet
    self.client = Client(api_key=self.api_key, api_secret=self.api_secret, testnet=self.testnet)
    self.positions = {}
    self.assets = {}
    self.balance = 0
    self.positions_str = ''
    self.positions_html = ''
    self.sub_client = None

  @debug
  def update_position(self, msg):
    if msg['data']['s'] in self.positions:
      self.positions[msg['data']['s']].update_mark(float(msg['data']['p']))
    self.print_positions()

  @debug
  # updates self.positions_str & self.positions_html
  # which gets streamed to flask console and socketio front-end stream
  def print_positions(self):
    self.positions_str = ''
    self.positions_html = '''<table style="width:100%; text-align: center" >'''
    print('---------------------------------')
    k=1
    for symb in self.positions.keys():
      if k!=1:
        self.positions_str += '\n'
      self.positions_str += str(k) + self.positions[symb].print()
      self.positions_html += self.positions[symb].html()
      k+=1
    print(self.positions_str)
    print('---------------------------------')
    self.positions_html += '''
    </table>
    '''

  @debug
  def start_webstream(self):
    if self.sub_client == None:
      self.sub_client = ThreadedWebsocketManager(testnet=self.testnet, api_key=self.api_key, api_secret=self.api_secret, daemon=True)
      self.sub_client.start()
      self.sub_client.start_futures_socket(callback=self.sub_callback)
    else:
      print('Stream already running!\n Not starting again')
  
  @debug
  def start_mark_price_ticker_stream(self, lst_pairs=[]):
    if self.sub_client:
        for pairs in lst_pairs:
            self.sub_client.start_symbol_mark_price_socket(callback=self.sub_callback, symbol=pairs.upper(), fast=False)
    else:
        print('start_webstream() was not called at init time')
  
  def sub_callback(self,msg):
    try:
        if msg:
          if 'data' in msg:
            if msg['data']['e'] == 'markPriceUpdate':
              self.update_position(msg)
            elif msg['data']['e'] == 'ORDER_TRADE_UPDATE':
              # TODO, affects self.positions
              pprint.pprint(msg)
              # self.get_open_trades()
          elif msg['e'] == 'ACCOUNT_UPDATE':
            # TODO, affects balance
            pprint.pprint(msg)
    except:
        print(traceback.format_exc())
    print("")

  # def sub_callback(self, data_type: 'SubscribeMessageType', event: 'any'):
  #   if data_type == SubscribeMessageType.RESPONSE:
  #       print("Event ID: ", event)
  #   elif  data_type == SubscribeMessageType.PAYLOAD:
  #       if(event.eventType == "ACCOUNT_UPDATE"):
  #           print("Event Type: ", event.eventType)
  #           print("Event time: ", event.eventTime)
  #           # print("Transaction time: ", event.transactionTime)
  #           # print("=== Balances ===")
  #           # PrintMix.print_data(event.balances)
  #           # print("================")
  #           # print("=== Positions ===")
  #           # PrintMix.print_data(event.positions)
  #           # print("================")
  #       elif(event.eventType == "ORDER_TRADE_UPDATE"):
  #           print("Event Type: ", event.eventType)
  #           print("Event time: ", event.eventTime)
  #           # print("Transaction Time: ", event.transactionTime)
  #           # print("Symbol: ", event.symbol)
  #           # print("Client Order Id: ", event.clientOrderId)
  #           # print("Side: ", event.side)
  #           # print("Order Type: ", event.type)
  #           # print("Time in Force: ", event.timeInForce)
  #           # print("Original Quantity: ", event.origQty)
  #           # print("Position Side: ", event.positionSide)
  #           # print("Price: ", event.price)
  #           # print("Average Price: ", event.avgPrice)
  #           # print("Stop Price: ", event.stopPrice)
  #           # print("Execution Type: ", event.executionType)
  #           # print("Order Status: ", event.orderStatus)
  #           # print("Order Id: ", event.orderId)
  #           # print("Order Last Filled Quantity: ", event.lastFilledQty)
  #           # print("Order Filled Accumulated Quantity: ", event.cumulativeFilledQty)
  #           # print("Last Filled Price: ", event.lastFilledPrice)
  #           # print("Commission Asset: ", event.commissionAsset)
  #           # print("Commissions: ", event.commissionAmount)
  #           # print("Order Trade Time: ", event.orderTradeTime)
  #           # print("Trade Id: ", event.tradeID)
  #           # print("Bids Notional: ", event.bidsNotional)
  #           # print("Ask Notional: ", event.asksNotional)
  #           # print("Is this trade the maker side?: ", event.isMarkerSide)
  #           # print("Is this reduce only: ", event.isReduceOnly)
  #           # print("stop price working type: ", event.workingType)
  #           # print("Is this Close-All: ", event.isClosePosition)
  #           # if not event.activationPrice is None:
  #           #     print("Activation Price for Trailing Stop: ", event.activationPrice)
  #           # if not event.callbackRate is None:
  #           #     print("Callback Rate for Trailing Stop: ", event.callbackRate)
  #           self.update_position(event)
  #       elif(event.eventType == "listenKeyExpired"):
  #           print("Event: ", event.eventType)
  #           print("Event time: ", event.eventTime)
  #           print("CAUTION: YOUR LISTEN-KEY HAS BEEN EXPIRED!!!")
  #       elif(event.eventType == "markPriceUpdate"):
  #           # print("Event: ", event.eventType)
  #           # print("Event time: ", event.eventTime)
  #           # PrintBasic.print_obj(event)
  #           self.update_position(event)
  #       else:
  #           print("Event: ", event.eventType)
  #           print("Event time: ", event.eventTime)
  #           # PrintBasic.print_obj(event)
  #       self.print_positions()
  #   else:
  #       print("Unknown Data:")
  #   print()
  
  @debug
  def get_account_info_v2(self):
    print('------------')
    result = self.client.get_account_information_v2()
    print('------------')
    if result.totalMarginBalance > 0:
      margin_ratio = (result.totalMaintMargin/result.totalMarginBalance)*100
    else:
      margin_ratio = 0.0
    # print("canDeposit: ", result.canDeposit)
    # print("canWithdraw: ", result.canWithdraw)
    # print("feeTier: ", result.feeTier)
    # print("maxWithdrawAmount: ", result.maxWithdrawAmount)
    # print("totalInitialMargin: ", result.totalInitialMargin)
    # print("totalMaintMargin: ", result.totalMaintMargin)
    # print("totalMarginBalance: ", result.totalMarginBalance)
    # print("totalOpenOrderInitialMargin: ", result.totalOpenOrderInitialMargin)
    # print("totalPositionInitialMargin: ", result.totalPositionInitialMargin)
    # print("totalunRealizedProfit: ", result.totalunRealizedProfit)
    # print("totalWalletBalance: ", result.totalWalletBalance)
    # print("totalCrossWalletBalance: ", result.totalCrossWalletBalance)
    # print("totalCrossUnPnl: ", result.totalCrossUnPnl)
    # print("availableBalance: ", result.availableBalance)
    # print("maxWithdrawAmount: ", result.maxWithdrawAmount)
    # print("updateTime: ", result.updateTime)
    # print("=== Assets ===")
    # PrintMix.print_data(result.assets)
    for asset in result.assets:
      if asset.availableBalance > 0:
        self.assets[asset.asset.upper()] = asset
    for position in result.positions:
      if position.symbol.upper() in self.positions and self.positions[position.symbol.upper()].positionSide == position.positionSide:
        self.positions[position.symbol.upper()].margin_ratio = margin_ratio
        self.positions[position.symbol.upper()].isolatedMargin = position.positionInitialMargin
  
  @debug
  def get_futures_balance(self):
    result = self.client.futures_account_balance()
    for res in result:
      if res['asset'] == "USDT":
        self.balance = float(res['balance'])
    return self.balance
  
  # @debug
  # def get_balance_V2(self, asset="USDT"):
  #   # self.client.get_asset_balance(asset)
  #   self.client.futures_account_balance()
  #   result = self.client.get_balance_v2()
  #   for res in result:
  #     if res.asset == "USDT":
  #       self.balance = res.balance
  #   return self.balance

  @debug
  def get_leverage_bracket(self, symbol=''):
    result = self.client.get_leverage_bracket(symbol)
    # PrintMix.print_data(result)
    return result
  
  @debug
  def get_position(self):
    result = self.client.get_position()
    # PrintMix.print_data(result)
    return result

  @debug
  def get_position_v2(self):
    result = self.client.get_position_v2()
    # PrintMix.print_data(result)
    return result
  
  @debug
  def get_open_trades(self):
    res = self.client.futures_position_information()
    lst_pairs = []
    for position in res:
      if float(position['positionAmt']) > 0.0 :
        pprint.pprint(position)
        self.positions[position['symbol'].upper()] = Futures_position(position)
        self.positions[position['symbol'].upper()].print()
        lst_pairs.append(position['symbol'])
        # self.get_leverage_bracket(position.symbol)

    # get margin values of orders and assets
    # TODO
    # self.get_account_info_v2()
    print('My positions : ' + str(len(self.positions)))

    self.start_mark_price_ticker_stream(lst_pairs)
    return lst_pairs
  
  @debug
  def get_position_margin_change_history(self, symbol):
    result = self.client.get_position_margin_change_history(symbol=symbol)
    # PrintBasic.print_obj(result)
    pprint.pprint(result)

  @debug
  def get_account_trades(self,symbol):
    result = self.client.get_account_trades(symbol=symbol)
    pprint.pprint(result)
  
  # class LeverageBracket:
  #   def __init__(self):
  #       self.symbol = ""
  #       self.brackets = list()
  # class Bracket:
  #   def __init__(self):
  #       self.bracket = 0
  #       self.initialLeverage = 0
  #       self.notionalCap = 0.0
  #       self.notionalFloor = 0.0
  #       self.maintMarginRatio = 0.0
  #       self.cum = 0.0

  @debug
  def get_leverage_bracket(self, symbol, lev):
    result = self.client.get_leverage_bracket()
    for res in result:
      if res.symbol == symbol:
        for l in res.brackets:
          if l.initialLeverage == lev:
            pprint.pprint(l)
          break
    return result

  @debug
  def get_order(self, symbol, orderid):
    result = self.client.get_order(symbol=symbol, orderId=orderid)
    pprint.pprint(result)

