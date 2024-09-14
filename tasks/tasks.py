import argparse
import os
from win11toast import toast

def create_parser():
    parser = argparse.ArgumentParser(description="Taskito Todo List App")
    parser.add_argument("-a", "--add", metavar="", help="Add a task")
    parser.add_argument("-l", "--list", action="store_true", help="See All Tasks")
    parser.add_argument("-r", "--remove", metavar="", help="Remove a task")
    return parser


def add_task(task):
    with open("database.txt", "w") as file:
        file.write(task + "\n")
        try:
            toast('Taskio', 'A new task added', audio='ms-winsoundevent:Notification.Reminder', duration="short")
        except TypeError:
            pass





def list_tasks():
    if os.path.exists("database.txt"):
        with open("database.txt", "r") as db:
            tasks = db.readlines()
            for i, task in enumerate(tasks, start=1):
                print(f"{i}-{task}")
    else:
        toast('Taskio', 'There is no task yet', audio='ms-winsoundevent:Notification.Reminder')





def remove_task(index):
    if os.path.exists("database.txt"):
        with open("database.txt", "r") as db:
            tasks = db.readlines()
        with open("database.txt", "w") as db:
            for i, task in enumerate(tasks, start=1):
                if i != index:
                    db.write(task)
            toast('Taskio', 'Task Removed')
    else:
        toast('Taskio', 'There is no task yet', audio='ms-winsoundevent:Notification.Reminder')



def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.add:
        add_task(args.add)
    elif args.list:
        list_tasks()
    elif args.remove:
        remove_task(int(args.remove))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()


