import sys, traceback

def hataKodGoster(err=""):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    if exc_type == None and exc_obj == None and exc_tb == None:
        return
    # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    fname = exc_tb.tb_frame.f_code.co_filename
    hataStr = "%s %s %s %s\nTraceback: %s" % (str(err), exc_type, fname, exc_tb.tb_lineno, traceback.format_exc())
    print(hataStr)