/*
 *     Copyright (c) 2013-2014 CoNWeT Lab., Universidad Politécnica de Madrid
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

/*global gettext, LayoutManagerFactory, OpManagerFactory, Wirecloud, Workspace*/

(function () {

    "use strict";

    var preferencesChanged = function preferencesChanged(preferences, modifiedValues) {
        if ('language' in modifiedValues) {
            window.location.reload();
        }
    };

    /**
     * Loads the Wirecloud Platform.
     */
    Wirecloud.init = function init(options) {

        options = Wirecloud.Utils.merge({
            'monitor': null
        }, options);

        if (options.monitor == null) {
            // Init Layout Manager
            var layoutManager = LayoutManagerFactory.getInstance();
            layoutManager.resizeWrapper();
            options.monitor = layoutManager._startComplexTask(gettext('Loading Wirecloud Platform'), 4);
            layoutManager.logSubTask(gettext('Retrieving Wirecloud code'));
            layoutManager.logStep('');
            layoutManager.logSubTask(gettext('Retrieving initial data'), 4);
        } else if (!(options.monitor instanceof Wirecloud.TaskMonitorModel)) {
            throw new TypeError('Invalid monitor');
        }

        if (typeof options.onSuccess !== 'function') {
            options.onSuccess = function () {
                Wirecloud.HistoryManager.init();
                var state = Wirecloud.HistoryManager.getCurrentState();
                LayoutManagerFactory.getInstance().changeCurrentView('workspace');

                if (state.workspace_name !== '') {
                    var workspace = opManager.workspacesByUserAndName[state.workspace_creator][state.workspace_name];
                    this.changeActiveWorkspace(workspace, null, {
                        onSuccess: function () {
                            this.loadCompleted = true;
                        }.bind(opManager)
                    });
                } else {
                    opManager.addWorkspace(gettext('Workspace'), {replaceNavigationState: true});
                }
            }.bind(this);
        }

        window.addEventListener(
                      "beforeunload",
                      Wirecloud.unload.bind(this),
                      true);

        var opManager = OpManagerFactory.getInstance(); // TODO

        var loaded_modules = 0;
        var checkPlatformReady = function checkPlatformReady() {
            loaded_modules += 1;
            if (loaded_modules === 4) {
                options.onSuccess();
            }
        };

        // Init platform context
        Wirecloud.io.makeRequest(Wirecloud.URLs.PLATFORM_CONTEXT_COLLECTION, {
            method: 'GET',
            requestHeaders: {'Accept': 'application/json'},
            onSuccess: function (response) {
                options.monitor.nextSubtask('Processing initial context data');
                Wirecloud.contextManager = new Wirecloud.ContextManager(Wirecloud, JSON.parse(response.responseText));
                Wirecloud.contextManager.modify({'mode': Wirecloud.constants.CURRENT_MODE});
                LayoutManagerFactory.getInstance().header._initUserMenu();

                // Init theme
                Wirecloud.io.makeRequest(Wirecloud.URLs.THEME_ENTRY.evaluate({name: Wirecloud.contextManager.get('theme')}), {
                    method: 'GET',
                    requestHeaders: {'Accept': 'application/json'},
                    onSuccess: function (response) {
                        Wirecloud.currentTheme = new Wirecloud.ui.Theme(JSON.parse(response.responseText));
                        checkPlatformReady();
                    }
                });

                // Load local catalogue
                Wirecloud.LocalCatalogue.reload({
                    onSuccess: checkPlatformReady,
                    onFailure: function (response) {
                        var msg = Wirecloud.GlobalLogManager.formatAndLog(gettext("Error retrieving available resources: %(errorMsg)s."), response);
                        (new Wirecloud.ui.MessageWindowMenu(msg, Wirecloud.constants.LOGGING.ERROR_MSG)).show();
                    }
                });

            }
        });

        // Init platform preferences
        Wirecloud.io.makeRequest(Wirecloud.URLs.PLATFORM_PREFERENCES, {
            method: 'GET',
            requestHeaders: {'Accept': 'application/json'},
            onSuccess: function (response) {
                var values = JSON.parse(response.responseText);

                Wirecloud.preferences = Wirecloud.PreferenceManager.buildPreferences('platform', values);
            },
            onFailure: function (response) {
                Wirecloud.GlobalLogManager.formatAndLog(gettext("Error retrieving platform preferences data: %(errorMsg)s"), response);
                Wirecloud.preferences = Wirecloud.PreferenceManager.buildPreferences('platform', {});
            },
            onComplete: function () {
                Wirecloud.preferences.addEventListener('post-commit', preferencesChanged.bind(this));
                checkPlatformReady();
            }.bind(this)
        });

        // Load workspace list
        Wirecloud.io.makeRequest(Wirecloud.URLs.WORKSPACE_COLLECTION, {
            method: 'GET',
            requestHeaders: {'Accept': 'application/json'},
            onSuccess: function (response) {
                var workspaces = JSON.parse(response.responseText);

                for (var i = 0; i < workspaces.length; i++) {
                    var workspace = workspaces[i];

                    this.workspaceInstances[workspace.id] = workspace;
                    if (!(workspace.creator in this.workspacesByUserAndName)) {
                        this.workspacesByUserAndName[workspace.creator] = {};
                    }
                    this.workspacesByUserAndName[workspace.creator][workspace.name] = workspace;
                }

                checkPlatformReady();
            }.bind(opManager),
            onFailure: function (response) {
                Wirecloud.GlobalLogManager.formatAndLog(gettext("Error retrieving workspace list"), response);
            }
        });
    };

    /**
     * Unloads the Wirecloud Platform. This method is called, by default, when
     * the unload event is captured.
     */
    Wirecloud.unload = function unload() {
        var layoutManager = LayoutManagerFactory.getInstance();
        layoutManager.hideCover();
        layoutManager._startComplexTask(gettext('Unloading Wirecloud Platform'));

        if (this.activeWorkspace != null) {
            this.activeWorkspace.unload();
            this.activeWorkspace = null;
        }
    };

    Wirecloud.changeActiveWorkspace = function changeActiveWorkspace(workspace, initial_tab, options) {
        var msg, state, steps = this.activeWorkspace != null ? 2 : 1;

        options = Wirecloud.Utils.merge({
            replaceNavigationState: false
        }, options);

        LayoutManagerFactory.getInstance()._startComplexTask(gettext("Changing current workspace"), steps);

        if (this.activeWorkspace != null) {
            this.activeWorkspace.unload();
        }

        state = {
            workspace_creator: workspace.creator,
            workspace_name: workspace.name,
            view: "workspace"
        };
        if (initial_tab) {
            state.tab = initial_tab;
        }
        if (options.replaceNavigationState) {
            Wirecloud.HistoryManager.replaceState(state);
        } else {
            Wirecloud.HistoryManager.pushState(state);
        }

        msg = interpolate(gettext("Downloading workspace (%(name)s) data"), {name: workspace.creator + '/' + workspace.name}, true);
        LayoutManagerFactory.getInstance().logSubTask(msg, 1);
        new Wirecloud.WorkspaceCatalogue(workspace.id, {
            onSuccess: function (workspace_resources) {
                var workspaceUrl = Wirecloud.URLs.WORKSPACE_ENTRY.evaluate({'workspace_id': workspace.id});
                Wirecloud.io.makeRequest(workspaceUrl, {
                    method: 'GET',
                    requestHeaders: {'Accept': 'application/json'},
                    onSuccess: function (response) {
                        var workspace_data = JSON.parse(response.responseText);

                        // Check if the workspace needs to ask some values before loading this workspace
                        if (workspace_data.empty_params.length > 0) {
                            var preferences, preferenceValues, param, i, dialog;

                            preferenceValues = {};
                            for (i = 0; i < workspace_data.empty_params.length; i += 1) {
                                param = workspace_data.empty_params[i];
                                if (workspace_data.preferences[param] != null) {
                                    preferenceValues[param] = workspace_data.preferences[param];
                                }
                            }

                            LayoutManagerFactory.getInstance().header.refresh();
                            preferences = Wirecloud.PreferenceManager.buildPreferences('workspace', preferenceValues, {workspaceState: workspace_data}, workspace_data.empty_params);
                            preferences.addEventListener('post-commit', function () {
                                setTimeout(function () {
                                    Wirecloud.changeActiveWorkspace(workspace, initial_tab, options);
                                }, 0);
                            }.bind(this));

                            LayoutManagerFactory.getInstance()._notifyPlatformReady();
                            dialog = new Wirecloud.ui.PreferencesWindowMenu('workspace', preferences);
                            dialog.setCancelable(false);
                            dialog.show();
                            return;
                        }

                        this.activeWorkspace = new Workspace(workspace_data, workspace_resources);
                        this.activeWorkspace.contextManager.addCallback(function (updated_attributes) {
                            var workspace, old_name;

                            if ('name' in updated_attributes) {
                                workspace = opManager.workspaceInstances[this.activeWorkspace.id];
                                old_name = workspace.name;
                                delete opManager.workspacesByUserAndName[workspace.creator][old_name];

                                workspace.name = updated_attributes.name;
                                opManager.workspacesByUserAndName[workspace.creator][workspace.name] = workspace;
                            }
                        }.bind(this));

                        LayoutManagerFactory.getInstance()._notifyPlatformReady();
                        LayoutManagerFactory.getInstance().header.refresh(); // FIXME

                        if (typeof options.onSuccess === "function") {
                            try {
                                options.onSuccess();
                            } catch (e) {}
                        }
                    }.bind(this)
                });
            }.bind(this)
        });
    };

})();
