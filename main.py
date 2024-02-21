# oding = utf-8
# -*- coding:utf-8 -*-
import requests,json,time,threading,os,msvcrt,sys

DEFAULT_COOKIES={}
POOL=[]
WEARCATEGORY={"wearcategory0":[0,0.07],"wearcategory1":[0.07,0.15],"wearcategory2":[0.15,0.38],"wearcategory3":[0.38,0.45],"wearcategory4":[0.45,0.7]}
SORT_BY=("default","created.desc","price.asc")
sortByIndex=0
maxPage=0

class Message:
    def __init__(self,text,title,time):
        self.title=title
        self.text=text
        self.time=time

class MessageQueue:
    def __init__(self):
        self.queue=[]
    def add(self,message: Message):
        self.queue.append(message)
    def get(self):
        return self.queue
    def __len__(self):
        return len(self.queue)
    def __getitem__(self, item):
        if len(self)>item>=-len(self):
            return self.queue[item]
        raise IndexError
    def clear(self):
        self.queue.clear()
class Item:
    COOKIES = {}
    RUN_FLAG=True
    def __init__(self,id : int,priceRange : tuple,cookies:dict,name : str,messageQueue:MessageQueue,pwRange:tuple):
        self.id = id
        self.min = priceRange[0]
        self.max = priceRange[1]
        self.COOKIES=cookies
        self.name=name
        self.messageQueue = messageQueue
        self.pwRange=pwRange
    def setCookie(self,csrf_token: str, session: str):
        self.COOKIES["csrf_token"] = csrf_token
        self.COOKIES["session"] = session
    def filter(self,item: dict) -> bool:
        if self.min <= float(item["price"]) <= self.max:
            if "paintwear" in item["asset_info"] and item["asset_info"]["paintwear"]:
                if self.pwRange[0]<=float(item["asset_info"]["paintwear"])<=self.pwRange[1]:
                    return True
                else:
                    return False
            return True
        return False
    def buyItem(self,item: dict,payMethod:int=3):
        data = {"game": "csgo", "goods_id": self.id, "pay_method": payMethod, "price": item["price"],
                "sell_order_id": item["id"], "token": "", "cdkey_id": "", "allow_tradable_cooldown": 0}
        preview = requests.get(
            f"https://buff.163.com/api/market/goods/buy/preview?game=csgo&sell_order_id={item['id']}&goods_id={self.id}&price={item['price']}&allow_tradable_cooldown=0&cdkey_id=&_=1708350622539",
            cookies=self.COOKIES)
        self.setCookie(preview.cookies.get_dict()["csrf_token"],self.COOKIES["session"])
        buy = requests.post("https://buff.163.com/api/market/goods/buy", headers={
            "X-Csrftoken": self.COOKIES["csrf_token"],
            "Referer": f"https://buff.163.com/goods/878856?from=market"}, data=data,cookies=self.COOKIES)
        return json.loads(buy.text)
    def looper(self):
        pi=1
        while self.RUN_FLAG:
            try:
                result=requests.get(f"https://buff.163.com/api/market/goods/sell_order?game=csgo&goods_id={self.id}&page_num={pi}&sort_by={SORT_BY[sortByIndex]}",cookies=self.COOKIES).text
                result=json.loads(result)
            except json.decoder.JSONDecodeError:
                self.messageQueue.add(Message("接收到无法json解码的信息 这并非一个错误", "Null Content From Server", time.time()))
                continue
            try:
                items=result["data"]["items"]
            except:
                if "code" in result:
                    if result["code"]=="System Error":
                        self.messageQueue.add(Message(result["error"],"Connect Failed",time.time()))
                        time.sleep(5)
                continue
            for itemIndex in range(len(items)):
                if self.filter(items[itemIndex]):
                    buyInfo=self.buyItem(items[itemIndex])
                    if buyInfo["code"]=="Market Cash Not Enough":
                        self.messageQueue.add(Message(
                            f"武器名称 {self.name} 无法购置\n余额不足 该物品检测程式结束",
                            "购入失败", time.time()))
                        self.RUN_FLAG=False
                        break
                    if "data" not in buyInfo:
                        continue
                    self.messageQueue.add(Message(f"订单号 {buyInfo['data']['id']}\n武器ID {buyInfo['data']['goods_id']} 武器名称 {self.name}\n价格 {buyInfo['data']['price']}元 / 支付方式 {'BUFF余额' if buyInfo['data']['pay_method']==3 else '微信' if buyInfo['data']['pay_method']==6 else '未知'}\n成交时间 {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(buyInfo['data']['created_at']))}","购入",buyInfo['data']['created_at']))
            if pi>=maxPage:
                pi=0
            pi+=1
            time.sleep(2)
        if self in POOL:
            POOL.pop(POOL.index(self))

