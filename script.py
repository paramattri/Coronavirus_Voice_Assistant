import requests
from bs4 import BeautifulSoup
import pandas as pd
import pyttsx3
import speech_recognition as sr
import re

r=requests.get("https://www.worldometers.info/coronavirus/",headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
c=r.content

soup=BeautifulSoup(c,"html.parser")
tables=pd.read_html(r.text)
table=tables[0]

table_data=table[["Country,Other","TotalCases","TotalDeaths","TotalRecovered"]]
table_data=table_data.drop([0,215,216])
table_data=table_data.fillna(0)
table_data["Country,Other"]=table_data["Country,Other"].apply(lambda x: x.lower())

totals=soup.find_all("div",{'class':"maincounter-number"})

total={}
total["Coronavirus Cases"] = totals[0].find("span").text.replace(" ","")
total["Deaths"] = totals[1].find("span").text.replace(" ","")
total["Recovered"] = totals[2].find("span").text.replace(" ","")

class Data:
    def get_total_cases(self):
        return total["Coronavirus Cases"]
    def get_total_deaths(self):
        return total["Deaths"]
    def get_total_recovered(self):
        return total["Recovered"]

    def get_country_data(self,country):
        store=table_data[table_data['Country,Other']==country]
        return store

def speak(text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

def get_audio():
    r=sr.Recognizer()
    with sr.Microphone() as source:
        audio=r.listen(source,phrase_time_limit=5)
        said=""

        try:
            said=r.recognize_google(audio)
        except Exception as e:
            print("Exception: ",str(e))

    return said.lower()


country_list=list(table_data["Country,Other"])
country_list=[country.lower() for country in country_list]

def main():
    print("Started Program!!")
    data=Data()
    END_PHRASE="stop"
    TOTAL_PATTERNS={
        re.compile("[\w\s]+ total [\w\s]+ cases"):data.get_total_cases,
        re.compile("[\w\s]+ total cases"):data.get_total_cases,
        re.compile("[\w\s]+ total [\w\s]+ deaths"):data.get_total_deaths,
        re.compile("[\w\s]+ total deaths"):data.get_total_deaths,
        re.compile("[\w\s]+ total [\w\s]+ recovered"):data.get_total_recovered,
        re.compile("[\w\s]+ total recovered"):data.get_total_recovered,
    }

    COUNTRY_PATTERNS={
        re.compile("[\w\s]+ cases [\w\s]+"):lambda country: data.get_country_data(country)['TotalCases'],
        re.compile("[\w\s]+ deaths [\w\s]+"):lambda country: data.get_country_data(country)['TotalDeaths'],
        re.compile("[\w\s]+ recovered [\w\s]+"):lambda country: data.get_country_data(country)['TotalRecovered'],
    }

    while True:
        print("Listening..")
        text=get_audio()
        print(text)
        result=None

        for pattern, func in COUNTRY_PATTERNS.items():
            if pattern.match(text):
                words=set(text.split(" "))
                for country in country_list:
                    if country in words:
                        result1=func(country)
                        result=str(list(result1)[0])
                        break

        if result == None:
            for pattern, func in TOTAL_PATTERNS.items():
                if pattern.match(text):
                    result=func()
                    break

        if result:
            speak(result)

        if END_PHRASE in text.split(" "):
            break

main()
