import logging
import os

def setup_logging(log_file, level=logging.DEBUG):
  if not os.path.exists('logs'):
    os.makedirs('logs')

  log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  logging.basicConfig(
    filename=f'logs/{log_file}', 
    filemode='a', 
    format=log_format, 
    level=level
  )
        
  console_handler = logging.StreamHandler()
  console_handler.setFormatter(logging.Formatter(log_format))
  logging.getLogger('').addHandler(console_handler)