class Program:
    def __init__(self):
        self.messageQueue=MessageQueue()
    def clear(self):
        os.system("cls")
    def getConfigFromFile(self):
        with open("config","r") as f:
            config=json.load(f)
        return config
    def setConfigToFile(self,obj):
        with open("config","w") as f:
            json.dump(obj, f,indent=4)
        return 0
    def run(self):
        global DEFAULT_COOKIES,sortByIndex,maxPage
        config=self.getConfigFromFile()
        DEFAULT_COOKIES=config["cookies"]
        weapons:list=config["weapons"]
        sortByIndex=config["sort_by"]
        maxPage=config["max_page"]
        flag=False
        logsPage=0
        METHODS=("1: Add Weapons","2: Run","3: Logs","4: Exit & Save")
        STATE=[0,0,0,0,0,0,0,0]
        while 1:
            os.system("cls")
            if len(self.messageQueue)>100:
                self.messageQueue.clear()
            if len(POOL)==0:
                STATE[6]=0
            if STATE[5]:
                m=self.messageQueue[-STATE[2]-1]
                print("---------------Logs---------------")
                print(f"Title {m.title}")
                print(f"Time {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(m.time))}")
                print("Text:")
                print(" "*3,m.text)
                _ = msvcrt.getche()
                if _ == b"\b":
                    STATE[5] = 0
                    continue
            if STATE[7]:
                print("---------------Logs---------------")
                print(f"              Page {logsPage}")
                print("Time"," "*17,"Title")
                if len(self.messageQueue)==0:
                    print("Nothing There Is...")
                    print("Type BACKSPACE To Return Last Page.")
                for i in range(10):
                    if len(self.messageQueue)<=i+logsPage*10:
                        break
                    if i+logsPage*10 == STATE[2]:
                        print("\033[107;90m", end="")
                    else:
                        print("\033[100;97m", end="")
                    m=self.messageQueue[-i-logsPage*10-1]
                    print(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(m.time))}   ",m.title)
                print("\033[0m\033[K", end="")
                _ = msvcrt.getche()
                if _ == b"\b":
                    STATE[7]=0
                    continue
                if _ == b'\xe0':
                    flag = True
                    continue
                if flag and _ == b'H':
                    if STATE[2] > 0:
                        STATE[2] -= 1
                elif flag and _ == b'P':
                    if STATE[2] < len(self.messageQueue) - 1:
                        STATE[2] += 1
                logsPage=STATE[2]//10
                if _ == b"\r":
                    STATE[5]=1
                flag = False
                continue
            print(r"""██████╗  ██╗   ██╗ ███████╗ ███████╗
██╔══██╗ ██║   ██║ ██╔════╝ ██╔════╝
██████╔╝ ██║   ██║ █████╗   █████╗  
██╔══██╗ ██║   ██║ ██╔══╝   ██╔══╝  
██████╔╝ ╚██████╔╝ ██║      ██║     
╚═════╝   ╚═════╝  ╚═╝      ╚═╝                               
███████╗ ███████╗   ███╗   ██████╗   ██████╗ ██╗  ██╗ ███████╗ ██████╗ 
██╔════╝ ██╔════╝ ██╔══██╗ ██╔══██╗ ██╔════╝ ██║  ██║ ██╔════╝ ██╔══██╗
███████╗ █████╗   ███████║ ██████╔╝ ██║      ███████║ █████╗   ██████╔╝
╚════██║ ██╔══╝   ██╔══██║ ██╔══██╗ ██║      ██╔══██║ ██╔══╝   ██╔══██╗
███████║ ███████╗ ██║  ██║ ██║  ██║ ╚██████╗ ██║  ██║ ███████╗ ██║  ██║
╚══════╝ ╚══════╝ ╚═╝  ╚═╝ ╚═╝  ╚═╝  ╚═════╝ ╚═╝  ╚═╝ ╚══════╝ ╚═╝  ╚═╝""")
            print("\033[?25l",end="")
            for i in range(len(METHODS)):
                if i==STATE[0]:
                    print("\033[107;90m", end="")
                else:
                    print("\033[100;97m", end="")
                print(METHODS[i])
            print("\033[0m\033[K",end="")
            if STATE[6]:
                print("\033[46;37mRUNNING! \033[0m")
            if STATE[1]:
                print("\033[93;107mPLEASE WAIT...\033[0m")
            _ = msvcrt.getche()
            if _ == b'\xe0':
                flag = True
                continue
            if flag and _ == b'H':
                if STATE[0]>0:
                    STATE[0]-=1
            elif flag and _ == b'P':
                if STATE[0] < len(METHODS)-1:
                    STATE[0] += 1
            flag=False
            if not _ == b"\r":
                continue
            if STATE[0]==0:
                print("\033[?25h", end="")
                try:
                    weapons_=json.loads((requests.get(
                        f"https://buff.163.com/api/market/goods?game=csgo&search={input('输入饰品名称:')}&tab=selling",
                        cookies=DEFAULT_COOKIES).text))
                    weapons_=weapons_["data"]["items"]
                except:
                    print("无法查找，请重新输入")
                    continue
                names={}
                exteriors={}
                for weapon in weapons_:
                    print(weapon["id"], weapon["name"])
                    names[weapon["id"]]=weapon["name"]
                    try:
                        exteriors[weapon["id"]]=weapon["goods_info"]["info"]["tags"]["exterior"]["internal_name"]
                    except:
                        exteriors[weapon["id"]]=None
                weapon_id=int(input("武器ID:"))
                minp = float(input("MIN PRICE:"))
                maxp=float(input("MAX PRICE:"))
                if not(exteriors[weapon_id] is None):
                    print(f"MIN PAINTWEAR: {WEARCATEGORY[exteriors[weapon_id]][0]}")
                    print(f"MAX PAINTWEAR: {WEARCATEGORY[exteriors[weapon_id]][1]}")
                    print("If you want not to set the paintwear,just type ENTER.")
                    minpw_ = input("MIN PAINTWEAR:")
                    maxpw_ = input("MAX PAINTWEAR:")
                    if not minpw_:
                        minpw=WEARCATEGORY[exteriors[weapon_id]][0]
                    else:
                        minpw =float(minpw_)
                    if not maxpw_:
                        maxpw=WEARCATEGORY[exteriors[weapon_id]][1]
                    else:
                        maxpw = float(maxpw_)
                else:
                    minpw,maxpw=0,0
                weapons.append({"id":weapon_id,"range":[minp,maxp],"pw_range":[float(minpw),float(maxpw)],"name":names[weapon_id]})
            elif STATE[0]==1:
                for p in POOL:
                    p.RUN_FLAG=False
                POOL.clear()
                for w in weapons:
                    POOL.append(Item(w["id"], tuple(w["range"]), DEFAULT_COOKIES,w["name"],self.messageQueue,w["pw_range"]))
                    threading.Thread(target=POOL[-1].looper).start()
                STATE[6] = 1
            elif STATE[0]==2:
                STATE[7]=1
            elif STATE[0]==3:
                STATE[1]=1
                for p in POOL:print("\033[30;43mPLEASE WAIT...\033[0m");p.RUN_FLAG=False
                self.setConfigToFile({"sort_by":sortByIndex,"max_page":maxPage,"cookies":DEFAULT_COOKIES,"weapons":weapons})
                STATE[1] = 0
                STATE[6] = 0
                os.system("cls")
                sys.exit()
            print("\033[0;0h", end="")
if __name__=="__main__":
    program=Program()
    program.run()