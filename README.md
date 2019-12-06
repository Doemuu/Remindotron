# Remindotron
 Remindotron is a Telegram bot to remind me of tasks I set up. It communicates with a localhost database, which runs on XAMPP. Therefore the bot needs XAMPP to open the port locally.

# Commands
  There is a very slim range of commands. I can only ask for data, clear data and create new data to work with.

  - `/start`
  - `/create`
  - `/cancel`
  - `/request`
  - `/clear`
  - `/today`
  - `/week`

### start
The start command was first implemented to be a testing tool as I have never previously used neither python nor the telegram api. It's purpose is to answer a quick prewritten phrase. \
Like: "I'm a bot, please talk to me!"

### create
The create Command is propably the biggest aspect of the whole bot. It creates new tasks and saves them on the database. In order to do that the bot needs three inputs. The task_name the task_date and finally the task_person. Task_name is a small discription of what the task is about. Task_date is the date on which the task has to be done and task_person is the person who has to do the task.

### cancel
Cancel is only callable during the creation process. It cancels the create command out and stops it from uploading and continuing.

### request
The request Command shows every single task, that has to be done.

### clear
Clear can be called to delete the obsolete, older tasks.

### today
The today Command is to call all the tasks that have to be done by this day.
Therefore it doesn't show the date on which the task has to be done but only the description and the person who has to do it.

### week
The week Command is fairly similar to the today command as it shows all tasks that have to be done during this week.


# Expansion Options

It's possible to make the bot delete old tasks automatically instead of by a user-input.
It's possible to add a command that deletes a task.
It's possible to add a command to show all the tasks of the month, the year and so on.
It's possible to make the bot "inline", so a preview of the commands show up.
