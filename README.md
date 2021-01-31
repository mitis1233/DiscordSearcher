# DiscordSearcher
可以自訂下載想要的Discord頻道

頻道內所有文字內容會以SQLite儲存在db檔案內

## 截圖

DiscordSearcher.exe介面：
![DiscordSearcher介面](https://github.com/mtis1233/DiscordSearcher/blob/v1.0/%E5%9C%96%E7%89%87/pic1.png?raw=true)

DB Browser for SQLite開啟DiscordData.db：
![DiscordData](https://github.com/mtis1233/DiscordSearcher/blob/v1.0/%E5%9C%96%E7%89%87/pic2.png?raw=true)

## 使用教學
1. 開啟DiscordSeacher.exe
2. 點選登入設定按鈕填入資訊儲存
3. 將要下載的頻道網址填入
4. 可選擇是否開啟快速模式(只下載最新50筆資料)
5. 點選開始搜尋按鈕


## 產生檔案

使用後會產生DiscordURL.txt及DiscordData.db

1. DiscordURL.txt ： 

      用於儲存要搜索的網址
      
      每行一個網址 格式為 https://discord.com/channels/.../...
      
2. DiscordData.db： 

      用於儲存搜索的資料

      可用DB Browser for SQLite開啟
      
      兩個資料庫： 內容只有文字、內容有網址
      
      資料庫表格格式：
      
        id: 創建第幾筆
      
        timestamp: 時間
      
        content: 聊天內容
      
        title: 內容裡的網站名稱
      
        url: 內容裡的網址
      
        attachmentsname: 上傳的文件名稱
      
        attachmentsurl: 上傳的文件下載網址
        
        referer: 這筆資料的來源

## 登入資訊填入教學

注意：authorization、cookie等同帳密資訊 勿外流

1. 使用Chrome登入Discord
2. 點F12
3. 點選Network標籤
4. 點選XHR標籤
5. 從Name列表點選其中一個
6. Headers標籤下尋找Request Headers
7. 在Request Headers下方尋找你所需要的資訊複製過去
