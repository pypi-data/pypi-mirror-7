import os

import bcdoc.docevents
from botocore.compat import OrderedDict

import awscli
from awscli.clidocs import CLIDocumentEventHandler
from awscli.argparser import ArgTableArgParser
from awscli.argprocess import unpack_argument
from awscli.clidriver import CLICommand
from awscli.arguments import CustomArgument
from awscli.help import HelpCommand


class _FromFile(object):
    def __init__(self, *paths):
        self.filename = None
        if paths:
            self.filename = os.path.join(*paths)


class BasicCommand(CLICommand):
    """Basic top level command with no subcommands.

    If you want to create a new command, subclass this and
    provide the values documented below.

    """

    # This is the name of your command, so if you want to
    # create an 'aws mycommand ...' command, the NAME would be
    # 'mycommand'
    NAME = 'commandname'
    # This is the description that will be used for the 'help'
    # command.
    DESCRIPTION = 'describe the command'
    # This is optional, if you are fine with the default synopsis
    # (the way all the built in operations are documented) then you
    # can leave this empty.
    SYNOPSIS = ''
    # If you want to provide some hand written examples, you can do
    # so here.  This is written in RST format.  This is optional,
    # you don't have to provide any examples, though highly encouraged!
    EXAMPLES = ''
    # If your command has arguments, you can specify them here.  This is
    # somewhat of an implementation detail, but this is a list of dicts
    # where the dicts match the kwargs of the CustomArgument's __init__.
    # For example, if I want to add a '--argument-one' and an
    # '--argument-two' command, I'd say:
    #
    # ARG_TABLE = [
    #     {'name': 'argument-one', 'help_text': 'This argument does foo bar.',
    #      'action': 'store', 'required': False, 'cli_type_name': 'string',},
    #     {'name': 'argument-two', 'help_text': 'This argument does some other thing.',
    #      'action': 'store', 'choices': ['a', 'b', 'c']},
    # ]
    ARG_TABLE = []
    # If you want the command to have subcommands, you can provide a list of
    # dicts.  We use a list here because we want to allow a user to provide
    # the order they want to use for subcommands.
    # SUBCOMMANDS = [
    #     {'name': 'subcommand1', 'command_class': SubcommandClass},
    #     {'name': 'subcommand2', 'command_class': SubcommandClass2},
    # ]
    # The command_class must subclass from ``BasicCommand``.
    SUBCOMMANDS = []

    FROM_FILE = _FromFile
    # You can set the DESCRIPTION, SYNOPSIS, and EXAMPLES to FROM_FILE
    # and we'll automatically read in that data from the file.
    # This is useful if you have a lot of content and would prefer to keep
    # the docs out of the class definition.  For example:
    #
    # DESCRIPTION = FROM_FILE
    #
    # will set the DESCRIPTION value to the contents of
    # awscli/examples/<command name>/_description.rst
    # The naming conventions for these attributes are:
    #
    # DESCRIPTION = awscli/examples/<command name>/_description.rst
    # SYNOPSIS = awscli/examples/<command name>/_synopsis.rst
    # EXAMPLES = awscli/examples/<command name>/_examples.rst
    #
    # You can also provide a relative path and we'll load the file
    # from the specified location:
    #
    # DESCRIPTION = awscli/examples/<filename>
    #
    # For example:
    #
    # DESCRIPTION = FROM_FILE('command, 'subcommand, '_description.rst')
    # DESCRIPTION = 'awscli/examples/command/subcommand/_description.rst'
    #

    # At this point, the only other thing you have to implement is a _run_main
    # method (see the method for more information).

    def __init__(self, session):
        self._session = session

    def __call__(self, args, parsed_globals):
        # args is the remaining unparsed args.
        # We might be able to parse these args so we need to create
        # an arg parser and parse them.
        subcommand_table = self._build_subcommand_table()
        arg_table = self.arg_table
        parser = ArgTableArgParser(arg_table, subcommand_table)
        parsed_args, remaining = parser.parse_known_args(args)

        # Unpack arguments
        for key, value in vars(parsed_args).items():
            param = None
            if key in arg_table:
                param = arg_table[key]

            setattr(parsed_args, key, unpack_argument(
                self._session,
                'custom',
                self.name,
                param,
                value
            ))

        if hasattr(parsed_args, 'help'):
            self._display_help(parsed_args, parsed_globals)
        elif getattr(parsed_args, 'subcommand', None) is None:
            # No subcommand was specified so call the main
            # function for this top level command.
            return self._run_main(parsed_args, parsed_globals)
        else:
            return subcommand_table[parsed_args.subcommand](remaining, parsed_globals)

    def _run_main(self, parsed_args, parsed_globals):
        # Subclasses should implement this method.
        # parsed_globals are the parsed global args (things like region,
        # profile, output, etc.)
        # parsed_args are any arguments you've defined in your ARG_TABLE
        # that are parsed.  These will come through as whatever you've
        # provided as the 'dest' key.  Otherwise they default to the
        # 'name' key.  For example: ARG_TABLE[0] = {"name": "foo-arg", ...}
        # can be accessed by ``parsed_args.foo_arg``.
        raise NotImplementedError("_run_main")

    def _build_subcommand_table(self):
        subcommand_table = OrderedDict()
        for subcommand in self.SUBCOMMANDS:
            subcommand_name = subcommand['name']
            subcommand_class = subcommand['command_class']
            subcommand_table[subcommand_name] = subcommand_class(self._session)
        self._session.emit('building-command-table.%s' % self.NAME,
                           command_table=subcommand_table,
                           session=self._session)
        return subcommand_table

    def _display_help(self, parsed_args, parsed_globals):
        help_command = self.create_help_command()
        help_command(parsed_args, parsed_globals)

    def create_help_command(self):
        return BasicHelp(self._session, self, command_table={},
                         arg_table=self.arg_table)

    @property
    def arg_table(self):
        arg_table = OrderedDict()
        for arg_data in self.ARG_TABLE:
            custom_argument = CustomArgument(**arg_data)
            arg_table[arg_data['name']] = custom_argument
        return arg_table

    @classmethod
    def add_command(cls, command_table, session, **kwargs):
        command_table[cls.NAME] = cls(session)

    @property
    def name(self):
        return self.NAME


