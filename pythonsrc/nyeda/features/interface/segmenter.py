
from nyeda.features.interface import mastertools, FilesystemTree, icons
from nyeda.bin.sharedobject import bundle, secure_delete
from nyeda.features.dismantler import dismantler
from nyeda.features.direngine import dirtools
from nyeda.features.preproc import preproc
from typing import Any

from tkinter.ttk import Panedwindow, Separator
from tkinter.filedialog import askdirectory
from customtkinter import CTkFrame, CTkButton, CTkTextbox

from pathlib import Path

import sys

if sys.platform == 'darwin':
    from nyeda.bin.sharedobject import macos

if sys.platform == 'win32':
    from nyeda.bin.sharedobject import windows

class segmenter(preproc, dismantler, dirtools, mastertools):
    def __init__(self, content: Any, thisfile: str, overwrites: int = 5) -> None:
        # set the global class variable
        setattr(self, '__thisfile__', thisfile)
        setattr(self, '__overwrites__', overwrites)

        # since preprocessing may require a password
        # popup, create a __master__ right now.
        self.__master__ = self.generate_master()
        self.__mastersetup__('Not Your Every Day Archive', icons.segment, (600, 324), False)

        self.__separator__ = Separator(self.__master__, orient='vertical')
        self.__separator__.place(relx=0.5, rely=0.22, height=180)

        # Divide pathway into two: View, Export

        self.__viewbutton__ = CTkButton(self.__master__, text='View', command=self.__view__)
        self.__exportbutton__ = CTkButton(self.__master__, text='Export', command=self.__export__)
        self.__viewbutton__.place(rely=0.5, relx=0.25, anchor='center')
        self.__exportbutton__.place(rely=0.5, relx=0.75, anchor='center')

        # set watchman
        if sys.platform == 'darwin':
            self.__watchman__ = macos.MacosSRCD()
        elif sys.platform == 'win32':
            self.__watchman__ = windows.WindowsSRCD()

        # Bind the master for focus out
        self.__master__.focus_force()
        self.__master__.bind('<FocusOut>', self.__focusout__)
        self.__master__.after(100, self.__watchmanpatrol__)

        self.__content__ = content

        self.__master__.mainloop()
    
    def __view__(self) -> None:
        self.__separator__.place_forget()
        self.__viewbutton__.place_forget()
        self.__exportbutton__.place_forget()
        self.__master__.update()

        # Since this is the view options, there must be a
        # new menu at the top asking for export (Do it Later)

        __processed__ = self.preproc(self.__content__)

        # the window needs to deinconify cause of preproc
        self.__master__.deiconify()

        __dismantled__ = self.dismantle(__processed__)

        # Handle any dismantling errors
        if not hasattr(self, '__dismantlefailure__') or (hasattr(self, '__dismantlefailure__') and getattr(self, '__dismantlefailure__') is True):
            # securely delete the thisfile
            _ = secure_delete.SecureDelete(str(getattr(self, '__thisfile__')), getattr(self, '__overwrites__'))

        # Create the master here

        # Create PannedWindow for the master
        self.__pannedwindow__ = Panedwindow(self.__master__, orient='horizontal')
        self.__pannedwindow__.pack(fill='both', expand=True)
        self.__pannedleft__ = CTkFrame(self.__pannedwindow__, width=200)
        self.__pannedright__ = CTkFrame(self.__pannedwindow__)
        self.__pannedwindow__.add(self.__pannedleft__)
        self.__pannedwindow__.add(self.__pannedright__)

        # Generate metadata to show
        self.__metadata__ = bundle.Structure.get(__dismantled__)
        self.__dirmap__ = self.generate_dirmap(self.__metadata__)

        # Create the filesystem tree
        self.__tree__ = FilesystemTree(self.__pannedleft__)
        self.__tree__.pack(fill='both', expand=True)

        # set the heading to the filesystem tree
        self.__tree__.heading('#0', text='Navigator', anchor='w')

        # set the interactive clicks
        self.__tree__.bind('<<TreeviewSelect>>', self.__nav__)

        # store the nodes for lookup (default: root)
        self.__nodes__ = {'/': self.__tree__.insert('', 'end', text='  /', open=False, image=self.__tree__.__archivetype__)}

        # Create all directories in the first pass
        # Use a sorted order for better readability
        # and structure
        for __path__ in sorted(self.__dirmap__.keys()):
            if __path__ == '/':
                continue

            # Current path and parent path must be derived
            *__parentparts__, __name__ = __path__.strip('/').split('/')
            __parent__ = '/' + '/'.join(__parentparts__) if __parentparts__ else '/'
            # find parent node ID ('' for root)
            __parentnode__ = self.__nodes__.get(__parent__, '')
            # define node structure
            __node__ = self.__tree__.insert(
                parent=__parentnode__,
                index='end',
                text='  ' + __name__,
                open=False,
                image=self.__tree__.__foldertype__,
            )
            # Insert into lookup
            self.__nodes__[__path__] = __node__
        # Add all contents (files and directories) inside the created directories
        for __path__, __contents__ in sorted(self.__dirmap__.items()):
            # get parent node ('' for root)
            __parentnode__ = self.__nodes__.get(__path__, '')

            for __item__ in sorted(__contents__):
                # Construct full path for the item
                __itemfullpath__ = f"{__path__.rstrip('/')}/{__item__}" if __path__ != '/' else f"/{__item__}"
                # If item is already in directory map, it is a directory and was
                # handled above (in first pass)
                if __itemfullpath__ not in self.__dirmap__:
                    self.__tree__.insert(
                        parent=__parentnode__,
                        index='end',
                        text='  ' + __item__,
                        open=False,
                        image=self.__tree__.__filetype__
                    )
        return None

    def __nav__(self, event=None, /) -> None:
        # Get currently selected field from the tree
        __selected__ = self.__tree__.selection()
        if not __selected__: return None
        
        # Destroy all child widgets of the right paned window
        for __child__ in self.__pannedright__.winfo_children():
            __child__.destroy()
        
        # Derive absolute text of the selected field from the tree
        __text__ = self.__tree__.item(__selected__[0], 'text').strip()

        # Try to find full path from the metadata map 
        # (determine if the selected item is a file or directory)
        __sfile__ = None
        if hasattr(self, '__metadata__'):
            for __path__ in self.__metadata__.keys():
                if __path__.endswith(__text__):
                    __sfile__ = __path__
                    break
            
            # if selection is a file
            if __sfile__:
                __content__ = self.__metadata__.get(__sfile__, None)
                if __content__:
                    # Create a TextBox under right paned window
                    __textbox__ = CTkTextbox(self.__pannedright__, height=500, wrap='word')
                    __textbox__.pack(fill='both', expand=True)

                    # Try to decode the content from the bytes to str
                    try:
                        __content__ = __content__.decode()
                        __textbox__.insert('1.0', __content__)
                    except Exception:
                        __textbox__.insert('1.0', 'Currently Supports Text Files Only! This file contains un-convert-able binary data.')
                    finally:
                        __textbox__.configure(state='disabled')
            else:
                # If selection is not a file, trigger opena and close behaviour
                if self.__tree__.item(__selected__[0], 'open'):
                    self.__tree__.item(__selected__[0], open=False)
                else:
                    self.__tree__.item(__selected__[0], open=True)
        return None
    
    def __export__(self) -> None:
        # Get the export location
        self.__master__.attributes('-topmost', False)
        extloc = askdirectory(initialdir=Path.cwd(), mustexist=True, title='Select export location', parent=self.__master__)
        self.__master__.attributes('-topmost', True)
        self.__master__.focus_force()

        if not extloc:
            return None

        __processed__ = self.preproc(self.__content__)
        
        if self.dismantle2(__processed__, extloc) is False:
            _ = secure_delete.SecureDelete(str(getattr(self, '__thisfile__')), getattr(self, '__overwrites__'))
    
    def __watchmanpatrol__(self, event=None, /) -> None:
        if sys.platform == 'darwin' and self.__watchman__.detect():
            self.__watchman__.kill()
            # Normal quit
            self.__quitmainloop__(event)
        self.__master__.after(1, self.__watchmanpatrol__)
    
    def __quitmainloop__(self, event=None, /) -> str:
        self.__quitmaster__(event)
        return 'break'
    
    def __focusout__(self, event=None, /) -> None:
        __focus__ = self.__master__.focus_get()
        if __focus__ is None:
            # this is focusout quit
            self.__quitmainloop__(event)
        else:
            if not str(__focus__).startswith(str(self.__master__)):
                # focus is not on any of the widgets too
                self.__quitmainloop__(event)
    