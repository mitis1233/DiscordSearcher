from random import uniform
import sys, os, requests, json, time, re, sqlite3
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget
from PyQt5.QtCore import QFile, pyqtSignal, QThread, QSettings,Qt
from UI_Main import Ui_MainWindow
from UI_Login import Ui_Form
from UI_RE import Ui_Form_RE

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
        DiscordRule=QSettings("DiscordRule.ini", QSettings.IniFormat)
        self.Discord.header['authorization']=DiscordRule.value("LoginWindow/authorization")
        self.Discord.header['cookie']=DiscordRule.value("LoginWindow/cookie")
        self.Discord.header['user-agent']=DiscordRule.value("LoginWindow/user-agent")
        self.Discord.header['x-super-properties']=DiscordRule.value("LoginWindow/x-super-properties")
        print(self.Discord.header)
        self.Discord.REWindowRuleTextEdit=DiscordRule.value("REWindow/rule")
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
        self.Login_window = LoginWindow()
        self.RE_window = REWindow()
        
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
        self.ui.pushButton_3.clicked.connect(self.Login_window.show)#登入設定
        self.ui.pushButton_4.clicked.connect(self.pushButton_Click_Stop)#強制停止(搜尋)
        self.ui.pushButton_5.clicked.connect(self.RE_window.show)#資料庫設定
        
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

class REWindow(QWidget):
    def __init__(self):
        super(REWindow, self).__init__()
        self.ui = Ui_Form_RE()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon('D://DiscordSearcher//ico.ico'))
        self.ui.pushButton.clicked.connect(self.button_1)#等於or不等於
        self.ui.pushButton_2.clicked.connect(self.button_2)#新增分類方式
        self.ui.pushButton_3.clicked.connect(self.button_3)#建立資料表
        self.ui.pushButton_4.clicked.connect(self.button_4)#開關刪除功能
        self.ui.pushButton_5.clicked.connect(self.button_5)#刪除資料
        self.ui.pushButton_6.clicked.connect(self.button_6)#刪除資料表
        self.ui.pushButton_7.clicked.connect(self.button_7)#點擊開始測試
        self.ui.pushButton_5.setEnabled(False)
        self.ui.pushButton_6.setEnabled(False)
        self.data_1=''#關鍵字
        self.data_2='='#有這關鍵字or沒有這關鍵字
        self.data_3=''#資料新增至哪個資料表
        self.settings = QSettings("DiscordRule.ini", QSettings.IniFormat)
        self.ui.textEdit.setText(self.settings.value("REWindow/rule"))
        print(self.settings.value("REWindow/rule"))
        self.listTable=[]
        conn = sqlite3.connect('DiscordData.db')
        Temp=conn.execute("select name from sqlite_master where type = 'table' order by name").fetchall()
        conn.close()
        for count in range(len(Temp)):
            self.listTable.append(Temp[count][0])
        try:
            self.listTable.remove('sqlite_sequence')
        except:
            print('查無資料庫，初始化資料庫')
            DiscordRun().ctrateDB()
            conn = sqlite3.connect('DiscordData.db')
            Temp=conn.execute("select name from sqlite_master where type = 'table' order by name").fetchall()
            conn.close()
            for count in range(len(Temp)):
                self.listTable.append(Temp[count][0])
            self.settings.setValue("REWindow/rule","r'http.+'，=，URL\nr'http.+'，≠，Chat")
            self.ui.textEdit.setText(self.settings.value("REWindow/rule"))
            self.listTable.remove('sqlite_sequence')
        print(self.listTable)
        self.ui.comboBox.addItems(self.listTable)
        self.ui.comboBox_2.addItems(self.listTable)
        
    def TableSave(self,value):
        value=[value]
        self.ui.comboBox.addItems(value)
        self.ui.comboBox_2.addItems(value)
        
    def button_1(self):
        if self.ui.pushButton.text() == "=":
            self.ui.pushButton.setText("≠")
            self.data_2='≠'
        else:
            self.ui.pushButton.setText("=")
            self.data_2='='
            
    def button_2(self):
        lineEditTXT=self.ui.lineEdit.text()
        if lineEditTXT == '':
            self.settings.setValue("REWindow/rule",self.ui.textEdit.toPlainText())
        else:
            lineEditTXT2=lineEditTXT+'，'+self.data_2+'，'+self.ui.comboBox.currentText()
            self.ui.textEdit.append(lineEditTXT2)
            
            textEditTXT=self.ui.textEdit.toPlainText()
            print(textEditTXT)
            self.settings.setValue("REWindow/rule",textEditTXT)
            print(self.settings.value("REWindow/rule"))
            self.ui.lineEdit.clear()
        
    def button_3(self):
        lineEdit_2text=self.ui.lineEdit_2.text().strip()
        if lineEdit_2text != '':
            self.ui.lineEdit_2.clear()
            try:
                DBtext="""CREATE TABLE '"""+lineEdit_2text+"""' (
                        "id"                INTEGER         NOT NULL,
                        "timestamp"         timestamp,
                        "content"           TEXT            UNIQUE,
                        "title"             TEXT,
                        "url"               TEXT,
                        "attachmentsname"	TEXT,
                        "attachmentsurl"	TEXT,
                        "referer"           varchar(120),
                        PRIMARY KEY("id" AUTOINCREMENT));
                        """
                print(DBtext)
                conn = sqlite3.connect('DiscordData.db')
                conn.execute(DBtext)
                conn.close()
                self.TableSave(lineEdit_2text)
            except:
                pass
            
    def button_4(self):
        if self.ui.pushButton_4.text() == "🔒": #🔒 Locked🔓 Unlocked
            self.ui.pushButton_4.setText("🔓")
            self.ui.label_3.setText("Unlocked")
            self.ui.pushButton_5.setEnabled(True)
            self.ui.pushButton_6.setEnabled(True)
        else:
            self.ui.pushButton_4.setText("🔒")
            self.ui.label_3.setText("Locked")
            self.ui.pushButton_5.setEnabled(False)
            self.ui.pushButton_6.setEnabled(False)
            
    def button_5(self):
        DBtext="""delete FROM '"""+self.ui.comboBox_2.currentText()+"';"
        try:
            conn = sqlite3.connect('DiscordData.db', isolation_level=None)
            conn.execute(DBtext)
            conn.execute("""VACUUM;""")
            conn.commit()
            conn.close()
        except:
            print('Err_button_5')
        
    def button_6(self):
        DBtext="""DROP TABLE '"""+self.ui.comboBox_2.currentText()+"';"
        try:
            conn = sqlite3.connect('DiscordData.db', isolation_level=None)
            conn.execute(DBtext)
            conn.execute("""VACUUM;""")
            conn.commit()
            conn.close()
            self.ui.comboBox.removeItem(self.ui.comboBox_2.findText(self.ui.comboBox_2.currentText()))
            self.ui.comboBox_2.removeItem(self.ui.comboBox_2.findText(self.ui.comboBox_2.currentText()))
        except:
            print('Err_button_6')
            
    def button_7(self):#測試自訂規則
        lines=self.ui.textEdit.toPlainText().splitlines()#資料分行
        for linescount in range(len(lines)):
            line=lines[linescount].split("，")#行資料分類
            data_1=line[0]#關鍵字
            data_2=line[1]# = or ≠
            data_3=line[2]#存到Table
            textEdit_2=self.ui.textEdit_2.toPlainText()
            if data_1[0:2]=="r'":#正則表達式
                data_1=eval(data_1)    
            if data_2 == "=":
                if re.findall(re.compile(data_1, re.I), textEdit_2)!=[]:
                    self.ui.textEdit_3.setText(data_3)
                    break
                else:
                    self.ui.textEdit_3.setText('None')
            else:#≠
                if re.findall(re.compile(data_1, re.I), textEdit_2)==[]:
                    self.ui.textEdit_3.setText(data_3)
                    break
                else:
                    self.ui.textEdit_3.setText('None')
            linescount+=1
            
    def closeEvent(self, event):
        if self.ui.pushButton_4.text() != "🔒":
            self.ui.pushButton_4.setText("🔒")
            self.ui.label_3.setText("Locked")
            self.ui.pushButton_5.setEnabled(False)
            self.ui.pushButton_6.setEnabled(False)
        

