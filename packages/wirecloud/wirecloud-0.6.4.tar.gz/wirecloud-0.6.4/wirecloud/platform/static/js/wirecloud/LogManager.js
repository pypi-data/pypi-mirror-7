/*
 *     Copyright (c) 2013 CoNWeT Lab., Universidad Politécnica de Madrid
 *
 *     This file is part of Wirecloud Platform.
 *
 *     Wirecloud Platform is free software: you can redistribute it and/or
 *     modify it under the terms of the GNU Affero General Public License as
 *     published by the Free Software Foundation, either version 3 of the
 *     License, or (at your option) any later version.
 *
 *     Wirecloud is distributed in the hope that it will be useful, but WITHOUT
 *     ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 *     FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
 *     License for more details.
 *
 *     You should have received a copy of the GNU Affero General Public License
 *     along with Wirecloud Platform.  If not, see
 *     <http://www.gnu.org/licenses/>.
 *
 */

/*global console, gettext, interpolate, Wirecloud*/

(function () {

    "use strict";

    var LogManager = function LogManager(parentLogger) {
        this.wrapperElement = document.createElement('div');
        this.parentLogger = parentLogger;
        this.errorCount = 0;
        this.totalCount = 0;
        this.entries = [];
        this.childManagers = [];
        this.closed = false;

        StyledElements.ObjectWithEvents.call(this, ['newentry']);

        if (parentLogger) {
            parentLogger.childManagers.push(this);
        }
    };
    LogManager.prototype = new StyledElements.ObjectWithEvents();

    LogManager.prototype._addEntry = function _addEntry(entry) {

        Object.freeze(entry);

        this.entries.push(entry);
        if (entry.level === Wirecloud.constants.LOGGING.ERROR_MSG) {
            this.errorCount += 1;
        }
        this.totalCount += 1;

        if (this.parentLogger) {
            this.parentLogger._addEntry(entry);
        }

        this.events.newentry.dispatch(this, entry);
    };

    LogManager.prototype.newCycle = function newCycle() {
        this.wrapperElement.insertBefore(document.createElement('hr'), this.wrapperElement.firstChild);
        this.resetCounters();
    };

    LogManager.prototype.log = function log(msg, level) {
        var date, index, logentry, entry;

        date = new Date();
        switch (level) {
        default:
            level = Wirecloud.constants.LOGGING.ERROR_MSG;
        case Wirecloud.constants.LOGGING.ERROR_MSG:
            if ('console' in window && typeof console.error === 'function') {
                console.error(msg);
            }
            break;
        case Wirecloud.constants.LOGGING.WARN_MSG:
            if ('console' in window && typeof console.warn === 'function') {
                console.warn(msg);
            }
            break;
        case Wirecloud.constants.LOGGING.INFO_MSG:
            if ('console' in window && typeof console.info === 'function') {
                console.info(msg);
            }
            break;
        }

        logentry = document.createElement("p");
        while ((index = msg.indexOf("\n")) != -1) {
            logentry.appendChild(document.createTextNode(msg.substring(0, index)));
            logentry.appendChild(document.createElement("br"));
            msg = msg.substring(index + 1);
        }
        logentry.appendChild(document.createTextNode(msg));

        entry = {
            "level": level,
            "msg": logentry.innerHTML,
            "date": date,
            "logManager": this
        };
        this._addEntry(entry);
    };

    LogManager.prototype.formatError = function formatError(format, transport, e) {
        var msg, errorDesc;

        if (e) {
            var context;
            if (e.lineNumber !== undefined) {
                // Firefox
                context = {errorFile: e.fileName, errorLine: e.lineNumber, errorDesc: e.message};
            } else if (e.line !== undefined) {
                // Webkit
                context = {errorFile: e.sourceURL, errorLine: e.line, errorDesc: e.message};
            } else {
                // Other browsers
                var text = gettext("unknown");
                context = {errorFile: text, errorLine: text, errorDesc: e.message};
            }

            msg = interpolate(gettext("JavaScript exception on file %(errorFile)s (line: %(errorLine)s): %(errorDesc)s"),
                      context,
                      true);
        } else {
            try {
                var errorInfo = JSON.parse(transport.responseText);
                msg = errorInfo.description;
            } catch (error) {
                msg = gettext("HTTP Error %(errorCode)s - %(errorDesc)s");
                if (transport.status !== 0 && transport.statusText !== '') {
                    errorDesc = gettext(transport.statusText);
                } else {
                    errorDesc = Wirecloud.constants.HTTP_STATUS_DESCRIPTIONS[transport.status];
                    if (errorDesc == null) {
                        errorDesc = Wirecloud.constants.UNKNOWN_STATUS_CODE_DESCRIPTION;
                    }
                }
                msg = interpolate(msg, {errorCode: transport.status, errorDesc: errorDesc}, true);
            }
        }
        msg = interpolate(format, {errorMsg: msg}, true);

        return msg;
    };

    LogManager.prototype.formatAndLog = function formatAndLog(format, transport, e, level) {
        var msg = this.formatError(format, transport, e);
        this.log(msg, level);

        return msg;
    };

    LogManager.prototype.reset = function reset() {
        var i;

        this.wrapperElement.innerHTML = '';
        this.resetCounters();
        this.entries = [];
        for (i = this.childManagers.length - 1; i >= 0; i -= 1) {
            if (this.childManagers[i].isClosed()) {
                this.childManagers.splice(i, 1);
            } else {
                this.childManagers[i].reset();
            }
        }
    };

    LogManager.prototype.resetCounters = function resetCounters() {
        this.errorCount = 0;
        this.totalCount = 0;
    };

    LogManager.prototype.getErrorCount = function getErrorCount() {
        return this.errorCount;
    };

    LogManager.prototype.close = function close() {
        this.closed = true;
    };

    LogManager.prototype.isClosed = function isClosed() {
        return this.closed;
    };

    Wirecloud.LogManager = LogManager;
    Wirecloud.GlobalLogManager = new LogManager();

})();
