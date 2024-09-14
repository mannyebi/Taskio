import argparse
import os
from win11toast import notify, toast
import curses

def create_parser():
    parser = argparse.ArgumentParser(description="Taskito Todo List App")
    parser.add_argument("-a", "--add", metavar="", help="Add a task")
    parser.add_argument("-l", "--list", action="store_true", help="See All Tasks")
    parser.add_argument("-r", "--remove", metavar="", help="Remove a task")
    return parser


def add_task(task):
    with open("database.txt", "a") as file:
        file.write(task + " | " + "*" + "\n")
        try:
            notify('Taskio', 'A new task added', audio='ms-winsoundevent:Notification.Reminder', duration="short")
        except TypeError:
            pass





def list_tasks(stdscr):
    # Clear the screen

    

    if os.path.exists("database.txt"):
        with open("database.txt", "r") as db:
            tasks = db.readlines()

        if not tasks:
            stdscr.addstr(0, 0, "No tasks available.", curses.color_pair(2))
            stdscr.refresh()
            stdscr.getch()  # Wait for a key press before exiting
            return

        # Initialize the selected task index
        current_row = 0

        # Function to display the tasks and highlight the selected one
        def print_menu(stdscr, current_row):
            for i, task in enumerate(tasks):
                if i == current_row:
                    stdscr.addstr(i, 0, f"> {task.strip()}", curses.color_pair(2))  # Highlighted
                else:
                    stdscr.addstr(i, 0, f"  {task.strip()}")
            stdscr.refresh()

        # Initialize curses colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)

        print_menu(stdscr, current_row)

        while True:
            key = stdscr.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(tasks) - 1:
                current_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                stdscr.addstr(len(tasks), 0, f"You selected: {tasks[current_row].strip()}")
                stdscr.refresh()
                stdscr.getch()  # Wait for a key press before exiting
                break

            print_menu(stdscr, current_row)
    else:
        curses.endwin()  # End curses to show the notification
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
        curses.wrapper(list_tasks)
    elif args.remove:
        remove_task(int(args.remove))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()


