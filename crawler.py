import requests
from bs4 import BeautifulSoup
import urllib
from dominate.util import raw
from dominate.tags import *
import csv
import datetime

#Transfer a result set into a list.
def fun_ResultSet2List(rs):
    r=[]
    for i in rs:
        r.append(i.get_text())
    return r

#Transfer a list into a string.
def fun_Tags2Str(l):
    string=""
    for word in l:
        string = string + word + "; "
    return string
#Save data in a csv file.
def fun_SaveCSV(list_dict,file):
    headers = list( list_dict[0].keys() )
    with open(file,'w',newline='',encoding='utf-8')as f:
        f_csv = csv.DictWriter(f,headers)
        f_csv.writeheader()
        f_csv.writerows(list_dict)

#Extracting data from the gURL, stackoverflow's search results page.
def fun_FetchFromSOF(gURL):
    data = []
    site = requests.get(gURL)
    if site.status_code == 200:
        content = BeautifulSoup(site.content, 'html.parser')
        questions = content.select('.question-summary')[0:10:1] #Extracting the top 10 question content on the page.

        #Extracting topic name, answers number, votes number, asked time, the url, tags and the full question text for every question. 
        for question in questions:
            topic = question.select( '.question-hyperlink')[0].get_text()
            answers = question.select('.status')[0].find('strong').get_text()
            votes = question.select('.votes')[0].find(class_='vote-count-post').get_text()
            askedtime = question.find(class_='started fr').select('.relativetime')[0].get_text()
            url = urllib.parse.urljoin('https://stackoverflow.com', question.select( '.question-hyperlink')[0].get('href'))
            q_site = requests.get(url)
            #Extracting tags and the full question text from the question's page. 
            if q_site.status_code == 200:
                q_content = BeautifulSoup(q_site.content,'html.parser')
                q_text = str(q_content.select('.post-text')[0])
                q_tags = fun_ResultSet2List(q_content.find(class_='post-taglist').select('.post-tag'))
            new_data = {"topic": topic, "url": url, "answers":answers, "votes":votes,"question":q_text,"tags":q_tags,"askedtime":askedtime}
            data.append(new_data)
        print('Successfully Fetching Data From ',gURL)
    else:
        print('Cannot Fetching Data From ',gURL)
    return data

#Run crawler and display the data in html file
def fun_RunCrawler():
    print('Start running!')
    print('Waiting for the crawler...')
    #Extracting data from stackoverflow's search results page for questions with tag android, which are not duplicated and are created within 7 days.
    data_MostVoted=fun_FetchFromSOF('https://stackoverflow.com/search?tab=votes&q=is%3aq+[android]+duplicate%3ano+created%3a7d..')

    #Extracting data from stackoverflow's search results page for questions with tag android, which are not duplicated and are the newest created.
    data_Newest=fun_FetchFromSOF('https://stackoverflow.com/search?tab=newest&q=[android]+duplicate%3ano')

    #Obtain current time
    current_time = datetime.datetime.now()
    time_File = current_time.strftime("%Y%m%d-%H%M")
    time_Html = current_time.strftime("%Y-%m-%d %H:%M")

    fun_SaveCSV(data_MostVoted, './' + time_File + 'MostVoted.csv')
    fun_SaveCSV(data_Newest, './' + time_File + 'Newest.csv')

    #Realease data which are fetched from stackoverflow on the html
    h = html()
    h_head = h.add(head())
    with h_head:
        link(rel='stylesheet', href='./mycss.css'),
        base(target='_blank')
        script(type="text/javascript",src="./myjs.js")
    h_body = h.add(body())
    with h_body:
        div(
                "Loading...",
                img(src="loading.gif",width="30",height="30"),
                id="loading",style="display:none;font-size:20;")
    h_body_div = h_body.add(div(id='content'))
    with h_body_div:
        #button('Update',onclick="$('#loading').show();javascript:location.reload();")
        button('Update',onclick="showLoading();javascript:window.location.href='http://127.0.0.1:5000/update';")
        div('Last Updated Time: ',time_Html,style='float: left',href='/update'),
        div(i('A Crawler From Stack Overflow By Chi Zhang'),style='float: right'),
        raw('<br/>'),
        h1(u'The 10 newest Android-related questions in Stack Overflow.'),
        for idx,data in enumerate(data_Newest):
            details(
                summary(
                    str(idx+1)+'. '+data['topic'][4:], #The extracted topic title initialed with 4 unrelated characters. 

                    a('Links',href=data['url']),
                    p(
                        a('Answers: ',list(filter(str.isdigit,data['answers']))," "),
                        a('Votes: ',list(filter(str.isdigit,data['votes']))," "),
                        a('Tags: ',fun_Tags2Str(data['tags'])),
                        a('Asked Time: ',data['askedtime'])
                    )
                ),
                blockquote(raw(data['question'])), #Presenting the full question text in a drop-down box when clicking on the topic title. 

                raw('<br/><hr/><br/><br/>') #Presenting a cutting line and some blank lines to make the page viewable.
            )
        raw('<br/>')

        h1(u'The 10 most voted Android-related questions posted in the past week in Stack Overflow.')
        for idx,data in enumerate(data_MostVoted):
            details(
                summary(
                    str(idx+1)+'. '+data['topic'][4:], #The extracted topic title initialed with 4 unrelated characters.

                    a('Links',href=data['url']),
                    p(
                        a('Answers: ',list(filter(str.isdigit,data['answers']))," "),
                        a('Votes: ',list(filter(str.isdigit,data['votes']))," "),
                        a('Tags: ',fun_Tags2Str(data['tags'])),
                        a('Asked Time: ',data['askedtime'])
                    )
                ),
                blockquote(raw(data['question'])), #Presenting the full question text in a drop-down box when clicking on the topic title. 

                raw('<br/><hr/><br/><br/>') #Presenting a cutting line and some blank lines to make the page viewable.

            )
        raw('<br/>')

    #Release the html.
    with open('./static/index.html','w',encoding='utf-8') as f:
        f.write(h.render())
    
    print('Finished!')
        
        
