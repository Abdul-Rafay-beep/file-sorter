#========= Import =========
lazy from mimetypes import guess_type
lazy from os import path, makedirs, listdir
lazy from pathlib import Path

#========== Exports =========
__all__=['DirReader', 'check_dir', 'Dir']

#======== Check dir ========
def check_dir(dir:str):
    if not path.exists(dir):
        return []
    l = listdir(dir)
    for i in l:
        l.insert(l.index(i), path.join(dir, i))
        l.remove(i)
    return l

#========== DFS ==========
class Dir:
    """
    Used by program to save dir location and its child
    in same identifier
    """
    __slots__=['path', 'content']
    def __init__(self, dir:str):
        self.path=dir
        self.content = check_dir(dir)

#========== DirReader ==========
class DirReader:
    """
    Create object to handle file Searcing. Support DPS

    Attributes:
    main_dir -> the location where unsorted files are present
                Add this either during obj creation or manually
                access obj.main_dir

    stdout -> bool: Whether to show outputs of the process, on
              terminals or not.

    sort_rule -> SortRule obj: Rules of where to sort
                 files of different types.

    _queue -> Search and Queue (index) all files in the main dir.
              Better is not to alter it, and let the system index
              them programmatically.

    Methods:
        read_target: Create the Output directorys that aren't present,
                     to prepare the enviroment.
                     Ask for providing sort rule or use self.sort_rule
                     attribute.

        index: Use DFS algorithm to search all and queue all files.

    """
    __slots__=['main_dir', 'sort_rule', 'stdout', '_queue']
    def __init__(self, main_dir:str, stdout:bool=True):
        """
        main_dir: The location of the dir containing
        unsorted file.
        stdout: Whether to use print statements
        """
        self.main_dir = main_dir
        self.stdout = stdout
        self.sort_rule = None
        self._queue = []

    #-------- Read Target ---------
    def read_target(self, sort_rule:dict=None):
        """
        Create Dirs where the files will be moved
        Use stdout to display result

        sort_rule: Dict that saves rules.
                   If already set, pass None
        """
        if sort_rule:
            self.sort_rule = sort_rule

        if self.sort_rule:
            for key in self.sort_rule.keys():
                if key == 'ignore':
                    self.sort_rule[key] = [Path(i) for i in self.sort_rule[key] if i.__class__ is str]
                if not self.sort_rule[key].__class__ is str:
                    continue
                if not path.exists(self.sort_rule[key]):
                    makedirs(self.sort_rule[key], exist_ok=True)
                    if self.stdout:
                        print(f"Missing dir created: ", self.sort_rule[key])
        return self

    #-------- index_file ---------
    def index(self):
        """
        Use DFS to index files in the main_dir.
        The results will be saved in self._queue
        """
        self.__DFS()
        return self

    #-------- DFS algorithm ---------
    def __DFS(self, dir:str = ''):
        if dir and path.exists(dir):
            dirobj = Dir(dir)
        else:
            dirobj = Dir(self.main_dir)

        for i in dirobj.content:
            if Path(i) in self.sort_rule.get('ignore', []):
                continue
            if path.isfile(i) and i not in self._queue:
                self._queue.append(i)
            else:
                try:
                    self.__DFS(i)
                except RecursionError:
                    return self
        return self

    #------- Move File --------
    def move_file(self, read_target:bool=True, index:bool=True):
        """
        Move the files to their target folder
        as described in the sort_rule
        read_target: Runs self.read_target() before proceeding.
                     Pass False if runned already.
        
        index: Run self.index() before proceeding. Pass False is
               runned already.
        """
        if read_target:
            self.read_target()
        if index:
            self.index()
        for i in self._queue:
            ty = guess_type(i)[0]
            target = self.sort_rule.get(ty)
            if target is None:
                target = self.sort_rule.get(ty.split('/')[0])
            
            if target is None or not path.exists(str(target)):
                continue
            try:
                Path(i).move_into(target)
                if self.stdout:
                    print(i , ' -- Moved successfully')
            except Exception as e:
                if self.stdout:
                    print('[Error]: ', e)
        self._queue.clear()