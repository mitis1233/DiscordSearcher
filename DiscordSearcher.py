from random import uniform
import sys, os, requests, json, time, re, sqlite3
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
from PyQt5.QtCore import QFile, pyqtSignal, QThread, QSettings,Qt
from UI_Main import Ui_MainWindow
from UI_Login import Ui_Form

class TutorialThread(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.stop1=0
    def stop(self):
        self.Discord.switch='False'
        self.stop1=1
    def run(self):
        self.stop1=0
        global window
        self.window=window
        self.window.ui.pushButton_2.setEnabled(False)
        self.window.ui.pushButton_4.setEnabled(True)
        self.Discord = DiscordRun()
        header=LoginWindow().settings.value('header')
        self.Discord.header['authorization']=header[0]
        self.Discord.header['cookie']=header[1]
        self.Discord.header['user-agent']=header[2]
        self.Discord.header['x-super-properties']=header[3]
        print(self.Discord.header)
        self.Discord.ctrateDB()
        if self.window.fastmode==1:
            self.fastmode()
        else:
            self.normalmode()
            
    def normalmode(self):
        txtdata = self.window.ui.textEdit.toPlainText()
        lines = txtdata.splitlines()
        for linecount in range(len(lines)):
            self.Discord.url=lines[linecount]
            PageCount=1
            self.Discord.searchLog()
            if self.stop1!=1:
                self.Discord.switch = 'True'
                print('執行網址:',self.Discord.url)
                self.window.ui.listWidget.addItem('執行網址:'+self.Discord.url)
            while self.Discord.switch == 'True':
                print('進度: 第',PageCount,'頁')
                self.window.ui.listWidget.addItem('進度: 第'+str(PageCount)+'頁')
                time.sleep(0.05)
                self.window.ui.listWidget.scrollToBottom()
                try:
                    self.Discord.searchA()
                    self.Discord.DataBase()
                    self.Discord.Data.clear()
                except:
                    self.window.ui.listWidget.addItem('錯誤: 無法取得資料 (401為登入失敗)')
                    self.window.ui.listWidget.addItem('stop 10s')
                    time.sleep(0.05)
                    self.window.ui.listWidget.scrollToBottom()
                    time.sleep(9.95)
                print(self.Discord.LogID)
                if self.Discord.LogID!='0':
                    try:
                        self.Discord.api=self.Discord.searchB()
                    except:
                        self.window.ui.listWidget.addItem('錯誤: 無法取得此網址最後一筆資料 直接結束')
                        self.Discord.LogID='0'
                        self.window.ui.listWidget.addItem('stop 10s')
                        time.sleep(0.05)
                        self.window.ui.listWidget.scrollToBottom()
                        time.sleep(9.95)
                    print('stop 5~8s')
                    self.window.ui.listWidget.addItem("stop 5~8s")
                    time.sleep(0.05)
                    self.window.ui.listWidget.scrollToBottom()
                    time.sleep(uniform(5,8))
                else:
                    self.Discord.switch='False'
                    print('End')
                    self.window.ui.listWidget.addItem('END')
                    self.window.ui.listWidget.addItem('=-=-=-=-=-=')
                    time.sleep(0.05)
                    self.window.ui.listWidget.scrollToBottom()
                PageCount+=1
            linecount+=1
        self.window.ui.listWidget.addItem('任務完成')
        time.sleep(0.05)
        self.window.ui.listWidget.scrollToBottom()
        self.window.ui.pushButton_2.setEnabled(True)
        self.window.ui.pushButton_4.setEnabled(False)
        
    def fastmode(self):
        txtdata = self.window.ui.textEdit.toPlainText()
        lines = txtdata.splitlines()
        for linecount in range(len(lines)):
            
            self.Discord.url=lines[linecount]
            self.Discord.searchLog()
            if self.stop1!=1:
                print('執行網址:',self.Discord.url)
                self.window.ui.listWidget.addItem('執行網址:'+self.Discord.url)
            try:
                self.Discord.searchA()
                self.Discord.DataBase()
                self.Discord.Data.clear()
            except:
                self.window.ui.listWidget.addItem('錯誤: 無法取得資料 (401為登入失敗)')
                self.window.ui.listWidget.addItem('stop 10s')
                time.sleep(0.05)
                self.window.ui.listWidget.scrollToBottom()
                time.sleep(9.95)
            print('stop 5~8s')
            self.window.ui.listWidget.addItem("stop 5~8s")
            self.window.ui.listWidget.addItem('=-=-=-=-=-=')
            time.sleep(0.05)
            self.window.ui.listWidget.scrollToBottom()
            time.sleep(uniform(5,8))
            linecount+=1
            if self.stop1==1:
                break
            
        self.window.ui.listWidget.addItem('任務完成')
        time.sleep(0.05)
        self.window.ui.listWidget.scrollToBottom()
        self.window.ui.pushButton_2.setEnabled(True)
        self.window.ui.pushButton_4.setEnabled(False)



class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon('D://DiscordSearcher//ico.ico'))
        self.ui.pushButton_4.setEnabled(False)
        self.thread=TutorialThread()
        self.file=''
        self.fastmode=0
        self.readFile()
        self.ui.checkBox.stateChanged.connect(self.checkBox)
        self.ui.pushButton.clicked.connect(self.pushButton_Click_URL)#Discord群組網址
        self.ui.pushButton_2.clicked.connect(self.pushButton_Click_Search)#開始搜尋
        self.Login_window = LoginWindow()
        self.ui.pushButton_3.clicked.connect(self.Login_window.show)#登入設定
        self.ui.pushButton_4.clicked.connect(self.pushButton_Click_Stop)#停止搜尋

    def PrintErr(self,ERR):
        self.ui.listWidget.addItem(str(ERR))
        
    def pushButton_Click_URL(self):
        lineEditTXT=self.ui.lineEdit.text().strip()
        if lineEditTXT == '':
            self.writeFile()
        else:
            self.ui.lineEdit.clear()
            self.ui.textEdit.append(lineEditTXT)
            self.writeFile()
            
    def pushButton_Click_Stop(self):
        self.ui.pushButton_4.setEnabled(False)
        self.thread.stop()
        
    def pushButton_Click_Search(self):
        self.thread.start()
        
    def checkBox(self, state):
        if state == Qt.Checked:
            self.fastmode=1
        else:
            self.fastmode=0
            
    def readFile(self):
        self.file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'DiscordURL.txt')
        print(self.file)
        fname = (self.file, 'Txt (*.txt)')
        if fname[0]:
            f = QFile(fname[0])
            try:
                f = open(fname[0], "r")
            except:
                f = open(fname[0], "w")
                f = open(fname[0], "r")
            with f:
                data = f.read()
                self.ui.textEdit.setText(data)
                f.close()

    def writeFile(self):
        fname = (self.file, 'Txt (*.txt)')
        if fname[0]:
            f = open(fname[0], "w")
            with f:
                data = self.ui.textEdit.toPlainText()
                f.write(data)
        f.close()
        
    def closeEvent(self, event):
        QApplication.closeAllWindows()

