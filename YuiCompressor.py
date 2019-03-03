import os
import sys
import sublime
import sublime_plugin

class YuiCompressorCommand(sublime_plugin.TextCommand):
    def run(self, edit):

        view = self.view

        import subprocess
        import re
        from os.path import join

        platform = sublime.platform()
        settings = sublime.load_settings('YuiCompressor.sublime-settings')
        opts = settings.get('yui_options')
        efile = view.file_name()
        ftype = os.path.splitext(efile)[-1][1:] # csak a kiterjesztes, ezt adom at a yui compresszornak

        package_path = join(sublime.packages_path(), "YuiCompressor")

        yui_path = package_path+"\\bin\\YuiConsole.exe"
        sys.stdout.write(yui_path + '\n')


        if (not(os.path.isfile(yui_path) and os.access(yui_path, os.R_OK))):
            if ('yui_path' in opts and opts['yui_path']):
                yui_path = opts['yui_path']

        cmd = []
        cmd.append(str(yui_path))
        cmd.append('--type=' + ftype)
        cmd.append('-')

        file_text = sublime.Region(0, view.size())
        file_text_utf = view.substr(file_text).encode('utf-8')
        if (len(file_text_utf) == 0):
            return

        try:
            if (platform == 'windows'):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                p = subprocess.Popen(
                    cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, startupinfo=startupinfo,
                    shell=False, creationflags=subprocess.SW_HIDE)
                stdout, stderr = p.communicate(file_text_utf)

        except Exception as e:
            stderr = str(e)

        if len(stderr) == 0 and len(stdout) > 0:
            szoveg = stdout.decode("UTF-8","ignore")
            sys.stdout.write(str(re.search("^\w+ = Line:[0-9]+, Col:[0-9]+$", szoveg.strip())))
            if (re.search("^[a-zA-Z0-9_ .-]+ = Line:[0-9]+, Col:[0-9]+$", szoveg.strip())):
                show_error("I'm sorry, but something is wrong!\nYui Compressor say's:\n"+szoveg.strip())
                return

            if (os.path.isfile(efile) and os.access(efile, os.R_OK)):
                basefile = os.path.basename(efile) #eredeti file nev dir nelkul
                dirname = os.path.dirname(efile) # csak dirname
                bfile = os.path.splitext(basefile)[0] # csak a fajlnev kiterjesztes nelkul
                ext = os.path.splitext(basefile)[-1] # csak a kiterjesztes
                cpedfname = bfile+"-min"+ext #uj fajlnev dir nelkul
                cpedfile = dirname+"\\"+cpedfname # uj fajl teljes elers

                with open(os.path.join(dirname, cpedfname), 'wb') as f:
                    f.write(bytes(szoveg.strip(),"UTF-8"))

                window = sublime.active_window()
                if(opts['yui_open_file_after_save']):
                    window.open_file(cpedfname, sublime.ENCODED_POSITION)

                sublime.message_dialog("Success!\n\nMinimized file has been saved:\n"+cpedfile)
        else:
            show_error('Compress error:\n' + str(stderr))

def show_error(text):
    sublime.error_message(u'YuiCompressor\n\n%s' % text)

