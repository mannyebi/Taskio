import argparse
import os
from win11toast import notify, toast
import curses
import psycopg2
import asyncio
import threading
import time
import sys
import var


def create_parser():
   
    parser = argparse.ArgumentParser(description="Taskito Todo List App")
    parser.add_argument("-a", "--add", metavar="", help="Add a task")
    parser.add_argument("-l", "--list", action="store_true", help="See All Tasks And Edit Them")
    return parser



def get_connection():
    """make the connnection
    Returns:
        idk :)
    """
    connection = psycopg2.connect(
        host= var.HOST,
        dbname= var.DBNAME,
        user= var.USER, 
        password= var.PASS, 
        port= 5432
        )
    return connection



def is_empty_or_whitespace(text):
    """Check if the given text is empty or contains only whitespace.

    Returns:
        bool: returns true if the text is only white spaces
    """
    return not text.strip()



def print_menu(stdscr, current_row, tasks):
        """get the fetched tasks and show them
        """
        stdscr.clear()
        for i, task in enumerate(tasks, start=0):
            if i == current_row:
                if task[2]:
                    stdscr.addstr(i, 0, f"> {task[1].strip()} - [X]", curses.color_pair(1))  # Highlighted
                else:
                    stdscr.addstr(i, 0, f"> {task[1].strip()} - [ ]", curses.color_pair(1))  # Highlighted
            else:
                if task[2]:
                    stdscr.addstr(i, 0, f" {task[1].strip()} - [X]")
                else:
                    stdscr.addstr(i, 0, f" {task[1].strip()} - [ ]")
        stdscr.refresh()



def add_task_to_db(task):
    """add a task to database

    Args:
        task (str): the task which user inputed

    Returns:
        None
    """
    conn = get_connection()
    with conn.cursor() as cursor:
        try:
            cursor.execute("INSERT INTO tasks (task, status) VALUES (%s, %s)", (task, False))
            conn.commit()
        finally:
            cursor.close()
    


def fetch_tasks():
    """fetch all tasks and return them as a list

    Args:
        None
    
    Returns:
        List: list of all tasks
    """
    conn = get_connection()
    with conn.cursor() as cursor:
        try:
            cursor.execute("SELECT * FROM tasks ORDER BY id;")
            rows = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    return rows



def change_task_status(taskId, status):
    """changes the status of a specific task.
    
    Args:
        taskId (int): the Pk of the task.
        status (bool): the current status of the task.

    Returns:
        None

    Note:
        if the current status is true, this function will change it to false. and inversly ...
    """
    conn = get_connection()
    with conn.cursor() as cursor:
        try:
            if status:
                cursor.execute(f"""UPDATE tasks
                            SET status= %s
                            WHERE id= %s
                                """, (False, taskId))
                conn.commit()
            else:
                cursor.execute(f"""UPDATE tasks
                            SET status = %s
                            WHERE id= %s
                                """, (True, taskId))
                conn.commit()
        finally:
            cursor.close()
            conn.close()



def edit_task_title(taskId, Newtask):
    """change the task title of a specific task.

    Args:
        taskId(int) : primary key of a specific task

    Returns:
        None
    """
    conn = get_connection()
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                """
                UPDATE tasks
                SET task = %s
                WHERE id = %s
                """, (Newtask, taskId)
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()



def delete_task(taskId):
    """delete a specific task

    Args:
        taskId(int): pk of the task

    Returns:
        None
    """
    conn = get_connection()
    with conn.cursor() as cursor:
        try:
            cursor.execute(
                """DELETE FROM tasks WHERE id = %s
                """, (taskId,)
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()



def dialog_page(stdscr, text=None):
    """show a dialog that user choose yes/no and return the answer.

    Args:
        stdscr():...
        text(str, optional):show the desired message

    Returns:
        bool: yes or no
    """
    stdscr.clear()
    options = ["Yes", "No"]
    option_index = 0
    start_color()
    dialog_text = text
    dialog_length = len(dialog_text) if dialog_text is not None else 0
    while True:
        for idx, option in enumerate(options):
            if idx == option_index:
                stdscr.addstr(0, dialog_length + (idx*5), option, curses.color_pair(4))
            else:
                stdscr.addstr(0, dialog_length + (idx*5), option, curses.color_pair(1))

        stdscr.addstr(0, 0, dialog_text, curses.color_pair(1))
        key = stdscr.getch()
        if key == ord('q'):
            sys.exit()
        if key == curses.KEY_ENTER or key in [10, 13]:
            if option_index == 0:#yes
                dialog_result = True
                break
            else:
                dialog_result = False
                break
        option_index = X_changer(key, option_index, len(options))
    return dialog_result



def add_task(task):
    """add task to db.
    """
    
    if not is_empty_or_whitespace(task):
        try:
            notify('Taskio', 'A new task added', audio='ms-winsoundevent:Notification.Reminder', duration="short")
        except TypeError:
            pass
        db_thread = threading.Thread(target=add_task_to_db, args=(task,))
        db_thread.start()
    else:
        notify('Taskio', 'use taskio -h for help', audio='ms-winsoundevent:Notification.Reminder', duration="short")




def loader(stdscr):
    stdscr.addstr(0, 0, f"Loading... ")
    stdscr.refresh()



def task_not_available(stdscr):
    start_color()
    stdscr.addstr(0, 0, "No tasks available press ENTER to add a task.", curses.color_pair(2))
    stdscr.refresh()
    stdscr.getch()  



def row_changer(current_row, key, maxrow):
    if key == curses.KEY_UP and current_row > 0:
        current_row -= 1
    elif key == curses.KEY_DOWN and current_row < maxrow-1:
        current_row += 1
    return current_row



def start_color():
    """defines the color using python curses
    """
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)



