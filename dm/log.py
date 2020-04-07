import logging
import os
import shutil

log_file_formatter = logging.Formatter(
    '%(asctime)s [%(levelname).1s] %(message)s\t(at %(filename)s:%(lineno)s) ')
log_stream_formatter = logging.Formatter('%(message)s')


# Create root logger
def create_root_logger():
    root_log_path = './logs'
    if not os.path.exists(root_log_path):
        os.makedirs(root_log_path)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    debug_file_handler = logging.FileHandler(
        os.path.realpath(os.path.join(root_log_path, 'DEBUG.log')))
    debug_file_handler.setFormatter(log_file_formatter)
    debug_file_handler.setLevel(logging.DEBUG)

    info_file_handler = logging.FileHandler(
        os.path.realpath(os.path.join(root_log_path, 'INFO.log')))
    info_file_handler.setFormatter(log_file_formatter)
    info_file_handler.setLevel(logging.INFO)

    error_file_handler = logging.FileHandler(
        os.path.realpath(os.path.join(root_log_path, 'ERROR.log')))
    error_file_handler.setFormatter(log_file_formatter)
    error_file_handler.setLevel(logging.ERROR)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_stream_formatter)
    stream_handler.setLevel(logging.DEBUG)

    root_logger.addHandler(debug_file_handler)
    root_logger.addHandler(info_file_handler)
    root_logger.addHandler(error_file_handler)
    root_logger.addHandler(stream_handler)


def add_outputpath_log_handler(output_path, logger):
    root_log_path = os.path.join(output_path, 'logs')
    if os.path.exists(root_log_path):
        shutil.rmtree(root_log_path)
    os.makedirs(root_log_path)

    debug_file_handler = logging.FileHandler(
        os.path.realpath(os.path.join(root_log_path, 'DEBUG.log')))
    debug_file_handler.setFormatter(log_file_formatter)
    debug_file_handler.setLevel(logging.DEBUG)

    info_file_handler = logging.FileHandler(
        os.path.realpath(os.path.join(root_log_path, 'INFO.log')))
    info_file_handler.setFormatter(log_file_formatter)
    info_file_handler.setLevel(logging.INFO)

    error_file_handler = logging.FileHandler(
        os.path.realpath(os.path.join(root_log_path, 'ERROR.log')))
    error_file_handler.setFormatter(log_file_formatter)
    error_file_handler.setLevel(logging.ERROR)

    logger.addHandler(debug_file_handler)
    logger.addHandler(info_file_handler)
    logger.addHandler(error_file_handler)
