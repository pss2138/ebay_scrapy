from ebaysdk.finding import Connection as finding
from bs4 import BeautifulSoup
import requests
from collections import Counter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import datetime as dt

def my_appid():
    YOURAPPID = 'ENTER YOUR EBAY APP ID HERE'
    return YOURAPPID

def get_keywords(YOURAPPID):
    Keywords = input('Enter your Keyword(s):\n')
    api = finding(domain='svcs.ebay.com', debug=False, appid=YOURAPPID, config_file=None)
    api_request = {'keywords': Keywords, 'outputSelector': 'SellerInfo'}

    response = api.execute('findItemsByKeywords', api_request)
    soup = BeautifulSoup(response.content, 'lxml')

    totalentries = int(soup.find('totalentries').text)
    items = soup.find_all('item')

    print()
    print() 
    title = []
    data = []
    for item in items:
        item_info = []
        name = item.title.string.lower().strip()
        title = title + name.split(" ")
        cat = item.categoryname.string.lower()
        cat_id = item.categoryid.string.lower()
        price = int(round(float(item.currentprice.string)))
        shippingcost = item.shippingservicecost
        if shippingcost is None:
            shippingcost = 0.0
        else:
            shippingcost = float(shippingcost.string.encode('utf-8'))
        starttime = item.starttime.string
        endtime = item.endtime.string
        url = item.viewitemurl.string

        item_info.extend((name, cat, price, shippingcost, starttime, endtime, url))
        data.append(item_info)

    df = pd.DataFrame(data, columns=['Title', 'Category', 'Price', 'ShippingCost', 'Starttime', 'Endtime', 'Url'])
    df['Starttime'] = df['Starttime'].apply(pd.to_datetime).dt.normalize()
    df['Endtime'] = df['Endtime'].apply(pd.to_datetime).dt.normalize()

    print('-<start>--------------------------------------------------------------------')
    print("Keyword: " + Keywords)
    c = Counter(title)
    recommendation = c.most_common(10)
    print("Keyword Recommended: " + str(recommendation))
    print("Number of Products: " + str(totalentries))
    print('----------------------------------------------------------------------------')
    print("Shipping Cost Distribution: \nCost($)   Top 100 Amounts")
    print(df['ShippingCost'].value_counts())
    print('----------------------------------------------------------------------------')
    df['Sales Day Length'] = (df['Endtime'] - df['Starttime']).dt.days

    print(df)
    print('----------------------------------------------------------------------------')


    return cat_id, df

def analyzing(df):
    while True:
        question = input("\nWould you like to explore more information with the previous keyword?: [yes/no]").lower()
        if question == "yes":
            print('----------------------------------------------------------------------------')
            print("Category Distribution(%): ")
            print(df['Category'].value_counts(normalize=True)*100)
            print('----------------------------------------------------------------------------')
            print("Price Distribution($): " )
            print(df['Price'].quantile([0, 0.25, 0.5, 0.75, 1]))
            print('----------------------------------------------------------------------------')
            print("Start Time Distribution: *** Please refer to the graph.***")
            print('----------------------------------------------------------------------------')
            print("Sales Day Length Distribution(days): ")
            print(df['Sales Day Length'].quantile([0, 0.25, 0.5, 0.75, 1]))

            fig = plt.figure(figsize=[15,15])

            plt.subplot(2,2,1)
            plt.title('Category Distribution')
            cat_pie = df['Category'].value_counts()
            cat_pie.plot(kind='pie', cmap=plt.cm.Pastel1, autopct='%.1f%%', labels=None)
            plt.legend(labels=cat_pie.index, loc="upper right", bbox_to_anchor=(1,1))
            plt.ylabel('')

            plt.subplot(2,2,2)
            plt.title('Price Distribution ($)')
            df['Price'].plot(kind='box', showfliers=False, labels=None)

            plt.subplot(2,2,3)
            plt.title('Start Time Distribution')
            df['Starttime'].hist(bins=30, color='lightgreen')
            plt.xticks(rotation=30)

            plt.subplot(2,2,4)
            plt.title('Sales Day Length (days)')
            df['Sales Day Length'].hist(bins=30)
            plt.show()
            
            break

        elif question == "no":
            return

        else:
            print("\nInvalid Answer. Please type yes or no.")
            continue

