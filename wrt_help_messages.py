#man pages for the commands, served by the different commands

bay_help = '''\
`/bay [text]` - change status emoji to :rocket:
Without [text], running `/bay` shouldn't change your status text, only the emoji,
With [text], your status will be set to [text].

Special commands:
`/bay who` - display a list of people whose current status is :rocket:
`/bay leave` - set your emoji to something else, and set an appropriately sad status text
`/bay help` - display this help'''

agenda_help = '''\
`/agenda [text]` - add an item to the weekly meeting agenda
Without [text], bay area will return a list of enumerated agenda items
With [text], [text] is added as an item, and we'll talk about it at the sunday meeting
The agenda is cleared every Sunday night, and is posted to #general before every meeting

Special commands:
`/agenda clear` - remove all agenda items that you've added.
`/agenda remove [number]` - remove a specific agenda item, by number
                  You cannot remove someone elses item
`/agenda help` - display this help'''

todo_help = '''\
`/todo` - add a todo item
This command is a bloated mess of spaghetti code, bad ideas, and worse implementations.
Bear with me

Different flavours
`/todo` - returns a list of todo items
`/todo text` - adds text as a personal todo item
`/todo [tag] text` - adds text as a todo item to the [tag] list
                     items in a tagged list are viewable to all team members
`/todo [tag] text @username` - adds text as a todo item in [tag] list and 
                               notify @username about that
`/todo [tag] text (username)` - same as above
`/todo [tag] {item 1} {item 2}` - adds item 1 and item 2 as separate todo
                                  items in [tag] list
`/todo #channel [tag]` - posts all todo items in the [tag] list to that channel
`/todo clear` - removes all of your personal todo items
`/todo remove number` - removes todo item with the specified number'''
