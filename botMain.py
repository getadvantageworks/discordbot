#ライブラリ
import datetime
import time
import discord
import asyncio
import requests
import parameter

#自作
import progress

class BotTask:
    
    #開始から終了、エラー処理
    def main(self):
        print('Hello , I am botMain.')
        #切断回数カウンタ、intだとイミュータブルなのでリスト形式、別関数に引数として渡している
        #通信が切断されても、一定回数再接続を試みる
        disconnectCounter = [0]
        #1カウントあたりの待ち時間
        waitTime = 10
        #カウントの上限
        maxWait = 3
        while True:
            try:
                print('try connect at ' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                
                #開始
                self.start(disconnectCounter)

                #正常終了の場合、10秒待機して再接続
                print('wait 10 seconds at ' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                time.sleep(10)
            #clientから例外が返されたときの処理
            except Exception as e:
                #エラーメッセージ表示
                print('error message:')
                print(e)
                print('connect error at ' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                
                #エラーが一定回数続いたら終了
                if disconnectCounter[0] >= maxWait:
                    print("can't connect " + str(maxWait) + " times at " + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                    print('Bye.')
                    exit()
                
                else:
                    #エラー回数が増えるたびに待ち時間を増加
                    disconnectCounter[0] += 1
                    print('wait '+ str(disconnectCounter[0] * waitTime) + ' seconds at ' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                    time.sleep(disconnectCounter[0] * waitTime)
    
    #botを開始する処理
    def start(self, disconnectCounter):
        client = self.makeClient(disconnectCounter)
        client.run(parameter.token, reconnect = False)
        
    #botの動作を定義する処理
    def makeClient(self, disconnectCounter):
        intents = discord.Intents.all()
        loop = asyncio.new_event_loop()
        client = discord.Client(intents = intents, loop = loop)

        #接続確認
        @client.event
        async def on_connect():
            print('connect success at ' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))

        #通信可能確認
        @client.event
        async def on_ready():
            #エラー回数リセット
            disconnectCounter[0] = 0
            print('ready at ' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
            channel = client.get_channel(parameter.checkchannelid)
            await channel.send('wake up')

        #メッセージ受信時
        @client.event
        async def on_message(Message):

            #自身のメッセージは無視
            if Message.author == client.user:
                return 0
            
            #自身以外のメッセージを受け取ったら出力
            print('get message at ' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))

            #進捗チャンネルに反応
            if Message.channel.name == 'test':
                #対応するメッセージを取得、投稿
                msg = progress.progress(Message.content)

                await Message.channel.send(msg)
                msg = None

                #レンタルサーバーに設置したAPIを経由して、データベースに記録する
                param = {"input": Message.content, "password": parameter.apipass}
                response = requests.post(parameter.apiurl, data = param)
                if(response.status_code == 200 and response.text == "success"):
                    print("insert to database")
                else:
                    print(response.status_code, response.text)

            #commandチャンネルの特定の文字列に反応、主に制御用
            if Message.channel.name == 'command':
                #別のチャンネルにメッセージを投稿し、わざと通知を作成する
                if(Message.content == 'send'):
                    print('call send at ' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                    channel = client.get_channel(parameter.makenoticechannelid)
                    await channel.send('make notice')
                #discordとの接続を一度切断する
                if(Message.content == 'close'):
                    print('call close at ' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                    await client.close()
                #botを終了する
                if(Message.content == 'exit'):
                    print('call exit at ' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
                    exit()
                #特定の行動に関するデータをAPIから取得する
                #例として、「運動」という言葉が記録された回数を取得する
                if(Message.content == 'count'):
                    response = requests.get(parameter.apiurl)
                    if(response.status_code == 200):
                        print("get count")
                    await Message.channel.send(response.text)
                    
            #動作確認チャンネルに反応、動作確認用
            if Message.channel.name == 'check':
                await Message.channel.send('I live at ' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
        
        #接続が切れたときの処理
        @client.event
        async def on_disconnect():
            print('disconnect at ' + datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'))

        #clientを返却
        return client

#インスタンス作成、処理実行
task = BotTask()
task.main()