def get_related_items(YOURAPPID, cat_id):
    while True:
        question = input("\nWould you like the recommendations of related products?: [yes/no]").lower()   
        if question == "yes":
            url = ('http://svcs.ebay.com/MerchandisingService?OPERATION-NAME=getMostWatchedItems&SERVICE-NAME=MerchandisingService&SERVICE-VERSION=1.1.0&CONSUMER-ID=' + YOURAPPID +'&RESPONSE-DATA-FORMAT=XML&REST-PAYLOAD&maxResults=20&categoryId=' + cat_id)
            url = url.replace(" ", "%20")
            api_result = requests.get(url)
            parsed_doc = BeautifulSoup(api_result.content, 'lxml')
            items = parsed_doc.find_all('item')
            print('----------------------------------------------------------------------------')
            data=[]
            for item in items:
                item_info=[]
                title = item.title.string.strip()
                cat = item.primarycategoryname.string.lower()
                price = int(round(float(item.buyitnowprice.string)))
                shippingcost = int(float(item.shippingcost.string))
                itemurl = item.viewitemurl.string
                watchcount = item.watchcount.string
                
                item_info.extend((title,cat,price,shippingcost,itemurl,watchcount))
                data.append(item_info)
            
            df = pd.DataFrame(data, columns=['Title', 'Category', 'Price', 'ShippingCost', 'Url', 'WatchCount'])
            print(df)
            break

        elif question == "no":
            return

        else:
            print("\nInvalid Answer. Please type yes or no.")
            continue

def get_related_items(YOURAPPID, cat_id):
    while True:
        question = input("\nWould you like the recommendations of related products?: [yes/no]").lower()   
        if question == "yes":
            url = ('http://svcs.ebay.com/MerchandisingService?OPERATION-NAME=getMostWatchedItems&SERVICE-NAME=MerchandisingService&SERVICE-VERSION=1.1.0&CONSUMER-ID=' + YOURAPPID +'&RESPONSE-DATA-FORMAT=XML&REST-PAYLOAD&maxResults=20&categoryId=' + cat_id)
            url = url.replace(" ", "%20")
            api_result = requests.get(url)
            parsed_doc = BeautifulSoup(api_result.content, 'lxml')
            items = parsed_doc.find_all('item')
            print('----------------------------------------------------------------------------')
            data=[]
            for item in items:
                item_info=[]
                title = item.title.string.strip()
                cat = item.primarycategoryname.string.lower()
                price = int(round(float(item.buyitnowprice.string)))
                shippingcost = int(float(item.shippingcost.string))
                itemurl = item.viewitemurl.string
                watchcount = item.watchcount.string
                
                item_info.extend((title,cat,price,shippingcost,itemurl,watchcount))
                data.append(item_info)
            
            df = pd.DataFrame(data, columns=['Title', 'Category', 'Price', 'ShippingCost', 'Url', 'WatchCount'])
            print(df)
            break

        elif question == "no":
            return

        else:
            print("\nInvalid Answer. Please type yes or no.")
            continue

def restart():
    while True:
        question = input('\nWould you like to restart? Enter yes or no.\n').lower()
        if question =='yes':
            main()
        elif question == 'no':
            return
        else:
            print("\nInvalid Answer. Please type yes or no.")
            continue

def main():
    while True:
        YOURAPPID = my_appid()
        cat_id, df = get_keywords(YOURAPPID)
        analyzing(df)
        get_related_items(YOURAPPID, cat_id)
        restart()
        break

if __name__ == "__main__":
    main()