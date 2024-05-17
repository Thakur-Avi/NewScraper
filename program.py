import requests
import json
from bs4 import BeautifulSoup
import mysql.connector



def writing_json(records):
    datas = []
    for record in records:
        data = {"URL":record[0], "KEYWORD":record[1], "TITLE":record[2], "DATE-TIME":record[3], "AUTHOR":record[4]}
        # Write the data to a JSON file
        datas.append(data)
    with open('data.json', 'w') as json_file:
        json.dump(datas, json_file, indent=4)
            
    print(f"\nData for keyword : '{keyword}' successfully extracted to data.json\n")



def web_search(keyword):
    search_url = f"https://news.google.com/search?q={keyword}&hl=en-US&gl=US&ceid=US:en"
    response = requests.get(search_url)
    insert_query = "INSERT INTO store(url, keyword, title, datetime_of_publishing, author) VALUES (%s, %s, %s, %s, %s)"

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        search_results = soup.find_all('div', class_='DP8GD')
        
        for result in search_results:
            link = result.find('a', class_='WwrzSb')['href']
            author = result.find('div', class_='vr1PYe').text
            heading = result.find('a', class_='JtKRv').text
            datetime = result.find('time', class_='hvbAAd')['datetime']
            mycursor.execute(insert_query,(link, keyword, heading, datetime, author))

        mycon.commit()
        print("\nResults saved in database... Loading in JSON...")
        mycursor.execute("SELECT * FROM store WHERE keyword = %s",(keyword,))
        records = mycursor.fetchall()
        writing_json(records)

    else:
        print(f"Failed to fetch data from {keyword}. Status code: {response.status_code}\n")
        


def check_database(keyword):
    mycursor.execute('SELECT * FROM store WHERE keyword = %s',(keyword,))
    records = mycursor.fetchall()
    if(records == []):
        web_search(keyword)
    else:
        mycursor.execute("DELETE FROM store WHERE keyword = %s",(keyword,))
        web_search(keyword)


try:
    mycon = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "1234",
    )

    if mycon.is_connected():
        mycursor = mycon.cursor()
        mycursor.execute("CREATE DATABASE IF NOT EXISTS scrap_store")      #Creating database
        mycursor.execute("USE scrap_store")
        mycursor.execute("""CREATE TABLE IF NOT EXISTS store(
                        url TEXT,
                        keyword TEXT,
                        title VARCHAR(255), 
                        datetime_of_publishing VARCHAR(255),
                        author VARCHAR(255))""")                                   #adding table to store data

        print("MySQL database connected successfully...")
        ans = "yes"
        while(ans.lower() == "yes"):
            keyword = input(f"Enter keyword for Scrapping : ")
            check_database(keyword)
            ans=input("Do you want to Search another keyword? (Yes/No) : ")
        
    else:
        print("Unable to connect to MySQL database! \nPlease Start Over the Program.")



except:
    print("MySQL database not connected. \nCheck credentials and try again.")
