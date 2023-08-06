# -*- coding: utf-8 -*-
# initializers.py
# Copyright (C) 2013 LEAP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Platform-dependant initialization code.
"""
import logging
import os
import platform
import stat
import sys
import subprocess
import tempfile

from PySide import QtGui

from leap.bitmask.config.leapsettings import LeapSettings
from leap.bitmask.services.eip import get_vpn_launcher
from leap.bitmask.services.eip.linuxvpnlauncher import LinuxVPNLauncher
from leap.bitmask.services.eip.darwinvpnlauncher import DarwinVPNLauncher
from leap.bitmask.util import first


logger = logging.getLogger(__name__)

# NOTE we could use a deferToThread here, but should
# be aware of this bug: http://www.themacaque.com/?p=1067

__all__ = ["init_platform"]

_system = platform.system()


def init_platform():
    """
    Return the right initializer for the platform we are running in, or
    None if no proper initializer is found
    """
    initializer = None
    try:
        initializer = globals()[_system + "Initializer"]
    except:
        pass
    if initializer:
        logger.debug("Running initializer for %s" % (platform.system(),))
        initializer()
    else:
        logger.debug("Initializer not found for %s" % (platform.system(),))


#
# common utils
#

NOTFOUND_MSG = ("Tried to install %s, but %s "
                "not found inside this bundle.")
BADEXEC_MSG = ("Tried to install %s, but %s "
               "failed to %s.")

UPDOWN_NOTFOUND_MSG = NOTFOUND_MSG % (
    "updown scripts", "those were")
UPDOWN_BADEXEC_MSG = BADEXEC_MSG % (
    "updown scripts", "they", "be copied")


def get_missing_updown_dialog():
    """
    Create a dialog for notifying of missing updown scripts.
    Returns that dialog.

    :rtype: QtGui.QMessageBox instance
    """
    WE_NEED_POWERS = ("To better protect your privacy, "
                      "Bitmask needs administrative privileges "
                      "to install helper files. "
                      "Do you want to proceed?")
    msg = QtGui.QMessageBox()
    msg.setWindowTitle(msg.tr("Missing up/down scripts"))
    msg.setText(msg.tr(WE_NEED_POWERS))
    # but maybe the user really deserve to know more
    #msg.setInformativeText(msg.tr(BECAUSE))
    msg.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
    msg.addButton("No, don't ask again", QtGui.QMessageBox.RejectRole)
    msg.setDefaultButton(QtGui.QMessageBox.Yes)
    return msg


def check_missing():
    """
    Check for the need of installing missing scripts, and
    raises a dialog to ask user for permission to do it.
    """
    config = LeapSettings()
    alert_missing = config.get_alert_missing_scripts()

    launcher = get_vpn_launcher()
    missing_scripts = launcher.missing_updown_scripts
    missing_other = launcher.missing_other_files

    if alert_missing and (missing_scripts() or missing_other()):
        msg = get_missing_updown_dialog()
        ret = msg.exec_()

        if ret == QtGui.QMessageBox.Yes:
            install_missing_fun = globals().get(
                "_%s_install_missing_scripts" % (_system.lower(),),
                None)
            if not install_missing_fun:
                logger.warning(
                    "Installer not found for platform %s." % (_system,))
                return

            # XXX maybe move constants to fun
            ok = install_missing_fun(UPDOWN_BADEXEC_MSG, UPDOWN_NOTFOUND_MSG)
            if not ok:
                msg = QtGui.QMessageBox()
                msg.setWindowTitle(msg.tr("Problem installing files"))
                msg.setText(msg.tr('Some of the files could not be copied.'))
                msg.setIcon(QtGui.QMessageBox.Warning)
                msg.exec_()

        elif ret == QtGui.QMessageBox.No:
            logger.debug("Not installing missing scripts, "
                         "user decided to ignore our warning.")

        elif ret == QtGui.QMessageBox.Rejected:
            logger.debug(
                "Setting alert_missing_scripts to False, we will not "
                "ask again")
            config.set_alert_missing_scripts(False)
#
# windows initializers
#


def _windows_has_tap_device():
    """
    Loop over the windows registry trying to find if the tap0901 tap driver
    has been installed on this machine.
    """
    import _winreg as reg

    adapter_key = 'SYSTEM\CurrentControlSet\Control\Class' \
        '\{4D36E972-E325-11CE-BFC1-08002BE10318}'
    with reg.OpenKey(reg.HKEY_LOCAL_MACHINE, adapter_key) as adapters:
        try:
            for i in xrange(10000):
                key_name = reg.EnumKey(adapters, i)
                with reg.OpenKey(adapters, key_name) as adapter:
                    try:
                        component_id = reg.QueryValueEx(adapter,
                                                        'ComponentId')[0]
                        if component_id.startswith("tap0901"):
                            return True
                    except WindowsError:
                        pass
        except WindowsError:
            pass
    return False


def WindowsInitializer():
    """
    Raise a dialog in case that the windows tap driver has not been found
    in the registry, asking the user for permission to install the driver
    """
    if not _windows_has_tap_device():
        msg = QtGui.QMessageBox()
        msg.setWindowTitle(msg.tr("TAP Driver"))
        msg.setText(msg.tr("Bitmask needs to install the necessary drivers "
                           "for Encrypted Internet to work. Would you like to "
                           "proceed?"))
        msg.setInformativeText(msg.tr("Encrypted Internet uses VPN, which "
                                      "needs a TAP device installed and none "
                                      "has been found. This will ask for "
                                      "administrative privileges."))
        msg.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        msg.setDefaultButton(QtGui.QMessageBox.Yes)
        ret = msg.exec_()

        if ret == QtGui.QMessageBox.Yes:
            # XXX should do this only if executed inside bundle.
            # Let's assume it's the only way it's gonna be executed under win
            # by now.
            driver_path = os.path.join(os.getcwd(),
                                       "apps",
                                       "eip",
                                       "tap_driver")
            dev_installer = os.path.join(driver_path,
                                         "devcon.exe")
            if os.path.isfile(dev_installer) and \
                    stat.S_IXUSR & os.stat(dev_installer)[stat.ST_MODE] != 0:
                inf_path = os.path.join(driver_path,
                                        "OemWin2k.inf")
                cmd = [dev_installer, "install", inf_path, "tap0901"]
                ret = subprocess.call(cmd, stdout=subprocess.PIPE, shell=True)
            else:
                logger.error("Tried to install TAP driver, but the installer "
                             "is not found or not executable")

#
# Darwin initializer functions
#


def _darwin_has_tun_kext():
    """
    Return True only if we found a directory under the system kext folder
    containing a kext named tun.kext, AND we found a startup item named 'tun'
    """
    # XXX we should be smarter here and use kextstats output.

    has_kext = os.path.isdir("/Library/Extensions/tun.kext")
    has_startup = os.path.isdir("/Library/StartupItems/tun")
    has_tun_and_startup = has_kext and has_startup
    logger.debug(
        'platform initializer check: has tun_and_startup = %s' %
        (has_tun_and_startup,))
    return has_tun_and_startup


def _darwin_install_missing_scripts(badexec, notfound):
    """
    Try to install the missing up/down scripts.

    :param badexec: error for notifying execution error during command.
    :type badexec: str
    :param notfound: error for notifying missing path.
    :type notfound: str
    :returns: True if the files could be copied successfully.
    :rtype: bool
    """
    # We expect to execute this from some way of bundle, since
    # the up/down scripts should be put in place by the installer.
    success = False
    installer_path = os.path.join(
        os.getcwd(),
        "..",
        "Resources",
        "openvpn")
    launcher = DarwinVPNLauncher

    if os.path.isdir(installer_path):
        fd, tempscript = tempfile.mkstemp(prefix="leap_installer-")
        try:
            scriptlines = launcher.cmd_for_missing_scripts(installer_path)
            with os.fdopen(fd, 'w') as f:
                f.write(scriptlines)
            st = os.stat(tempscript)
            os.chmod(tempscript, st.st_mode | stat.S_IEXEC | stat.S_IXUSR |
                     stat.S_IXGRP | stat.S_IXOTH)

            cmd, args = launcher().get_cocoasudo_installmissing_cmd()
            args.append(tempscript)
            cmdline = " ".join([cmd] + args)
            ret = subprocess.call(
                cmdline, stdout=subprocess.PIPE,
                shell=True)
            success = ret == 0
            if not success:
                logger.error("Install missing scripts failed.")
        except Exception as exc:
            logger.error(badexec)
            logger.error("Error was: %r" % (exc,))
        finally:
            try:
                os.remove(tempscript)
            except OSError as exc:
                logger.error("%r" % (exc,))
    else:
        logger.error(notfound)
        logger.debug('path searched: %s' % (installer_path,))

    return success


def DarwinInitializer():
    """
    Raise a dialog in case that the osx tuntap driver has not been found
    in the registry, asking the user for permission to install the driver
    """
    # XXX split this function into several

    TUNTAP_NOTFOUND_MSG = NOTFOUND_MSG % (
        "tuntaposx kext", "the installer")
    TUNTAP_BADEXEC_MSG = BADEXEC_MSG % (
        "tuntaposx kext", "the installer", "be launched")

    # TODO DRY this with other cases, and
    # factor out to _should_install() function.
    # Leave the dialog as a more generic thing.

    if not _darwin_has_tun_kext():
        msg = QtGui.QMessageBox()
        msg.setWindowTitle(msg.tr("TUN Driver"))
        msg.setText(msg.tr("Bitmask needs to install the necessary drivers "
                           "for Encrypted Internet to work. Would you like to "
                           "proceed?"))
        msg.setInformativeText(msg.tr("Encrypted Internet uses VPN, which "
                                      "needs a kernel extension for a TUN "
                                      "device installed, and none "
                                      "has been found. This will ask for "
                                      "administrative privileges."))
        msg.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
        msg.setDefaultButton(QtGui.QMessageBox.Yes)
        ret = msg.exec_()

        if ret == QtGui.QMessageBox.Yes:
            installer_path = os.path.abspath(
                os.path.join(
                    os.getcwd(),
                    "..",
                    "Resources",
                    "tuntap-installer.app"))
            if os.path.isdir(installer_path):
                cmd = ["open '%s'" % (installer_path,)]
                try:
                    ret = subprocess.call(
                        cmd, stdout=subprocess.PIPE,
                        shell=True)
                except:
                    logger.error(TUNTAP_BADEXEC_MSG)
            else:
                logger.error(TUNTAP_NOTFOUND_MSG)

    # Second check, for missing scripts.
    check_missing()


#
# Linux initializers
#

def _get_missing_resolvconf_dialog():
    """
    Create a dialog for notifying about missing openresolv.

    :rtype: QtGui.QMessageBox instance
    """
    NO_RESOLVCONF = (
        "Could not find <b>resolvconf</b> installed in your system.\n"
        "Do you want to quit Bitmask now?")

    EXPLAIN = (
        "Encrypted Internet needs resolvconf installed to work properly.\n"
        "Please use your package manager to install it.\n")

    msg = QtGui.QMessageBox()
    msg.setWindowTitle(msg.tr("Missing resolvconf framework"))
    msg.setText(msg.tr(NO_RESOLVCONF))
    # but maybe the user really deserve to know more
    msg.setInformativeText(msg.tr(EXPLAIN))
    msg.setStandardButtons(QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
    msg.setDefaultButton(QtGui.QMessageBox.Yes)
    return msg


def _linux_check_resolvconf():
    """
    Raise a dialog warning about the lack of the resolvconf framework.
    """
    RESOLVCONF_PATH = "/sbin/resolvconf"
    missing = not os.path.isfile(RESOLVCONF_PATH)

    if missing:
        msg = _get_missing_resolvconf_dialog()
        ret = msg.exec_()

        if ret == QtGui.QMessageBox.Yes:
            sys.exit()


def _linux_install_missing_scripts(badexec, notfound):
    """
    Try to install the missing up/down scripts.

    :param badexec: error for notifying execution error during command.
    :type badexec: str
    :param notfound: error for notifying missing path.
    :type notfound: str
    :returns: True if the files could be copied successfully.
    :rtype: bool
    """
    success = False
    installer_path = os.path.join(os.getcwd(), "apps", "eip", "files")
    launcher = LinuxVPNLauncher

    # XXX refactor with darwin, same block.

    if os.path.isdir(installer_path):
        fd, tempscript = tempfile.mkstemp(prefix="leap_installer-")
        polfd, pol_tempfile = tempfile.mkstemp(prefix="leap_installer-")
        try:
            pkexec = first(launcher.maybe_pkexec())
            scriptlines = launcher.cmd_for_missing_scripts(installer_path)
            with os.fdopen(fd, 'w') as f:
                f.write(scriptlines)

            st = os.stat(tempscript)
            os.chmod(tempscript, st.st_mode | stat.S_IEXEC | stat.S_IXUSR |
                     stat.S_IXGRP | stat.S_IXOTH)
            cmdline = ["%s %s" % (pkexec, tempscript)]
            ret = subprocess.call(
                cmdline, stdout=subprocess.PIPE,
                shell=True)
            success = ret == 0
            if not success:
                logger.error("Install missing scripts failed.")
        except Exception as exc:
            logger.error(badexec)
            logger.error("Error was: %r" % (exc,))
        finally:
            try:
                os.remove(tempscript)
            except OSError as exc:
                logger.error("%r" % (exc,))
    else:
        logger.error(notfound)
        logger.debug('path searched: %s' % (installer_path,))

    return success


def LinuxInitializer():
    """
    Raise a dialog if needed files are missing.

    Missing files can be either system-wide resolvconf, bitmask-root, or
    policykit file. The dialog will also be raised if some of those files are
    found to have incorrect permissions.
    """
    _linux_check_resolvconf()
    check_missing()
