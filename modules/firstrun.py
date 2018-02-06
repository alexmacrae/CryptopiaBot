import subprocess
import os

class FirstRun:

    def __init__(self):

        self.crypto_dir = '/root/CryptopiaBot/www'
        self.var_dir = '/var'
        self.apache_dir = self.var_dir + '/www'
        self.web_dirs_moved = False

        print 'Checking webserver dirs...'

        if os.path.isdir(self.apache_dir) and os.path.isdir(self.crypto_dir):
            print 'CryptopiaBot website files haven\'t been moved, and default Apache dir still exists...'
            self.web_dirs_moved = False
        else:
            print 'Everything is fine :)'
            self.web_dirs_moved = True

    def go(self):

        if self.web_dirs_moved == False:
            print 'Removing default Apache www/ dir...'
            subprocess.call(['rm', '-r', self.apache_dir])
            print 'Replacing with the www/ dir in /root/CryptopiaBot'
            subprocess.call(['mv', '-f', self.crypto_dir, self.var_dir])
            self.web_dirs_moved = True

if __name__ == '__main__':

    fr = FirstRun().go()
