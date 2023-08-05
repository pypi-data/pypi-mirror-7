/*
 *     Copyright (c) 2014 CoNWeT Lab., Universidad Politécnica de Madrid
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

/*global gettext, StyledElements, Wirecloud*/

(function () {

    "use strict";

    var EmbedCodeWindowMenu = function EmbedCodeWindowMenu(title, msg) {
        Wirecloud.ui.WindowMenu.call(this, title);

        this.code = new StyledElements.StyledTextArea();
        this.code.insertInto(this.windowContent);

        // Accept button
        this.button = new StyledElements.StyledButton({
            text: gettext('Accept'),
            'class': 'btn-primary'
        });
        this.button.insertInto(this.windowBottom);
        this.button.addEventListener("click", this._closeListener);

        this.setMsg(msg);
    };
    EmbedCodeWindowMenu.prototype = new Wirecloud.ui.WindowMenu();

    EmbedCodeWindowMenu.prototype.setMsg = function setMsg(msg) {
        this.code.setValue(msg);

        this.calculatePosition();
    };

    EmbedCodeWindowMenu.prototype.setFocus = function setFocus() {
        this.code.select();
    };

    Wirecloud.ui.EmbedCodeWindowMenu = EmbedCodeWindowMenu;

})();
