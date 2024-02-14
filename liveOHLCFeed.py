
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
from multiprocessing import Process, Value
from datetime import datetime, timedelta


class ohlcStream:
    def __init__(self, interval, stock_code = None, indexCode = None):
        self.stock_code = stock_code
        self.indexCode = indexCode
        self.interval = interval
        self.url = self.__getUrl()

    def __getUrl(self):
        #using google finance web page for price fetching via scrapping
        if(self.stock_code):
            url = "https://www.google.com/finance/quote/{}:NSE".format(self.stock_code)
        elif(self.indexCode):
            url = "https://www.google.com/finance/quote/{}:INDEXNSE".format(self.indexCode)
        else:
            raise Exception("Please provide stock code or index code eg: indexCode = 'NIFTY_50'")
        return url

    def stream(self):
        self.__wait()

        # time(9, 15) <= self.__getCurrentDateTime.time() <= time(15, 30)
        while True:                
            start_price = self.__getCurrentPrice()
            high = low = open = close = start_price

            current_datetime = self.__getCurrentDateTime()
            new_datetime = current_datetime + timedelta(minutes=5) #for now keeping hardcodED interval time to be 5 minutes, to be changed later

            while ((new_datetime.minute != self.__getCurrentDateTime().minute)):
                current_price = self.__getCurrentPrice()
                if current_price != None:
                    if (current_price > high) : 
                        high = current_price

                    if (current_price < low) :
                        low = current_price

                print(new_datetime.minute, self.__getCurrentDateTime().minute)
                close = self.__getCurrentPrice()
            
            print([open, high, low, close])
            yield [self.__getCurrentDateTime().strftime("%Y-%m-%d - %H:%M:%S"), open, high, low, close]

    def streamMP(self):
        self.__wait()

        while True:
            start_price = self.__getCurrentPrice()
            open = start_price
            close = None
            high = Value('d', start_price) 
            low = Value('d', start_price)

            current_datetime = datetime.now()
            new_datetime = current_datetime + timedelta(minutes=5)

            processes = []
            while new_datetime.minute != datetime.now().minute:
                high_process = Process(target=self.update_high_price, args=(high,))
                low_process = Process(target=self.update_low_price, args=(low,))
                high_process.start()
                low_process.start()
                processes.extend([high_process, low_process])
                close = self.__getCurrentPrice()
                print(self.__getCurrentDateTime().minute)

            for process in processes:
                process.join()

            yield [self.__getCurrentDateTime().strftime("%Y-%m-%d - %H:%M:%S"), open, high.value, low.value, close]

        
    def __wait(self):
        #hardcoding interval for 5 minutes for now
        current_minute = self.__getCurrentDateTime().minute    
        minutes_until_next_multiple_of_5 = 5 - (current_minute % 5) if 5 - (current_minute % 5) != 5 else 0
        seconds_until_next_multiple_of_5 = minutes_until_next_multiple_of_5 * 60

        print("connection established wait for {} seconds to start getting data".format(seconds_until_next_multiple_of_5 + 300))
        time.sleep(seconds_until_next_multiple_of_5)


    def __getCurrentPrice(self):
        
        classNameInHtmlOfLiveData = "YMlKec fxKbKc"
        try:
            # print("url : " ,self.url)
            response = requests.get(self.url)
            extract = BeautifulSoup(response.text, 'html.parser')
            current_price = float(extract.find(class_ = classNameInHtmlOfLiveData).text.replace(",",""))
            return current_price
        except Exception as e:
            print("Found exception while price fetching at {} :".format(self.__getCurrentDateTime()), e)
            return None
        
    def __getCurrentDateTime(self):
        return datetime.now()
    
    def __isMarketLive(self):
        time(9, 15) <= self.__getCurrentDateTime.time() <= time(15, 30)

    def update_high_price(self, high):
        current_price = self.__getCurrentPrice()
        if current_price is not None and current_price > high.value:
            high.value = current_price

    def update_low_price(self, low):
        current_price = self.__getCurrentPrice()
        if current_price is not None and current_price < low.value:
            low.value = current_price

        
def stream():
    data = ohlcStream(5, indexCode="NIFTY_50")

    while True:
        price = next(data.streamMP())
        print(price)
    

if __name__ == '__main__':    
    stream()


            


        



    


        
    