class LoginWindow(QWidget):
    def __init__(self):
        super(LoginWindow, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon('D://DiscordSearcher//ico.ico'))
        self.ui.pushButton.clicked.connect(self.set1)
        self.settings = QSettings("DiscordRule.ini", QSettings.IniFormat)
        self.ui.lineEdit.setText(self.settings.value("LoginWindow/authorization"))
        self.ui.lineEdit_2.setText(self.settings.value('LoginWindow/cookie'))
        self.ui.lineEdit_3.setText(self.settings.value('LoginWindow/user-agent'))
        self.ui.lineEdit_4.setText(self.settings.value('LoginWindow/x-super-properties'))
        
    def set1(self):
        self.settings.setValue("LoginWindow/authorization",self.ui.lineEdit.text())
        self.settings.setValue("LoginWindow/cookie",self.ui.lineEdit_2.text())
        self.settings.setValue("LoginWindow/user-agent",self.ui.lineEdit_3.text())
        self.settings.setValue("LoginWindow/x-super-properties",self.ui.lineEdit_4.text())
        self.close()


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
        self.REWindowRuleTextEdit=''
                    
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
        global window
        for count in range(self.LogLen):#REWindow/rule
            Temp=eval(self.Data[count])
            readData=Temp["content"]
            lines=self.REWindowRuleTextEdit.splitlines()#資料分行
            for linescount in range(len(lines)):
                line=lines[linescount].split("，")#行資料分類
                data_1=line[0]#關鍵字
                data_2=line[1]# = or ≠
                data_3=line[2]#存到Table
                if data_1[0:2]=="r'":#正則表達式
                    data_1=eval(data_1)    
                if data_2 == "=":
                    if re.findall(re.compile(data_1, re.I), readData)!=[]:
                        command = "INSERT INTO '"+data_3+"'(timestamp, content, title, url, attachmentsname, attachmentsurl, referer)VALUES(?,?,?,?,?,?,?)"
                        try:
                            cursor.execute(command, (Temp["timestamp"], Temp["content"], Temp["title"], Temp["url"], Temp["attachmentsname"], Temp["attachmentsurl"], Temp["referer"]))
                        except Exception as err:
                            if re.compile(r'UNIQUE constraint failed:.+').findall(str(err)) ==[]:
                                window.PrintErr(err)
                                print(count,err)
                        break
                else:#≠
                    if re.findall(re.compile(data_1, re.I), readData)==[]:
                        command = "INSERT INTO '"+data_3+"'(timestamp, content, title, url, attachmentsname, attachmentsurl, referer)VALUES(?,?,?,?,?,?,?)"
                        try:
                            cursor.execute(command, (Temp["timestamp"], Temp["content"], Temp["title"], Temp["url"], Temp["attachmentsname"], Temp["attachmentsurl"], Temp["referer"]))
                        except Exception as err:
                            if re.compile(r'UNIQUE constraint failed:.+').findall(str(err)) ==[]:
                                window.PrintErr(err)
                                print(count,err)
                        break
                linescount+=1
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