"""
Useable Items:
check_dir :: function -> Give list of children o a parent dir
Dir :: class -> Saves parent and children node
DirReader :: class -> Handles file Indexing and sorting.

Sorting Rules: dict of rules
Keys must be mimetype either broader or specific.
Example:
    broader: 'image'
    specific: 'image/png'
'ignore' key saves list of files or dirs to be ignored in DFS.
Example sort_rule:
{
  'image': 'D:/test/images',
  'image/svg': 'D:/test/images/svgs,
  'application': 'D:/test/applications',
  'application/javascript': 'D:/test/applications/js'
  'ignore': [
             'D:/test/.venv',
             'D:/.gitignore
            ]
}
File whose location rule is not defined (in the above example, all
text file), will not touched.
"""
#========= Import =========
lazy from mimetypes import guess_type
lazy from os import path, makedirs, listdir, PathLike
lazy from pathlib import Path

#========== Exports =========
__all__=['DirReader', 'check_dir', 'Dir']

#======== Check dir ========
def check_dir(dir:str) -> list[str]:
    """Provides list of absolute paths of children"""
    # os.path.exists can handle str|int|bytes|os.PathLike.
    # This whole module works on str, so the function restricts
    # type to string only.
    if dir.__class__ is not str:
        return []
    if not path.exists(dir):
        return []
    l = listdir(dir)
    return [path.join(dir, i) for i in l]

#========== DFS ==========
class Dir:
    """
    Used by program to save dir location and its child
    in same identifier.
    Attributes:
        path -> str: absolute path of the parent dir

        content -> list of absolute path of children.
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
              terminals or not. Add this either during object
              creation of manually access obj.main_dir

    sort_rule -> dict: Rules of where to sort
                 files of different types. Add this using obj.sort_rule
                 or pass it while using read_target.

    _queue -> Saves Queue (index) of all files in the main dir.
              Better is not to alter it, and let the system index
              them programmatically.

    Methods:
        read_target -> Create the Output directories that aren't present,
                     to prepare the enviroment.
                     Ask for providing sort rule or use self.sort_rule
                     attribute instead

        index -> Use DFS algorithm to search all and queue all files.

        move_file -> Start the file sorting process. By default, it
                     automatically calls self.read_target() and self.index()
                     This behavior is modifiable
    """
    __slots__=['main_dir', 'sort_rule', 'stdout', '_queue']
    def __init__(self, main_dir:str, stdout:bool=False):
        """
        main_dir: The location of the dir containing
        unsorted file.
        stdout: Whether to use print statements
        """
        # The default value of stdout is kept False, because most
        # production ready programs doesn't uses cmd output.
        # The stdout can also be captured using subprocess, to show
        # in in-app console UI.
        self.main_dir = main_dir
        self.stdout = stdout
        self.sort_rule = None
        self._queue = set()

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
                    # Converted all files to pathlib.Path
                    # This is because __DFS has to compare to
                    # Paths to check whether it has to be ignored
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
    # DFS was first tried to make as a function
    # but it was found difficult is running recursive
    # rule. Using it as method give robust polimorphism
    def __DFS(self, dir:str = None):
        if dir is not None and path.exists(dir):
            dirobj = Dir(dir)
        else:
            dirobj = Dir(self.main_dir)

        for i in dirobj.content:
            if Path(i) in self.sort_rule.get('ignore', []):
                continue
            if path.isfile(i):
                self._queue.add(i)
            else:
                try:
                    self.__DFS(i)
                except RecursionError:
                    return self
                except Exception as e:
                    if self.stdout:
                        print(e)
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

        This function automatically run self.read_target() and
        self.index(), so you not need to call them manually. To
        prevent this, explicitly pass False to default arguments.
        """
        if read_target:
            self.read_target()
        if index:
            self.index()
        for i in self._queue:
            ty = guess_type(i)[0]
            if ty is None:
                continue
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
                    print(e)
        self._queue.clear()