class LoginWindow(QWidget):
    def __init__(self):
        super(LoginWindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon('D://DiscordSearcher//ico.ico'))
        self.ui.pushButton.clicked.connect(self.set1)
        self.settings = QSettings('header')
        self.ui.lineEdit.setText(self.settings.value('header')[0])
        self.ui.lineEdit_2.setText(self.settings.value('header')[1])
        self.ui.lineEdit_3.setText(self.settings.value('header')[2])
        self.ui.lineEdit_4.setText(self.settings.value('header')[3])
        
    def set1(self):
        
        self.settings.setValue('header', [self.ui.lineEdit.text().strip(), self.ui.lineEdit_2.text().strip(), self.ui.lineEdit_3.text().strip(),self.ui.lineEdit_4.text().strip()])
        self.close()
        #print(self.settings.value('header'))


class DiscordRun:
    def __init__(self):
        self.url = ''
        self.api = ''
        self.LogID = '0'
        self.LogLen = 0
        self.switch= 'True'
        self.Data={}
        self.header={
                    'authorization': '',
                    'cookie': '',
                    'referer': '',
                    'user-agent': '',
                    'x-super-properties': ''
                    }
                    
    def searchLog(self):
        self.api='https://discord.com/api/v8/channels/'+re.compile(r'\d+$').findall(self.url)[0]+'/messages?limit=50'
        return self.api, self.url
        
    def searchA(self):
        DataValue={}
        self.header['referer']=self.url
        count,countURL=0,0
        Doc=requests.get(self.api,headers=self.header)
        global window
        window.PrintErr(Doc)
        print(Doc)
        WebTemp = json.loads(Doc.text)
        self.LogLen=len(WebTemp)#資料筆數
        while count<self.LogLen: #A:timestamp B:content C:title D:url E:attachmentsname F:attachmentsurl G:referer
            DataTitle,DataUrl,DataAttname,DataAtturl='','','',''
            countURL=0
            try:
                DataTitleontent=WebTemp[count]['content']
                DataTime=WebTemp[count]['timestamp']
                DataReferer=self.url+'/'+WebTemp[count]['id']
                DataValue['content']=DataTitleontent
                DataValue['timestamp']=DataTime
                DataValue['referer']=DataReferer
                
                countURLMax=len(WebTemp[count]['embeds'])
                for countURL in range(countURLMax):
                    TitleTemp=WebTemp[count]['embeds'][countURL]['title']
                    UrlTemp=WebTemp[count]['embeds'][countURL]['url']
                    if countURLMax==1 or DataTitle=='':
                        DataTitle=TitleTemp
                        DataUrl=UrlTemp
                    else:
                        DataTitle=DataTitle+'\n'+TitleTemp
                        DataUrl=DataUrl+'\n'+UrlTemp
                DataValue['title']=DataTitle
                DataValue['url']=DataUrl
            except:
                UrlTemp=WebTemp[count]['embeds'][countURL]['url']
                if countURLMax==1 or DataUrl=='':
                    DataUrl=UrlTemp
                else:
                    DataUrl=DataUrl+'\n'+UrlTemp
                DataValue['title']=''
                DataValue['url']=DataUrl
            try:#attachments
                countURLMax=len(WebTemp[count]['attachments'])
                for countURL in range(countURLMax):
                    AttnameTemp=WebTemp[count]['attachments'][countURL]['filename']
                    AtturlTemp=WebTemp[count]['attachments'][countURL]['url']
                    if countURLMax==1 or DataAttname=='':
                        DataAttname=AttnameTemp
                        DataAtturl=AtturlTemp
                    else:
                        DataAttname=DataAttname+'\n'+AttnameTemp
                        DataAtturl=DataAtturl+'\n'+AtturlTemp
                DataValue['attachmentsname']=DataAttname
                DataValue['attachmentsurl']=DataAtturl
                self.Data.setdefault(count,str(DataValue))
            except:
                try:
                    AtturlTemp=WebTemp[count]['attachments'][countURL]['url']
                    if countURLMax==1 or DataAtturl=='':
                        DataAtturl=AtturlTemp
                    else:
                        DataAtturl=DataAtturl+'\n'+AtturlTemp
                    DataValue['attachmentsname']=''
                    DataValue['attachmentsurl']=DataAtturl
                    self.Data.setdefault(count,str(DataValue))
                except:
                    DataValue['attachmentsname']=''
                    DataValue['attachmentsurl']=''
                    self.Data.setdefault(count,str(DataValue))
            count+=1
        
        if self.LogLen==50:
            self.LogID = WebTemp[-1]['id']
        else:
            self.LogID = '0'
    def searchB(self):
        self.api=re.compile(r'https://discord.com/api/v8/channels/\d+/messages\?').findall(self.api)[0]+'before='+self.LogID+'&limit=50'
        return self.api
    
    def DataBase(self):
        count=0
        conn = sqlite3.connect('DiscordData.db')
        cursor=conn.cursor()
        for count in range(self.LogLen):
            Temp=eval(self.Data[count])
            readData=Temp["content"]
            if re.compile(r'[hH][tT][tT][pP]').findall(readData) !=[]: #有http進入
                command = "INSERT INTO URL(timestamp, content, title, url, attachmentsname, attachmentsurl, referer)VALUES(?,?,?,?,?,?,?)"
            else:
                command = "INSERT INTO Chat(timestamp, content, title, url, attachmentsname, attachmentsurl, referer)VALUES(?,?,?,?,?,?,?)"
            try:
                cursor.execute(command, (Temp["timestamp"], Temp["content"], Temp["title"], Temp["url"], Temp["attachmentsname"], Temp["attachmentsurl"], Temp["referer"]))
            except Exception as err:
                if re.compile(r'UNIQUE constraint failed:.+').findall(str(err)) ==[]:
                    global window
                    window.PrintErr(err)
                    print(count,err)
        conn.commit()
        conn.close()
    def ctrateDB(self):
        try:
            conn = sqlite3.connect('DiscordData.db')
            conn.execute("""
                        CREATE TABLE "URL" (
                    	"id"	INTEGER NOT NULL,
                    	"timestamp"	 timestamp,
                    	"content"	TEXT UNIQUE,
                    	"title"	TEXT,
                    	"url"	TEXT,
                        "attachmentsname"	TEXT,
                        "attachmentsurl"	TEXT,
                        "referer"	varchar(120),
                    	PRIMARY KEY("id" AUTOINCREMENT));
                         """)
            conn.execute("""
                        CREATE TABLE "Chat" (
                    	"id"	INTEGER NOT NULL,
                    	"timestamp"	 timestamp,
                    	"content"	TEXT UNIQUE,
                    	"title"	TEXT,
                    	"url"	TEXT,
                        "attachmentsname"	TEXT,
                        "attachmentsurl"	TEXT,
                        "referer"	varchar(120),
                    	PRIMARY KEY("id" AUTOINCREMENT));
                         """)
            conn.close()
        except:
            pass

    def deleteDB(self):
        conn = sqlite3.connect('DiscordData.db')
        conn.execute("""delete FROM URL;""")
        conn.execute("""delete FROM Chat;""")
        conn.execute("""VACUUM;""")
        conn.commit()
        conn.close()

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
