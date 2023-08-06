from IPython.kernel.zmq.kernelbase import Kernel
from IPython.core.oinspect import Inspector, cast_unicode
from oct2py import octave, Oct2PyError

import os
import signal
from subprocess import check_output
import re

__version__ = '0.1'

version_pat = re.compile(r'version (\d+(\.\d+)+)')


class OctaveKernel(Kernel):
    implementation = 'octave_kernel'
    implementation_version = __version__
    language = 'octave'

    @property
    def language_version(self):
        m = version_pat.search(self.banner)
        return m.group(1)

    _banner = None

    @property
    def banner(self):
        if self._banner is None:
            self._banner = check_output(['octave',
                                         '--version']).decode('utf-8')
        return self._banner

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        # Signal handlers are inherited by forked processes,
        # and we can't easily reset it from the subprocess.
        # Since kernelapp ignores SIGINT except in message handlers,
        # we need to temporarily reset the SIGINT handler here
        # so that octave and its children are interruptible.
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            self.octavewrapper = octave
        finally:
            signal.signal(signal.SIGINT, sig)

        self.inspector = Inspector()
        self.inspector.set_active_scheme("Linux")

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        code = code.strip()
        abort_msg = {'status': 'abort',
                     'execution_count': self.execution_count}

        if not code or code == 'keyboard' or code.startswith('keyboard('):
            return {'status': 'ok', 'execution_count': self.execution_count,
                    'payload': [], 'user_expressions': {}}

        elif (code == 'exit' or code.startswith('exit(')
                or code == 'quit' or code.startswith('quit(')):
            # TODO: exit gracefully here
            self.do_shutdown(False)
            return abort_msg

        elif code == 'restart':
            self.octavewrapper.restart()
            return abort_msg

        elif code.endswith('?') or code.startswith('?'):
            self._get_help(code)
            return abort_msg

        interrupted = False
        try:
            output = self.octavewrapper._eval([code])

        except KeyboardInterrupt:
            self.octavewrapper._session.proc.send_signal(signal.SIGINT)
            interrupted = True
            output = 'Octave Session Interrupted'

        except Oct2PyError as e:
            return self._handle_error(str(e))

        except Exception:
            self.octavewrapper.restart()
            output = 'Uncaught Exception, Restarting Octave'

        else:
            if output is None:
                output = ''
            elif output == 'Octave Session Interrupted':
                interrupted = True

        if not silent:
            stream_content = {'name': 'stdout', 'data': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        if interrupted:
            return abort_msg

        return {'status': 'ok', 'execution_count': self.execution_count,
                'payload': [], 'user_expressions': {}}

    def do_complete(self, code, cursor_pos):
        code = code[:cursor_pos]
        default = {'matches': [], 'cursor_start': 0,
                   'cursor_end': cursor_pos, 'metadata': dict(),
                   'status': 'ok'}

        if code[-1] == ' ':
            return default

        tokens = code.replace(';', ' ').split()
        if not tokens:
            return default
        token = tokens[-1]

        if os.sep in token:
            dname = os.path.dirname(token)
            rest = os.path.basename(token)
            if os.path.exists(dname):
                files = os.listdir(dname)
                matches = [f for f in files if f.startswith(rest)]
                start = cursor_pos - len(rest)
            else:
                return default
        else:
            start = cursor_pos - len(token)
            cmd = 'completion_matches("%s")' % token
            output = self.octavewrapper._eval([cmd])
            matches = output.split()

            for item in dir(self.octavewrapper):
                if item.startswith(token) and not item in matches:
                    matches.append(item)

        return {'matches': matches, 'cursor_start': start,
                'cursor_end': cursor_pos, 'metadata': dict(),
                'status': 'ok'}

    def do_inspect(self, code, cursor_pos, detail_level=0):
        data = dict()
        if (not code or not len(code) >= cursor_pos or
                not code[cursor_pos - 1] == '('):
            return {'status': 'ok', 'data': data, 'metadata': dict()}

        else:
            token = code[:cursor_pos - 1].replace(';', '').split()[-1]
            docstring = self._get_octave_info(token, detail_level)['docstring']
            if docstring:
                data = {'text/plain': docstring}
            return {'status': 'ok', 'data': data, 'metadata': dict()}

    def do_shutdown(self, restart):
        if restart:
            self.octavewrapper.restart()
        else:
            self.octavewrapper.close()
        return Kernel.do_shutdown(self, restart)

    def _get_help(self, code):
        if code.startswith('??') or code.endswith('??'):
            detail_level = 1
        else:
            detail_level = 0

        code = code.replace('?', '')
        info = self._get_octave_info(code, detail_level)
        output = self._get_printable_info(info, detail_level)
        stream_content = {'name': 'stdout', 'data': output}
        self.send_response(self.iopub_socket, 'stream', stream_content)

    def _handle_error(self, err):
        if 'parse error:' in err:
            err = 'Parse Error'

        elif 'Octave returned:' in err:
            err = err[err.index('Octave returned:'):]
            err = err[len('Octave returned:'):].lstrip()

        elif 'Syntax Error' in err:
            err = 'Syntax Error'

        stream_content = {'name': 'stdout', 'data': err.strip()}
        self.send_response(self.iopub_socket, 'stream', stream_content)

        return {'status': 'error', 'execution_count': self.execution_count,
                'ename': '', 'evalue': err, 'traceback': []}

    def _get_printable_info(self, info, detail_level=0):
        inspector = self.inspector
        displayfields = []

        def add_fields(fields):
            for title, key in fields:
                field = info[key]
                if field is not None:
                    displayfields.append((title, field.rstrip()))

        add_fields(inspector.pinfo_fields1)
        add_fields(inspector.pinfo_fields2)
        add_fields(inspector.pinfo_fields3)

        # Source or docstring, depending on detail level and whether
        # source found.
        if detail_level > 0 and info['source'] is not None:
            source = cast_unicode(info['source'])
            displayfields.append(("Source",  source))

        elif info['docstring'] is not None:
            displayfields.append(("Docstring", info["docstring"]))

        # Info for objects:
        else:
            add_fields(inspector.pinfo_fields_obj)

        # Finally send to printer/pager:
        if displayfields:
            return inspector._format_fields(displayfields)

    def _get_octave_info(self, obj, detail_level):
        info_obj = dict(argspec=None, base_class=None, call_def=None,
                        call_docstring=None, class_docstring=None,
                        definition=None,
                        docstring=None, file=None, found=False,
                        init_definition=None, init_docstring=None, isalias=0,
                        isclass=None,  ismagic=0, length=None, name='',
                        namespace=None, source=None, string_form=None,
                        type_name='')

        oc = self.octavewrapper

        if obj in dir(oc):
            obj = getattr(oc, obj)
            return self.inspector.info(obj, detail_level=detail_level)

        exist = oc.run('exist "%s"' % obj)
        if exist.endswith('0'):
            return info_obj

        try:
            help_str = oc.run('help %s' % obj)
        except Oct2PyError:
            help_str = None
        type_str = oc.type(obj)[0].strip()
        cls_str = oc.run("class %s" % obj)[6:]

        type_first_line = type_str.splitlines()[0]
        type_str = '\n'.join(type_str.splitlines()[1:])
        is_var = 'is a variable' in type_first_line

        info_obj['found'] = True
        info_obj['docstring'] = help_str or type_first_line
        info_obj['type_name'] = cls_str if is_var else 'built-in function'
        info_obj['source'] = help_str
        info_obj['string_form'] = obj if not is_var else type_str.rstrip()

        if type_first_line.rstrip().endswith('.m'):
            info_obj['file'] = type_first_line.split()[-1]
            info_obj['type_name'] = 'function'
            info_obj['source'] = type_str
            if not help_str:
                info_obj['docstring'] = None

        return info_obj

if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=OctaveKernel)
