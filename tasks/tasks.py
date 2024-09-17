import argparse
import os
from win11toast import notify, toast
import curses
import locale

locale.setlocale(locale.LC_ALL, '')


def create_parser():
    parser = argparse.ArgumentParser(description="Taskito Todo List App")
    parser.add_argument("-a", "--add", metavar="", help="Add a task")
    parser.add_argument("-l", "--list", action="store_true", help="See All Tasks And Edit Them")
    parser.add_argument("-r", "--remove", metavar="", help="Remove a task")
    return parser


def is_empty_or_whitespace(text):
    """Check if the given text is empty or contains only whitespace."""
    return not text.strip()



def add_task(task):
    with open("database.txt", "a") as file:
        file.write(task + " | " + "-" + "\n")
        try:
            notify('Taskio', 'A new task added', audio='ms-winsoundevent:Notification.Reminder', duration="short")
        except TypeError:
            pass



def list_tasks(stdscr):
    # Clear the screen
    stdscr.clear()

    if os.path.exists("database.txt"):
        with open("database.txt", "r") as db:
            tasks = db.readlines()

        if not tasks:
            stdscr.addstr(0, 0, "No tasks available.")
            stdscr.refresh()
            stdscr.getch()  # Wait for a key press before exiting
            return

        # Initialize the selected task index
        current_row = 0

        # Function to display the tasks and highlight the selected one
        def print_menu(stdscr, current_row):
            for i, task in enumerate(tasks):
                if i == current_row:
                    stdscr.addstr(i, 0, f"> {task.strip()}", curses.color_pair(1))  # Highlighted
                else:
                    stdscr.addstr(i, 0, f"  {task.strip()}")
            stdscr.refresh()

        # Initialize curses colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)

        print_menu(stdscr, current_row)

        while True:
            key = stdscr.getch()

            if key == ord('q'):
                return

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(tasks) - 1:
                current_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                # Task selected; now show "Done Edit Remove"
                options = ["Done", "Edit", "Remove"]
                option_index = 0

                while True:
                    stdscr.clear()

                    # Display the selected task (static)
                    stdscr.addstr(0, 0, f"> {tasks[current_row].strip()} - ", curses.color_pair(1))
                    
                    # Display the options ("Done Edit Remove")
                    for idx, option in enumerate(options):
                        # Set the starting position after the static task text
                        start_x = len(f"> {tasks[current_row].strip()} - ")

                        if idx == option_index:
                            stdscr.addstr(0, start_x + (idx * 5), option, curses.color_pair(2))  # Highlighted option
                        else:
                            stdscr.addstr(0, start_x + (idx * 5), option, curses.color_pair(1))  # Normal option

                    stdscr.refresh()

                    # Get user input for option selection
                    key = stdscr.getch()

                    if key == ord('q'):
                        return

                    # Navigate between "Done", "Edit", and "Remove"
                    if key == curses.KEY_LEFT and option_index > 0:
                        option_index -= 1
                    elif key == curses.KEY_RIGHT and option_index < len(options) - 1:
                        option_index += 1
                    elif key == curses.KEY_ENTER or key in [10, 13]:
                        if option_index == 0:
                            Task_status(current_row)
                            return
                        elif option_index == 1:
                            stdscr.clear()
                            curses.echo()
                            stdscr.addstr(0, 0, f"Edit Task -> {tasks[current_row]} ", curses.color_pair(1))
                            text = str(stdscr.getstr(1, 0, 64))
                            text = text.split("'")[1].strip()
                            Edit_task(current_row, text)
                            return
                        elif option_index == 2:
                            remove_task(current_row+1)
                            return
                        
                        stdscr.refresh()
                        stdscr.getch()  # Wait for a key press before exiting
                        break



            print_menu(stdscr, current_row)
    else:
        curses.endwin()  # End curses to show the notification
        toast('Taskio', 'There is no task yet', audio='ms-winsoundevent:Notification.Reminder')



def remove_task(index):
    if os.path.exists("database.txt"):
        with open("database.txt", "r") as file:
            tasks = file.readlines()
        with open("database.txt", "w") as file:
            for i, task in enumerate(tasks, start=1):
                if i != index:
                    file.write(task)
        notify("Taskio", "Task removed successfully.")
    else:
        notify("Taskio", "No tasks found.")
   


def Edit_task(index, Task):
    with open("database.txt", "r") as db:
        tasks = db.readlines()
    with open("database.txt", "r") as db:
        for i, task in enumerate(tasks):
            if i == index:
                if is_empty_or_whitespace(Task):
                    print('empt')
                    tasks[i] = task

                else:
                    tasks[i] = f"{Task.strip()} | * \n"
    with open('database.txt', 'w') as file:
        file.writelines(tasks)
    notify('Taskio', 'Task Edited')



def Task_status(index):
    with open("database.txt", "r") as db:
            tasks = db.readlines()

    for i, task in enumerate(tasks):
        print(i, task)
        if i == index:
            thetask = task.split("|")[0]
            tasks[i] = f"{thetask.strip()} | + \n"
        else:
            tasks[i] = f"{task}"

    with open('database.txt', 'w', encoding="utf-8") as file:
        file.writelines(tasks)
    print("√")
    notify('Taskio', 'Task Updated')





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


