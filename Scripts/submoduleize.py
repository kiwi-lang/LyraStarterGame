import argparse
import os
import shutil
import subprocess


this = os.path.dirname(__file__)
base = "E:/Examples/LyraStarterGame/"

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
]

def apply(command, ctx=None, **kwargs):
    if ctx is not None:
        kwargs.update(ctx)

    resolved = []
    for cmd in command:
        resolved.append(cmd.format(**kwargs))
    return resolved

def replace_submodule():
    def commands():
        return ["git", "submodule", "add", "git@github.com:kiwi-lang/{name}.git", "{dest}"],
    
    cwd = base
    os.chdir(cwd)

    for repo in repositories:
        name = repo.split('/')[-1]
        rest =  os.path.join(*repo.split('/')[:-1])
        # print(name)

        folder = os.path.join(base, repo)
        # print("delete", folder)
        # shutil.rmtree(folder)
        # print(f"cd {folder}/.. && rm -rf {name}")
        os.makedirs(rest, exist_ok=True)
        
        for cmd in commands():
            cmd = apply(cmd, name=name, dest=repo)
            print(' '.join(cmd))
            subprocess.run(cmd, cwd=cwd)


def init():
    commands = [
        "git init",
        "git remote add origin git@github.com:kiwi-lang/{name}.git",
        "git add --all",
        "git commit -m \"initial_commit\"",
        "git push origin master"
    ]

    for repo in repositories:
        name = repo.split('/')[-1]
        print(name)
        cwd = os.path.join(base, repo)
        shutil.copyfile(os.path.join(this, '.gitignore'), os.path.join(cwd, '.gitignore'))
        for cmd in commands:
            cmd = cmd.format(name=name)
            print(cmd)
            subprocess.run(cmd.split(' '), cwd=cwd)


def commit_all(remote, message, branch, dry):
    commands = [
        ["git", "add", "--all"],
        ["git", "commit", "-m", "{message}"],
        ["git", "push", "{remote}", "{branch}"]
    ]

    for repo in repositories + ["."]:
        name = repo.split('/')[-1]

        print(name)

        cwd = os.path.join(base, repo)
        for cmd in commands:
            cmd = apply(cmd, message=message, remote=remote, branch=branch)

            print(f'    {" ".join(cmd)}')

            if not dry:
                subprocess.run(cmd, cwd=os.path.abspath(cwd))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--message", "-m", type=str, default="-", help="commit message")
    parser.add_argument("--remote", "-r", type=str, default="origin", help="remote")
    parser.add_argument("--branch", "-b", type=str, default="master", help="branch")
    parser.add_argument("--dry", action="store_true", default=False, help="dry run")

    args = parser.parse_args()

    commit_all(args.remote, args.message, args.branch, args.dry)


if __name__ == "__main__":
    main()
