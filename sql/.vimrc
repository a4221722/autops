set nocompatible              " required
filetype off                  " required

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
  
"alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')
"  
" let Vundle manage Vundle, required
Bundle 'gmarik/vundle'

" Add all your plugins here (note older versions of Vundle used Bundle  instead of Plugin)
Plugin 'gmarik/Vundle.vim'
Plugin 'vim-scripts/indentpython.vim'
Plugin 'scrooloose/syntastic'
Plugin 'scrooloose/nerdtree'
"Plugin 'Valloric/YouCompleteMe'
    


" All of your Plugins must be added before the following line
call vundle#end()            " required
filetype plugin indent on    " required

" Enable folding
set foldmethod=indent
set foldlevel=99
nnoremap <space> za


let python_highlight_all=1
syntax on

au BufNewFile,BufRead *.py set number 
au BufNewFile,BufRead *.py set number 
au BufNewFile,BufRead *.py set expandtab
au BufNewFile,BufRead *.py set tabstop=4
au BufNewFile,BufRead *.py set shiftwidth=4
au BufNewFile,BufRead *.py set softtabstop=4
au BufNewFile,BufRead *.py set encoding=utf-8
au BufNewFile,BufRead *.py set autoindent

:syntax on

"F2开启和关闭树"
"map <F2> :NERDTreeToggle<CR>
"let NERDTreeChDirMode=1
""显示书签"
let NERDTreeShowBookmarks=1
"设置忽略文件类型"
"let NERDTreeIgnore=['\~$', '\.pyc$', '\.swp$']
""窗口大小"
let NERDTreeWinSize=25

set encoding=utf-8
set fileencodings=utf-8,gbk
set termencoding=utf-8
let &termencoding=&encoding
