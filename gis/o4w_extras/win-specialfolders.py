import ctypes
from ctypes.wintypes import HWND, HANDLE, DWORD, LPCWSTR, MAX_PATH
ctypes.create_unicode_buffer

SpecialFolders={
   'Desktop':0,
   'Programs':2,
   'MyDocuments':5,
   'Favorites':6,
   'Startup':7,
   'Recent':8,
   'SendTo':9,
   'StartMenu':11,
   'MyMusic':13,
   'MyVideos':14,
   'NetHood':19,
   'Fonts':20,
   'Templates':21,
   'AllUsersStartMenu':22,
   'AllUsersPrograms':23,
   'AllUsersStartup':24,
   'AllUsersDesktop':25,
   'ApplicationData':26,
   'PrintHood':27,
   'LocalSettingsApplicationData':28,
   'AllUsersFavorites':31,
   'LocalSettingsTemporaryInternetFiles':32,
   'Cookies':33,
   'LocalSettingsHistory':34,
   'AllUsersApplicationData':35
}


SHGetFolderPath = ctypes.windll.shell32.SHGetFolderPathW
SHGetFolderPath.argtypes = [HWND, ctypes.c_int, HANDLE, DWORD, LPCWSTR]
auPathBuffer = ctypes.wintypes.create_unicode_buffer(MAX_PATH)

for i in SpecialFolders:
   try:
       exit_code=SHGetFolderPath(0, SpecialFolders[i], 0, 0,
auPathBuffer)
       print "%s - %s = %s" % (SpecialFolders[i],i,auPathBuffer.value)
   except:pass

