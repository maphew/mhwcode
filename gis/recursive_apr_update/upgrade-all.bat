@echo off
echo.
echo	°upgrade-all.bat° RRGIS		- mhw -		* 2001-March-20 *
echo.
echo	This batch file upgrades ArcView project files to work with 
echo	version 2.0 of the RRGIS Repository. It's steps are:
echo.
echo	-Create a list of all .APR files under current directory (.\apr-list.txt)
echo	-Build todo list from the apr list (.\apr-list.vim)
echo	-Run x:\replace.vim on the todo list
echo.
echo	...this could take awhile.
echo.
pause

:: build apr-list
dir /s/b *.apr > apr-list.txt

:: transmogrify apr-list into vim todo list
vim -s x:/build-replace.vim apr-list.txt

:: add commands to todo list to cut down on the screen noise
echo :visual 	>  prefix.vim
echo :set nosc  >> prefix.vim
echo Q 		>> prefix.vim
type prefix.vim 	>  apr-list.vim2
type apr-list.vim 	>> apr-list.vim2
echo :q 		>> apr-list.vim2
del apr-list.vim
del prefix.vim
rename apr-list.vim2 apr-list.vim
	

:: upgrade the APR files, this is where the work actually happens.
vim -n -s apr-list.vim
	:: -n = no swap file
	
echo.
echo	°upgrade-all.bat° complete.
echo.