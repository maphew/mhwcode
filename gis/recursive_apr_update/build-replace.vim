:" go through file list and change:
:"	C:\Vince\Arc view\105m.apr
:" to:
:"	:e! C:/Vince/Arc\ view/105m.apr
:"	:w C:/Vince/Arc\ view/105m.apr.orig
:"	:source! x:/replace.vim
:"
:%s/\\/\//ge	" switch backslash to foreslash
:%s/ /\\\ /ge	" preface a space with a backslash
:%s/[~@!#$%^&()}{;'",.]/\\&/ge	" do the same for punctuation characters
:"
:" ^.*$				match whole line 	(c:/vince/105m/105m.apr)
:" :e! &\r			put :edit in front	(:e! c:/vince/105m/105m.apr)
:" :w &.orig\r			make backup 		(:w c:/vince/105m/105m.apr)
:" :source! x:\/replace.vim	add run replace script	
:"
:%s/^.*$/:e! &\r:w &.orig\r:source! x:\/replace.vim/e
:"
:w! apr-list.vim	" save as script
:q			" exit vim
