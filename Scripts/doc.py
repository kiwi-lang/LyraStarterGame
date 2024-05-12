import argparse
import os
import shutil
import subprocess

this = os.path.dirname(__file__)

def main():
    base = "E:/Examples/LyraStarterGame/"
    doc = os.path.join(base, "Docs", "Plugins")

    repositories = [
        "Plugins/AsyncMixin",
        "Plugins/CommonUser",            
        "Plugins/GameSettings",                 
        "Plugins/UIExtension",
        "Plugins/CommonGame",          
        "Plugins/GameFeatures/ShooterCore",
        "Plugins/GameFeatures/ShooterExplorer",  
        "Plugins/GameFeatures/ShooterMaps",
        "Plugins/GameFeatures/ShooterTests",  
        "Plugins/GameFeatures/TopDownArena",          
        "Plugins/GameSubtitles",
        "Plugins/ModularGameplayActors",
        "Plugins/CommonLoadingScreen",
        "Plugins/GameplayMessageRouter", 
        "Plugins/PocketWorlds",
    ] + [
        "Plugins/LyraExtTool", 
        "Plugins/LyraExampleContent",
    ]

    for repo in repositories:
        name = repo.split('/')[-1]

        # with open(os.path.join(base, repo, "README.rst"), 'w') as fp:
        #     fp.write(name + '\n')
        #     fp.write("=" * len(name) + '\n\n')

        # with open(os.path.join(doc, name) + '.rst', "w") as fp:
        #     fp.write(f'.. include:: ../../{repo}/README.rst')

        print(name)

        code = os.path.join(base, repo, 'Source')
        content = os.path.join(base, repo, 'Content')

        listclasses(base, repo, code, content)



def parse_file(path):
    import clang.cindex

    macros = [
        "UENUM",
        "UFUNCTION",
        "UPROPERTY",
        "DECLARE_LOG_CATEGORY_EXTERN",
        "IMPLEMENT_MODULE",
        "UCLASS",
        "DEFINE_LOG_CATEGORY_STATIC",
        "UINTERFACE",
        "DECLARE_MULTICAST_DELEGATE_OneParam",
        "DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam",
        "DECLARE_DELEGATE_OneParam",
        "DECLARE_DYNAMIC_DELEGATE_TwoParams",
        "GENERATED_BODY"
    ]

    macros_api = [
        "UIEXTENSION_API",
        "GAMEPLAYMESSAGERUNTIME_API",
        "COMMONLOADINGSCREEN_API",
        "GAMESUBTITLES_API",
        "GAMESETTINGS_API",
        "COMMONUSER_API",
        "ASYNCMIXIN_API",
        "MODULARGAMEPLAYACTORS_API"
    ]

    index = clang.cindex.Index.create()
    args=['-x', 'c++']
    args.extend(["-D" + macro + "(...)" for macro in macros])
    args.extend(["-D" + macro for macro in macros_api])

    with open(os.path.join(this, 'macros.h'), 'r') as fp:
        code = fp.read() + "\n\n"

    with open(path, 'r') as fp:
        code += fp.read() + "\n\n"

    # print(code)
    print(path)
    translation_unit = index.parse(path, args=args) # None, unsaved_files=[("whatever.h", code)])
    # translation_unit = index.parse(None, unsaved_files=[("whatever.h", code)])

    valid = (
        clang.cindex.CursorKind.CLASS_DECL,
        clang.cindex.CursorKind.STRUCT_DECL,
        clang.cindex.CursorKind.ENUM_DECL,
        clang.cindex.CursorKind.FUNCTION_DECL
    )

    for cursor in translation_unit.cursor.walk_preorder():
        if cursor.kind.is_declaration() or cursor.is_definition():
            #if cursor.kind in valid:
            print("    ", cursor.spelling, cursor.is_definition(), cursor.type.spelling)



def listclasses(base, repo, code, content):
    if not os.path.exists(code):
        return

    stream = []
    def add(*args):
        stream.append(" ".join(args) + "\n")
    
    for (root, _ ,files) in os.walk(code, topdown=True): 
        if len(files) > 0:
            for f in files:
                if f.endswith('.h'):
                    header = os.path.join(root, f)
                    parse_file(header)
                
    # with open(os.path.join(base, repo, "README.rst"), 'a') as fp:
    #     fp.write("Classes\n")
    #     fp.write("-------\n")
    #     fp.write("\n")
    #     fp.write(".. code-block: txt\n")
    #     fp.write(lines)

def listfiles(base, repo, code, content):
    stream = []
    def add(*args):
        stream.append(" ".join(args) + "\n")

    if os.path.exists(code):
        add("    Code")

        for (root,dirs,files) in os.walk(code, topdown=True): 
            if len(files) > 0:
                basepath = root.removeprefix(code + "\\")
                for f in files:
                    if not f.endswith('cs'):
                        add("       ",  os.path.join(basepath, f))

    if os.path.exists(content):
        add("    Content")
        for (root,dirs,files) in os.walk(content, topdown=True): 
            if len(files) > 0:
                basepath = root.removeprefix(content + "\\")
                basepath = basepath.removeprefix(content)

                if len(files) > 10:
                    add("       ", basepath )
                    continue

                for f in files:
                    if (not basepath.startswith("__ExternalActors__")) and (not basepath.startswith("__ExternalObjects__")):
                        add("       ",  os.path.join(basepath, f))

    lines = "".join(stream)

    with open(os.path.join(base, repo, "README.rst"), 'a') as fp:
        fp.write("Files\n")
        fp.write("-----\n")
        fp.write("\n")
        fp.write(".. code-block: txt\n")
        fp.write(lines)


if __name__ == "__main__":
    main()
