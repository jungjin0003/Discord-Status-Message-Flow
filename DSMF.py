# -*- coding: utf-8 -*-
from ctypes import *
import requests
import time
import sys
import os
import re

user32 = windll.LoadLibrary('user32.dll')

URL = 'https://discord.com/api/v9/users/@me/settings'

class OPENFILENAMEA(Structure):
    _fields_ = [
        ('lStructSize', c_ulong),
        ('hwndOwner', c_void_p),
        ('hInstance', c_void_p),
        ('lpstrFilter', c_char_p),
        ('lpstrCustomFilter', c_char_p),
        ('nMaxCustFilter', c_ulong),
        ('nFilterIndex', c_ulong),
        ('lpstrFile', c_char_p),
        ('nMaxFile', c_ulong),
        ('lpstrFileTitle', c_char_p),
        ('nMaxFileTitle', c_ulong),
        ('lpstrInitialDir', c_char_p),
        ('lpstrTitle', c_char_p),
        ('Flags', c_ulong),
        ('nFileOffset', c_ushort),
        ('nFileExtension', c_ushort),
        ('lpstrDefExt', c_char_p),
        ('lCustData', c_ulonglong),
        ('lpfnHook', c_void_p),
        ('lpTemplateName', c_char_p),
        ('pvReserved', c_void_p),
        ('dwReserved', c_ulong),
        ('FlagsEx', c_ulong)
    ]

def change_message(token, message):
    headers = { 'Host' : 'discord.com', 'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36', 'Content-Type' : 'application/json', 'Authorization' : token, 'Accept' : '*/*', 'Origin' : 'https://discord.com', 'Accept-Encoding' : 'gzip, deflate' }
    
    if message == None:
        payload = {'custom_status':None}
    else:
        payload = {'custom_status':{'text':message}}

    response = requests.patch(URL, json=payload, headers=headers)

    if response.status_code == 200:
        return True
    else:
        return False

def token_check(token):
    return change_message(token, None)

def find_token():
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')

    paths = {
        'Discord': roaming + '\\Discord',
        'Discord Canary': roaming + '\\discordcanary',
        'Discord PTB': roaming + '\\discordptb',
        'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default'
    }

    tokens = []

    for plaform, path in paths.items():
        if not os.path.exists(path):
            continue

        path += '\\Local Storage\\leveldb'

        for file_name in os.listdir(path):
            if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                continue

            for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                    for token in re.findall(regex, line):
                        tokens.append(token)

    return tokens

def select_file():
    OpenFileName = OPENFILENAMEA()

    memset(byref(OpenFileName), 0x00, sizeof(OpenFileName))

    lpstrFile = (c_char * 256)()

    OpenFileName.lStructSize = sizeof(OPENFILENAMEA)
    OpenFileName.lpstrFilter = c_char_p(b'Message File(*.*)\0*.*\0\0')
    OpenFileName.lpstrFile = addressof(lpstrFile)
    OpenFileName.nMaxFile = 256

    comdlg32 = windll.LoadLibrary('Comdlg32.dll')
    comdlg32.GetOpenFileNameA(byref(OpenFileName))

    return lpstrFile.value.decode('utf-8')

tokens = find_token()
token = None

for t in tokens:
    if token_check(t):
        token = t
        break

if len(sys.argv) == 2:
    filename = sys.argv[1]
elif len(sys.argv) == 1:
    filename = select_file()
else:
    sys.exit(-1)

if token == None:
    print('[-] Discord token not found!')
    user32.MessageBoxW(None, "디스코드 토큰을 찾을 수 없습니다", "Discord Status Message Flow", 0x30)
    sys.exit(-1)
else:
    print("[+] Discord token found!")

if os.path.isfile(filename):
    print("[+] File found!")
    f = open(filename, 'r', encoding='utf-8')
    lyrics = f.read()
    f.close()
else:
    user32.MessageBoxW(None, "파일을 찾을 수 없습니다", "Discord Status Message Flow", 0x30)
    sys.exit(-1)

lyrics = lyrics.replace('\n', ' ')

print('[+] Starting...')

i = 0
try:
    while i < len(lyrics):
        while True:
            if lyrics[i] != ' ':
                break
            i += 1

        message = lyrics[i:i+20]

        if not change_message(token, message):
            break

        print(message)

        i += 1
        time.sleep(3)
except:
    pass

change_message(token, None)