def X_changer(key, option_index, max_index):
    """accoriding to key variable change the X position and return it
    """
    if key == curses.KEY_RIGHT and option_index < max_index-1:
        option_index += 1
    elif key == curses.KEY_LEFT and option_index > 0:
        option_index -= 1
    return option_index



def get_text(stdscr, description=None):
    """Get the user's input and clean it and then return it 

    Args:
        stdscr(_curses.window): required.
        description(str, optional): desired text for show, before getting the user's input.

    Returns:
        str: the user's cleaned input text
    """
    stdscr.clear()
    curses.echo()
    if description:
        stdscr.addstr(0, 0, f"{description} : ", curses.color_pair(1))
    else:
        pass
    text = str(stdscr.getstr(1, 0, 64))
    text = text.split("'")[1].strip() #this is so crucial for cleaning the user's inputed data.
    return text



def task_options(task, stdscr):
    """shows a task with options including check as done, editing, deleteing.
    """
    stdscr.clear()
    options = ["Done", "Edit", "Delete"]
    option_index = 0
    start_color()
    while True:
        
        task_text = f"> {task[1]} - "
        

        for idx, option in enumerate(options): #show options
            start_x_position = len(task_text) #this is shows the position of X that the task text is done and we can add our options with some spaces.
            
            if idx == option_index:
                stdscr.addstr(0, start_x_position + (idx * 5), option, curses.color_pair(2))
            else:
                stdscr.addstr(0, start_x_position + (idx * 5), option, curses.color_pair(1))
        stdscr.addstr(0, 0, task_text, curses.color_pair(1))
        stdscr.refresh()
        key = stdscr.getch()
        if key == ord('q'):
            print('q2 pressed')
            sys.exit()

        elif key == curses.KEY_ENTER or key in [10, 13]: 
            try:
                if option_index == 0: #Done Option, Which changes to status of tasks from true to false and inverse ...
                    change_task_status(task[0], task[2])
                    notify('Taskio', 'Tasked Updated', audio='ms-winsoundevent:Notification.Reminder', duration="short")
                    break

                elif option_index == 1: #Editing option, which user can edit the tasks's title ...
                    text = get_text(stdscr, f"Edit Task {task[1]}")
                    edit_task_title(task[0], text)
                    notify('Taskio', 'Tasked Updated', audio='ms-winsoundevent:Notification.Reminder', duration="short")
                    break

                elif option_index == 2: #Deleting Option, which shows a yes/no dialog first

                    dialog = dialog_page(stdscr, f"Are you sure you want to delete {task[1]} ? ")
                    if dialog :
                        print('yes')
                        delete_task(task[0])
                        notify('Taskio', 'Tasked Deleted', audio='ms-winsoundevent:Notification.Reminder', duration="short")
                        break
                    else:
                        print('no')
                        break
            except:
                pass
            break
        
        option_index = X_changer(key, option_index, len(options) )

    return list_tasks



def list_tasks(stdscr):
    """show a list of tasks. while tasks are fetching, show loader
    """
    stdscr.clear()

    for _ in range(20):
        loader(stdscr)
        tasks = fetch_tasks()
        if tasks:
            stdscr.clear()
            break
    

    if not tasks:
        task_not_available(stdscr)
        while True:
            key = stdscr.getch()
            if key == curses.KEY_ENTER or key in [10, 13]:
                task = get_text(stdscr, "Write The Task You Want To Add")
                add_task(task)
                return list_tasks(stdscr)
            elif key == ord("q"):
                sys.exit()

            
                    

    start_color()
    current_row = 0

    while True:
        print_menu(stdscr, current_row, tasks)
        key = stdscr.getch()
        if key == ord('q'):
            sys.exit()
        elif key == curses.KEY_ENTER or key in [10, 13]:
            while True:
                stdscr.clear()
                refresh = task_options(tasks[current_row], stdscr)
                refresh(stdscr)
        current_row = row_changer(current_row, key, len(tasks))
        print_menu(stdscr, current_row, tasks)



def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.add:
        add_task(args.add)
    elif args.list:
        curses.wrapper(list_tasks)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()