class BasicHelp(HelpCommand):
    event_class = 'command'

    def __init__(self, session, command_object, command_table, arg_table,
                 event_handler_class=None):
        super(BasicHelp, self).__init__(session, command_object,
                                        command_table, arg_table)
        # This is defined in HelpCommand so we're matching the
        # casing here.
        if event_handler_class is None:
            event_handler_class=BasicDocHandler
        self.EventHandlerClass = event_handler_class

        # These are public attributes that are mapped from the command
        # object.  These are used by the BasicDocHandler below.
        self._description = command_object.DESCRIPTION
        self._synopsis = command_object.SYNOPSIS
        self._examples = command_object.EXAMPLES

    @property
    def name(self):
        return self.obj.NAME

    @property
    def description(self):
        return self._get_doc_contents('_description')

    @property
    def synopsis(self):
        return self._get_doc_contents('_synopsis')

    @property
    def examples(self):
        return self._get_doc_contents('_examples')

    def _get_doc_contents(self, attr_name):
        value = getattr(self, attr_name)
        if isinstance(value, BasicCommand.FROM_FILE):
            if value.filename is not None:
                trailing_path = value.filename
            else:
                trailing_path = os.path.join(self.name, attr_name + '.rst')
            doc_path = os.path.join(
                os.path.abspath(os.path.dirname(awscli.__file__)), 'examples',
                trailing_path)
            with open(doc_path) as f:
                return f.read()
        else:
            return value

    def __call__(self, args, parsed_globals):
        # Create an event handler for a Provider Document
        instance = self.EventHandlerClass(self)
        # Now generate all of the events for a Provider document.
        # We pass ourselves along so that we can, in turn, get passed
        # to all event handlers.
        bcdoc.docevents.generate_events(self.session, self)
        self.renderer.render(self.doc.getvalue())
        instance.unregister()


class BasicDocHandler(CLIDocumentEventHandler):
    def __init__(self, help_command):
        super(BasicDocHandler, self).__init__(help_command)
        self.doc = help_command.doc

    def doc_description(self, help_command, **kwargs):
        self.doc.style.h2('Description')
        self.doc.write(help_command.description)
        self.doc.style.new_paragraph()

    def doc_synopsis_start(self, help_command, **kwargs):
        if not help_command.synopsis:
            super(BasicDocHandler, self).doc_synopsis_start(
                help_command=help_command, **kwargs)
        else:
            self.doc.style.h2('Synopsis')
            self.doc.style.start_codeblock()
            self.doc.writeln(help_command.synopsis)

    def doc_synopsis_option(self, arg_name, help_command, **kwargs):
        if not help_command.synopsis:
            super(BasicDocHandler, self).doc_synopsis_option(
                arg_name=arg_name,
                help_command=help_command, **kwargs)
        else:
            # A synopsis has been provided so we don't need to write
            # anything here.
            pass

    def doc_synopsis_end(self, help_command, **kwargs):
        if not help_command.synopsis:
            super(BasicDocHandler, self).doc_synopsis_end(
                help_command=help_command, **kwargs)
        else:
            self.doc.style.end_codeblock()

    def doc_option_example(self, arg_name, help_command, **kwargs):
        pass

    def doc_examples(self, help_command, **kwargs):
        if help_command.examples:
            self.doc.style.h2('Examples')
            self.doc.write(help_command.examples)

    def doc_subitems_start(self, help_command, **kwargs):
        pass

    def doc_subitem(self, command_name, help_command, **kwargs):
        pass

    def doc_subitems_end(self, help_command, **kwargs):
        pass
