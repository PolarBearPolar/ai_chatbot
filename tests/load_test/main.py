import argparse
import constants
from load_test import testApplicationLoad
from logger import setupLogger, stopLogger

logger = setupLogger(__name__)

# TO-DO:
# fix post request error

def main():
    parser = argparse.ArgumentParser(description="Testing command arguments.")
    parser.add_argument(
        "--user-num",
        action="store",
        help="Number of users to simulate simultaneous app usage.",
        type=int,
        required=True    
    )
    parser.add_argument(
        "--enable-rag",
        action="store_true",
        help="Enable RAG when generating answers."
    )
    parser.add_argument(
        "--enable-multiple-queries-per-chat",
        action="store_true",
        help="Enable multiple queries in a single chat, not one query per one chat."
    )
    parser.add_argument(
        "--output-filename",
        action="store",
        help="User-specified output file name.",
        default=constants.DEFAULT_OUTPUT_FILENAME
    )
    parser.add_argument(
        "--output-file-write-mode",
        action="store",
        help="User-specified output file write mode ('w' - rewrite, 'a' - append).",
        default=constants.DEFAULT_OUTPUT_FILE_WRITE_MODE
    )
    args = parser.parse_args()
    logger.info(f"TESTING PARAMETERS:\n\tuser number: {args.user_num}\n\trag enabled: {args.enable_rag}\n\tmultiple queries per chat: {args.enable_multiple_queries_per_chat}\n\toutput file: {args.output_filename} (mode={args.output_file_write_mode})")
    testApplicationLoad(
        args.user_num,
        args.enable_rag,
        args.enable_multiple_queries_per_chat,
        args.output_filename,
        args.output_file_write_mode
    )

if __name__ == '__main__':
    try:
        main()
    finally:
        stopLogger()