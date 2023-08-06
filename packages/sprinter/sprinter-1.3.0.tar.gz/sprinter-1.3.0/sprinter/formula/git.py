"""
Creates a git repository and places it at the install location.

[sub]
formula = sprinter.formula.git
url = https://github.com/toumorokoshi/sub.git
branch = toumorokoshi
rc = . %(sub:root_dir)s/libexec/sub-init
"""
from __future__ import unicode_literals
import logging
import os

from sprinter.formula.base import FormulaBase
import sprinter.lib as lib


class GitException(Exception):
    pass


class GitFormula(FormulaBase):
    """ A sprinter formula for git"""

    required_options = FormulaBase.required_options + ['url']
    valid_options = FormulaBase.valid_options + ['branch']

    def install(self):
        if not lib.which('git'):
            self.logger.warn("git is not installed! Please install git to install this feature.")
            return
        self.__clone_repo(self.target.get('url'),
                          self.directory.install_directory(self.feature_name),
                          branch=self.target.get('branch', 'master'))
        FormulaBase.install(self)

    def update(self):
        if not lib.which('git'):
            self.logger.warn("git is not installed! Please install git to install this feature.")
            return
        target_directory = self.directory.install_directory(self.feature_name)
        source_branch = self.source.get('branch', 'master')
        target_branch = self.target.get('branch', 'master')

        if not os.path.exists(target_directory):
            # directory doesn't exist, so we just clone again
            self.logger.debug("No repository cloned. Re-cloning...")
            self.__clone_repo(self.target.get('url'),
                              target_directory,
                              branch=target_branch)

        if self.target.get('url') != self.source.get('url'):

            self.logger.debug("Old git repository Found. Deleting...")
            self.directory.remove_feature(self.feature_name)
            self.__clone_repo(self.target.get('url'),
                              target_directory,
                              branch=self.target.get('branch', 'master'))

        elif source_branch != target_branch:
            self.__checkout_branch(target_directory, target_branch)

        else:
            if not os.path.exists(target_directory):
                self.logger.debug("No repository cloned. Re-cloning...")
                self.__clone_repo(self.target.get('url'),
                                  target_directory,
                                  branch=target_branch)
            self.__fetch_merge_repo(target_directory, target_branch)

        FormulaBase.update(self)

    def __checkout_branch(self, target_directory, branch):
        self.logger.debug("Checking out branch %s..." % branch)
        for command in ("git fetch origin {0}".format(branch),
                        "git checkout {0}".format(branch)):
            error, output = lib.call(
                command,
                output_log_level=logging.DEBUG,
                cwd=target_directory
            )
            if error:
                self.logger.info(output)
                raise GitException("An error occurred when checking out a branch!")

    def __clone_repo(self, repo_url, target_directory, branch):
        self.logger.debug("Cloning repository %s into %s..." % (repo_url, target_directory))
        error, output = lib.call("git clone %s %s" % (repo_url, target_directory),
                                 output_log_level=logging.DEBUG)
        if error:
            self.logger.info(output)
            raise GitException("An error occurred when cloning!")
        if branch != "master":
            self.__checkout_branch(target_directory, branch)

    def __fetch_merge_repo(self, target_directory, target_branch):
        self.logger.debug("Fetching branch %s..." % target_branch)
        os.chdir(target_directory)

        error, output = lib.call("git fetch origin %s" % target_branch,
                                 output_log_level=logging.DEBUG)
        if error:
            self.logger.info(output)
            raise GitException("An error occurred while fetching!")

        self.logger.info(output)
        self.logger.debug("Merging branch %s..." % target_branch)
        error, output = lib.call("git merge --ff-only origin %s" % target_branch,
                                     output_log_level=logging.DEBUG)
        if error:
            #do not want to raise exception on merge failures/conflicts
            self.logger.warning(output)
        else:
            self.logger.info(output)
