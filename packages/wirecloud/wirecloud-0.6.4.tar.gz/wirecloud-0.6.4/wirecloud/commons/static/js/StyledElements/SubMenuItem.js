/*global StyledElements*/

(function () {

    "use strict";

    /**
     *
     */
    var SubMenuItem = function SubMenuItem(text, handler, options) {

        if (arguments.length === 0) {
            return true;
        }

        options = Wirecloud.Utils.merge({
            'position': ['right-bottom', 'left-bottom']
        }, options);

        StyledElements.PopupMenuBase.call(this, options);

        this.menuItem = new StyledElements.MenuItem(text, handler);
        this.menuItem.addClassName('submenu');
    };
    SubMenuItem.prototype = new StyledElements.PopupMenuBase({extending: true});

    SubMenuItem.prototype._getContext = function _getContext() {
        if (this.parentMenu instanceof SubMenuItem) {
            return this.parentMenu._getContext();
        } else {
            return this.parentMenu._context;
        }
    };

    SubMenuItem.prototype._menuItemCallback = function _menuItemCallback(menuItem) {
        var currentMenu = this;
        while (currentMenu.parentMenu) {
            currentMenu = currentMenu.parentMenu;
        }
        currentMenu.hide();
        menuItem.run(currentMenu._context);
    };

    SubMenuItem.prototype._setParentPopupMenu = function _setParentPopupMenu(popupMenu) {
        this.parentMenu = popupMenu;

        this.parentMenu.addEventListener('itemOver', function (popupMenu, item) {
            if (item === this.menuItem) {
                this.show(this.menuItem.wrapperElement.getBoundingClientRect());
            } else {
                this.hide();
            }
        }.bind(this));
    };

    SubMenuItem.prototype._getMenuItem = function _getMenuItem() {
        return this.menuItem;
    };

    SubMenuItem.prototype.addEventListener = function addEventListener(eventId, handler) {
        switch (eventId) {
        case 'mouseover':
        case 'click':
            return this.menuItem.addEventListener(eventId, handler);
        default:
            return StyledElements.PopupMenuBase.prototype.addEventListener.call(this, eventId, handler);
        }
    };

    SubMenuItem.prototype.enable = function enable() {
        this.menuItem.enable();
    };

    SubMenuItem.prototype.disable = function disable() {
        this.menuItem.disable();
    };

    SubMenuItem.prototype.setDisabled = function setDisabled(disabled) {
        this.menuItem.setDisabled(disabled);
    };

    SubMenuItem.prototype.destroy = function destroy() {
        if (this.menuItem) {
            this.menuItem.destroy();
        }
        this.menuItem = null;

        StyledElements.PopupMenuBase.prototype.destroy.call(this);
    };


    StyledElements.SubMenuItem = SubMenuItem;

})();
