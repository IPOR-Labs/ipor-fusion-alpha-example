import time

import schedule

from alpha_bot import AlphaBot
from logging_config import LoggingConfig


class Scheduler:

    def __init__(self, fusion_alpha_bot: AlphaBot, interval: int):
        self.fusion_alpha_bot = fusion_alpha_bot
        self.interval = interval
        self.logger = LoggingConfig.get_logger("Scheduler")

    def schedule(self):
        self.logger.info("Script starting with scheduler")

        # Schedule the main task to run every minute
        schedule.every(self.interval).seconds.do(self.fusion_alpha_bot.do_fusion)

        # Run the task immediately once at startup
        self.logger.info("Running the task immediately for the first time")
        self.fusion_alpha_bot.do_fusion()

        # Keep the script running and execute scheduled tasks
        while True:
            schedule.run_pending()
            time.sleep(1)
