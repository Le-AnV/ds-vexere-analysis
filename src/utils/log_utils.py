from datetime import datetime
import traceback


def log(msg: str):

    print(f"[{datetime.now():%H:%M:%S}] {msg}")


def log_exception(func_name: str, e: Exception):
    """In ra lỗi kèm tên hàm và dòng xảy ra."""
    tb = traceback.extract_tb(e.__traceback__)
    last_call = tb[-1]
    line_no = last_call.lineno
    file_name = last_call.filename
    log(f"ERROR in {func_name} ({file_name}:{line_no}) - {type(e).__name__}: {e}")
