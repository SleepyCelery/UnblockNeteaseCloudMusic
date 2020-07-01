import requests
import os
import psutil
import json
from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import askdirectory
import multiprocessing
import sys
import subprocess
import win32com.client
from log import write_log
import UserConfig
from concurrent.futures import ThreadPoolExecutor, wait
import ClashProviderMerge

requests.packages.urllib3.disable_warnings()

proxy_process = False


def check_cloudmusic_process():
    try:
        WMI = win32com.client.GetObject('winmgmts:')
        processCodeCov = WMI.ExecQuery('select * from Win32_Process where Name="cloudmusic.exe"')
        if len(processCodeCov) > 0:
            return True
        else:
            return False
    except Exception as e:
        showerror('错误', '检测网易云进程出错!错误信息:{}'.format(e))
        write_log(e)


def terminate_cloudmusic():
    times = 0
    while True:
        try:
            times += 1
            process_list = []
            for i in psutil.pids():
                p = psutil.Process(i)
                if p.name() == 'cloudmusic.exe':
                    process_list.append(p)
            for i in process_list:
                i.terminate()
            break
        except Exception as e:
            if times >= 5:
                showerror('错误', '结束网易云进程出错!错误信息:{}'.format(e))
                write_log(e)
            else:
                continue


def terminate_proxy():
    p = subprocess.Popen("KillClash.bat")
    p.wait()


def get_config_path():
    appdata = os.getenv('APPDATA').rstrip("Roaming")
    cloudmusic_config = appdata + r'Local\Netease\CloudMusic\Config'
    if os.path.exists(cloudmusic_config):
        return cloudmusic_config
    return False


def backup_config():
    with open(get_config_path(), mode='r') as config:
        with open('Config.backup', mode='w') as backup:
            backup.write(json.dumps(json.load(config)))


def restore_config():
    if check_cloudmusic_process():
        if askokcancel('警告', '在紧急恢复配置文件时,需要关闭网易云音乐!您确认关闭网易云音乐吗?'):
            terminate_cloudmusic()
    if os.path.exists('Config.backup') and not check_cloudmusic_process():
        with open('Config.backup', mode='r') as backup:
            with open(get_config_path(), mode='w') as config:
                config.write(json.dumps(json.load(backup)))
                showinfo('提示', '紧急恢复成功!请启动网易云音乐!')
                status['text'] = '当前状态:紧急恢复成功'


def change_proxy_settings(switch):
    if switch:
        with open(get_config_path(), mode='r') as config:
            settings = json.load(config)
        try:
            settings['Proxy']['Type'] = 'http'
            settings['Proxy']['http']['Host'] = '127.0.0.1'
            settings['Proxy']['http']['Port'] = '7890'
            settings = json.dumps(settings)
        except:
            settings['Proxy'] = {"Type": "http",
                                 "http": {"Host": "127.0.0.1", "Password": "", "Port": "7890", "UserName": ""},
                                 "https": {"Host": "", "Password": "", "Port": "80", "UserName": ""},
                                 "ie": {"Host": "", "Password": "", "Port": "", "UserName": ""},
                                 "none": {"Host": "", "Password": "", "Port": "", "UserName": ""},
                                 "socks": {"Host": "", "Password": "", "Port": "1080", "UserName": ""},
                                 "socks4": {"Host": "", "Password": "", "Port": "1080", "UserName": ""},
                                 "socks5": {"Host": "", "Password": "", "Port": "1080", "UserName": ""}}
            settings = json.dumps(settings)
        with open(get_config_path(), mode='w') as config:
            config.write(settings)
    else:
        with open(get_config_path(), mode='r') as config:
            settings = json.load(config)
        try:
            settings['Proxy']['Type'] = 'none'
            settings['Proxy']['http']['Host'] = ''
            settings['Proxy']['http']['Port'] = '80'
            settings = json.dumps(settings)
        except:
            settings['Proxy'] = {"Type": "none",
                                 "http": {"Host": "127.0.0.1", "Password": "", "Port": "7890", "UserName": ""},
                                 "https": {"Host": "", "Password": "", "Port": "80", "UserName": ""},
                                 "ie": {"Host": "", "Password": "", "Port": "", "UserName": ""},
                                 "none": {"Host": "", "Password": "", "Port": "", "UserName": ""},
                                 "socks": {"Host": "", "Password": "", "Port": "1080", "UserName": ""},
                                 "socks4": {"Host": "", "Password": "", "Port": "1080", "UserName": ""},
                                 "socks5": {"Host": "", "Password": "", "Port": "1080", "UserName": ""}}
            settings = json.dumps(settings)
        with open(get_config_path(), mode='w') as config:
            config.write(settings)


def get_github_config(path, url):
    if 'raw.githubusercontent.com' in url:
        url = url.replace('raw.githubusercontent.com', '151.101.184.133')
    with open(path, mode='w', encoding='utf-8') as file:
        response = requests.get(
            url=url, headers={"Host": 'raw.githubusercontent.com'}, verify=False)
        response.encoding = 'utf-8'
        file.write(response.text)


