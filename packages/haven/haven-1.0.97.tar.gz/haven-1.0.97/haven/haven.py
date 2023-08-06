# -*- coding: utf-8 -*-

from multiprocessing import Process
from threading import Lock
import time
import signal
from .callbacks_mixin import AppCallBacksMixin
from . import autoreload
from .log import logger


class Haven(AppCallBacksMixin):
    debug = False
    got_first_request = False
    got_first_request_lock = None
    blueprints = None

    def __init__(self):
        super(Haven, self).__init__()
        self.got_first_request_lock = Lock()
        self.blueprints = list()

    def register_blueprint(self, blueprint):
        blueprint.register2app(self)

    def run(self, host, port, debug=None, use_reloader=None, workers=None):
        if debug is not None:
            self.debug = debug

        use_reloader = use_reloader if use_reloader is not None else self.debug

        def run_wrapper():
            logger.info('Running server on %s:%s, debug: %s, use_reloader: %s',
                        host, port, self.debug, use_reloader)
            self._start_repeat_timers()

            self._prepare_server(host, port)
            if workers is not None:
                if not use_reloader:
                    # 因为只能在主线程里面设置signals
                    self._handle_parent_proc_signals()

                proc_list = []
                for it in xrange(0, workers):
                    p = Process(target=self._try_serve_forever, args=(False,))
                    # 当前进程_daemonic默认是False，改成True将启动不了子进程
                    # 但是子进程要设置_daemonic为True，这样父进程退出，子进程会被强制关闭
                    p.daemon = True
                    p.start()
                    proc_list.append(p)

                while True:
                    if not filter(lambda x: x, proc_list):
                        # 子进程已经全死了
                        break

                    for idx, it in enumerate(proc_list):
                        if it and not it.is_alive():
                            logger.error('process[%s] dead.', it.pid)
                            proc_list[idx] = None

                    try:
                        time.sleep(1)
                    except KeyboardInterrupt:
                        break
                    except:
                        logger.error('exc occur.', exc_info=True)
                        break
            else:
                self._try_serve_forever(True)

        if use_reloader:
            autoreload.main(run_wrapper)
        else:
            run_wrapper()

    def repeat_timer(self, interval):
        raise NotImplementedError

    def _try_serve_forever(self, main_process):
        if not main_process:
            self._handle_child_proc_signals()

        try:
            self._serve_forever()
        except KeyboardInterrupt:
            pass
        except:
            logger.error('exc occur.', exc_info=True)

    def _handle_parent_proc_signals(self):
        try:
            # 修改SIGTERM，否则父进程被term，子进程不会自动退出；明明子进程都设置为daemon了的
            signal.signal(signal.SIGTERM, signal.default_int_handler)
            # 即使对于SIGINT，SIG_DFL和default_int_handler也是不一样的，要是想要抛出KeyboardInterrupt，应该用default_int_handler
            signal.signal(signal.SIGINT, signal.default_int_handler)
        except Exception, e:
            logger.error('handle_signals fail. e: %s', e)

    def _handle_child_proc_signals(self):
        try:
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            signal.signal(signal.SIGINT, signal.SIG_IGN)
        except Exception, e:
            logger.error('handle_signals fail. e: %s', e)

    def _start_repeat_timers(self):
        self.events.repeat_timer()
        for bp in self.blueprints:
            bp.events.repeat_app_timer()

    def _prepare_server(self, host, port):
        raise NotImplementedError

    def _serve_forever(self):
        raise NotImplementedError
