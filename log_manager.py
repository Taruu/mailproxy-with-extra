import logging


class LogManager:
    def __init__(self,
                level: int=logging.DEBUG,
                formatter: str=None,
                filename: str="log.log",
                filemode: str="a"
                ):
        self.level = level
        self.formatter = formatter
        self.filename = filename
        self.filemode = filemode
        
        # Configure the root logger with our default settings
        logging.basicConfig(level=self.level, format=self.formatter, filename=self.filename, filemode=self.filemode)
        
        # Add file handler if filename is provided
        if self.filename:
            file_handler = logging.FileHandler(self.filename)
            logging.root.addHandler(file_handler)
        
        # Add file handler if filename and filemode is provided
        if self.filename and self.filemode:
            file_handler = logging.FileHandler(self.filename, self.filemode)
            logging.root.addHandler(file_handler)
        
        # Update all existing handlers with the new formatter
        for handler in logging.root.handlers:
            handler.setFormatter(self.formatter or logging.Formatter())

    def set_level(self, level):
        self.level = level
        logging.root.setLevel(self.level)

    def set_formatter(self, formatter):
        self.formatter = formatter

        # Update all existing handlers with the new formatter
        for handler in logging.root.handlers:
            handler.setFormatter(self.formatter or logging.Formatter())

    def set_file_handler(self, filename=None, filemode='a'):
        self.filename = filename
        self.filemode = filemode

        # Add file handler
        file_handler = logging.FileHandler(self.filename, filemode=self.filemode)
        file_handler.setFormatter(self.formatter or logging.Formatter())
        logging.root.addHandler(file_handler)