def update():
    times = 0
    while True:
        try:
            times += 1
            if not os.path.exists('./RuleSet'):
                os.mkdir('./RuleSet')
            if not os.path.exists('./Proxy'):
                os.mkdir('./Proxy')
            Threadlist = []
            ThreadPool = ThreadPoolExecutor(max_workers=3)
            Threadlist.append(ThreadPool.submit(get_github_config, 'config.yaml',
                                                'https://151.101.184.133/DesperadoJ/Rules-for-UnblockNeteaseMusic/master/Clash/UnblockNeteaseMusic.yaml'))
            Threadlist.append(ThreadPool.submit(get_github_config, './Proxy/NeteaseMusic.yaml',
                                                'https://151.101.184.133/DesperadoJ/Rules-for-UnblockNeteaseMusic/master/Clash/Proxy/NeteaseMusic.yaml'))
            Threadlist.append(ThreadPool.submit(get_github_config, './RuleSet/NeteaseMusic.yaml',
                                                'https://151.101.184.133/DesperadoJ/Rules-for-UnblockNeteaseMusic/master/Clash/RuleSet/NeteaseMusic.yaml'))
            wait(Threadlist)
            ClashProviderMerge.ConfigMerge()
            # with open('config.yaml', mode='w', encoding='utf-8') as file:
            #     response = requests.get(
            #         url='https://151.101.184.133/DesperadoJ/Rules-for-UnblockNeteaseMusic/master/Clash/UnblockNeteaseMusic.yaml',
            #         headers={"Host": 'raw.githubusercontent.com'}, verify=False)
            #     response.encoding = response.apparent_encoding
            #     file.write(response.text)
            # with open('./Proxy/NeteaseMusic.yaml', mode='w', encoding='utf-8') as file:
            #     response = requests.get(
            #         url='https://151.101.184.133/DesperadoJ/Rules-for-UnblockNeteaseMusic/master/Clash/Proxy/NeteaseMusic.yaml',
            #         headers={"Host": 'raw.githubusercontent.com'}, verify=False)
            #     response.encoding = response.apparent_encoding
            #     file.write(response.text)
            # with open('./RuleSet/NeteaseMusic.yaml', mode='w', encoding='utf-8') as file:
            #     response = requests.get(
            #         url='https://151.101.184.133/DesperadoJ/Rules-for-UnblockNeteaseMusic/master/Clash/RuleSet/NeteaseMusic.yaml',
            #         headers={"Host": 'raw.githubusercontent.com'}, verify=False)
            #     response.encoding = response.apparent_encoding
            #     file.write(response.text)
            print("更新订阅成功!")
            break
        except Exception as e:
            if times >= 5:
                showerror('警告', '在更新订阅时遇到了一个错误,请联系管理员修复程序!\n错误信息:{}'.format(e))
                write_log(e)
                sys.exit(0)
            else:
                continue


def run_proxy_process():
    global proxy_process
    proxy_process = subprocess.Popen('Start.bat', shell=False)


def run():
    status['text'] = '当前状态:正在启动代理'
    # 配置文件内路径包含.exe文件部分
    if not UserConfig.read_config('NeteaseCloudMusicPath') or not os.path.exists(
            UserConfig.read_config('NeteaseCloudMusicPath')):
        showinfo('提示', '检测到您是第一次使用本程序,请先选择网易云音乐安装目录!')
        while True:
            exe_path = askdirectory()
            if os.path.exists(str(exe_path) + r'/cloudmusic.exe'):
                UserConfig.add_config('NeteaseCloudMusicPath', str(exe_path) + r'/cloudmusic.exe')
                break
            else:
                if askokcancel('提示', '未在选择的目录下找到cloudmusic.exe文件,您依然可以使用本软件,但代理启动成功后不会自动打开网易云!\n是否重新选择路径?'):
                    continue
                else:
                    break
    if check_cloudmusic_process():
        if askokcancel('提示', '网易云音乐开启时无法启动代理,是否立即关闭网易云?'):
            terminate_cloudmusic()
        else:
            return False
    update()
    if os.path.exists('clash-windows-amd64.exe') and os.path.exists('config.yaml') and os.path.exists(
            'Country.mmdb') and os.path.exists('./RuleSet/NeteaseMusic.yaml') and os.path.exists(
        './Proxy/NeteaseMusic.yaml'):
        change_proxy_settings(True)
        run_proxy_process()
        showinfo('提示', '代理启动成功!现在可以畅听网易云音乐了!')
        subprocess.Popen(UserConfig.read_config('NeteaseCloudMusicPath'))
        status['text'] = '当前状态:代理启动成功'
        root.iconify()
    else:
        showerror('警告', '程序关键文件丢失,请修复程序!')
        return False


def show_instruction():
    showinfo('使用说明',
             '正常打开本程序后,先确保网易云未运行,然后点击启动代理按钮,当弹出启动成功的提示框后,即可正常使用网易云.\n本程序关闭会自动结束代理并关闭网易云\n如果遇到单独启动网易云断网的情况,请使用本软件的紧急恢复功能\n祝使用愉快(*^▽^*)')


def on_closing():
    global proxy_process
    if askokcancel('提示', '您确认关闭本程序吗?这将会同时关闭网易云音乐'):
        if check_cloudmusic_process():
            terminate_cloudmusic()
        if proxy_process:
            terminate_proxy()
            proxy_process.kill()
        change_proxy_settings(False)
        root.destroy()
        sys.exit(0)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    if not get_config_path():
        showerror('找不到配置文件', '找不到网易云音乐配置文件,请检查网易云音乐是否已安装!')
        sys.exit(0)
    else:
        if not os.path.exists('Config.backup'):
            backup_config()
    root = Tk()
    root.iconbitmap("logo.ico")
    root.title('网易云畅听代理')
    root.geometry("270x270")
    welcome_label = Label(root,
                          text='网易云畅听代理\n启动本程序后可听网易云收费及无版权歌曲\nPowered by 爱睡觉的南昌芹菜\nProxy from DesperadoJ, Clash Support')
    welcome_label.pack()
    start_button = Button(root, text='启动代理', command=run)
    instruction_button = Button(root, text='使用说明', command=show_instruction)
    restore_button = Button(root, text='紧急恢复', command=restore_config)
    start_button.pack(pady=10)
    instruction_button.pack(pady=10)
    restore_button.pack(pady=10)
    status = Label(root, text='当前状态:')
    status.pack(pady=10)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
