/*
 *     Copyright (c) 2012-2014 CoNWeT Lab., Universidad Politécnica de Madrid
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

/*global LayoutManagerFactory, gettext, StyledElements, Wirecloud */

(function () {

    "use strict";

    var MAC_MIMETYPES = ['application/x-widget+mashable-application-component', 'application/x-operator+mashable-application-component', 'application/x-mashup+mashable-application-component'];

    var CURRENCY_SYMBOL = {
        'EUR': '€',
        'GBP': '£',
        'USD': '$'
    };

    var is_mac_mimetype = function is_mac_mimetype(mimetype) {
        return MAC_MIMETYPES.indexOf(mimetype) !== -1;
    };

    var install = function install(url, catalogue_view, store, monitor) {
        var layoutManager, local_catalogue_view, market_id;

        local_catalogue_view = LayoutManagerFactory.getInstance().viewsByName.marketplace.viewsByName.local;
        layoutManager = LayoutManagerFactory.getInstance();
        layoutManager.logSubTask(gettext('Uploading resource'));

        if (catalogue_view.catalogue.market_user !== 'public') {
            market_id = catalogue_view.catalogue.market_user + '/' + catalogue_view.catalogue.market_name;
        } else {
            market_id = catalogue_view.catalogue.market_name;
        }

        local_catalogue_view.catalogue.addResourceFromURL(url, {
            packaged: true,
            forceCreate: true,
            market_info: {
                name: market_id,
                store: store
            },
            onSuccess: function () {
                LayoutManagerFactory.getInstance().logSubTask(gettext('Resource installed successfully'));
                LayoutManagerFactory.getInstance().logStep('');

                local_catalogue_view.viewsByName.search.mark_outdated();
                catalogue_view.refresh_search_results();
            },
            onFailure: function (msg) {
                Wirecloud.GlobalLogManager.log(msg);
                (new Wirecloud.ui.MessageWindowMenu(msg, Wirecloud.constants.LOGGING.ERROR_MSG)).show();
            },
            onComplete: function () {
                LayoutManagerFactory.getInstance()._notifyPlatformReady();
            }
        });
    };

    var onInstallClick = function onInstallClick(offering, catalogue_view) {
        var layoutManager, monitor, i;

        layoutManager = LayoutManagerFactory.getInstance();
        monitor = layoutManager._startComplexTask(gettext("Importing offering resources into local repository"), 3);

        for (i = 0; i < offering.resources.length; i++) {
            if ('type' in offering.resources[i]) {
                install(offering.resources[i].url, catalogue_view, offering.store);
            }
        }
    };

    var onUninstallClick = function onUninstallClick(offering, catalogue_view) {
        var layoutManager, local_catalogue_view, monitor, i, count;

        layoutManager = LayoutManagerFactory.getInstance();
        local_catalogue_view = LayoutManagerFactory.getInstance().viewsByName.marketplace.viewsByName.local;
        monitor = layoutManager._startComplexTask(gettext("Uninstalling offering resources"), 1);

        count = offering.resources.length;
        for (i = 0; i < offering.resources.length; i++) {
            if ('type' in offering.resources[i]) {
                local_catalogue_view.catalogue.uninstallResource(offering.resources[i], {
                    onSuccess: function () {
                        local_catalogue_view.viewsByName.search.mark_outdated();
                        catalogue_view.viewsByName.search.mark_outdated();
                    },
                    onComplete: function () {
                        if (--count === 0) {
                            LayoutManagerFactory.getInstance()._notifyPlatformReady();
                            catalogue_view.refresh_if_needed();
                        }
                    }
                });
            } else {
                count -= 1;
            }
        }
    };

    var is_single_payment = function is_single_payment(offering) {
        var pricing = offering.pricing[0];
        return pricing.priceComponents.length === 1 && pricing.priceComponents[0].unit.toLowerCase() === 'single payment';
    };

    var OfferingPainter = function OfferingPainter(catalogue_view, offering_template, container, extra_context) {
        if (arguments.length === 0) {
            return;
        }

        this.builder = new StyledElements.GUIBuilder();
        this.catalogue_view = catalogue_view;
        this.structure_template = offering_template;
        this.error_template = '<s:styledgui xmlns:s="http://wirecloud.conwet.fi.upm.es/StyledElements" xmlns:t="http://wirecloud.conwet.fi.upm.es/Template" xmlns="http://www.w3.org/1999/xhtml"><div class="alert alert-block alert-error"><t:message/></div></s:styledgui>';
        this.container = container;
        this.is_details_view = extra_context != null; // TODO
        if (extra_context != null && (typeof extra_context === 'object' || typeof extra_context === 'function')) {
            this.extra_context = extra_context;
        } else {
            this.extra_context = {};
        }
    };

    OfferingPainter.prototype.setError = function setError(message) {
        this.container.clear();

        var contents = this.builder.parse(this.error_template, {
            'message': message
        });

        this.container.appendChild(contents);
    };

    OfferingPainter.prototype.paint = function paint(offering) {
        var extra_context, i, context, offering_element;

        if (typeof this.extra_context === 'function') {
            extra_context = this.extra_context(offering);
        } else {
            extra_context = Wirecloud.Utils.clone(this.extra_context);
        }

        context = Wirecloud.Utils.merge(extra_context, {
            'displayname': offering.getDisplayName(),
            'name': offering.name,
            'owner': offering.owner,
            'store': offering.store,
            'version': offering.version,
            'abstract': offering['abstract'],
            'description': offering.description,
            'type': function () {
                var label = document.createElement('div');
                label.textContent = offering.type;
                label.className = 'label';
                switch (offering.type) {
                case 'widget':
                    label.classList.add('label-success');
                    break;
                case 'operator':
                    label.classList.add('label-warning');
                    break;
                case 'mashup':
                    label.classList.add('label-important');
                    break;
                case 'pack':
                    label.classList.add('label-info');
                    break;
                }

                return label;
            },
            'publicationdate': function () {
                if (offering.publicationdate != null) {
                    return offering.publicationdate.strftime('%x');
                } else {
                    return gettext('N/A');
                }
            },
            'doc': function () {
                var button;

                button = new StyledElements.StyledButton({
                    'plain': true,
                    'class': 'icon-doc',
                    'title': gettext('Documentation')
                });
                button.addEventListener('click', function () {
                    window.open(offering.getUriWiki(), '_blank');
                });

                return button;
            },
            'home': function () {
                var button;

                button = new StyledElements.StyledButton({
                    'plain': true,
                    'class': 'icon-home',
                    'title': gettext('Home page')
                });
                button.addEventListener('click', function () {
                    window.open(offering.getUriWiki(), '_blank');
                });

                return button;
            },
            'rating': this.get_popularity_html.bind(this, offering.rating),
            'mainbutton': function () {
                var button, local_catalogue_view;

                local_catalogue_view = LayoutManagerFactory.getInstance().viewsByName.marketplace.viewsByName.local;

                if (!this.catalogue_view.catalogue.is_purchased(this.offering) && ['widget', 'operator', 'mashup', 'pack'].indexOf(this.offering.type) !== -1) {
                    if (offering.pricing.length == 0 || !('priceComponents' in offering.pricing[0])) {
                        button = new StyledElements.StyledButton({
                            'class': 'mainbutton btn-success',
                            'text': gettext('Free')
                        });
                    } else if (is_single_payment(offering)) {
                        button = new StyledElements.StyledButton({
                            'class': 'mainbutton btn-warning',
                            'text': offering.pricing[0].priceComponents[0].value + ' ' + CURRENCY_SYMBOL[offering.pricing[0].priceComponents[0].currency]
                        });
                    } else {
                        button = new StyledElements.StyledButton({
                            'class': 'mainbutton btn-warning',
                            'text': gettext('Purchase')
                        });
                    }
                    button.addEventListener('click', this.catalogue_view.createUserCommand('buy', this.offering));
                    return button;
                }

                if (['widget', 'operator', 'mashup', 'pack'].indexOf(this.offering.type) !== -1) {

                    for (i = 0; i < this.offering.resources.length; i++) {
                        if (!Wirecloud.LocalCatalogue.resourceExistsId(this.offering.resources[i].id)) {
                            button = new StyledElements.StyledButton({
                                'text': gettext('Install')
                            });

                            button.addEventListener('click', onInstallClick.bind(null, this.offering, this.catalogue_view));
                            break;
                        }
                    }

                    if (!button) {
                        button = new StyledElements.StyledButton({
                            'class': 'btn-danger',
                            'text': gettext('Uninstall')
                        });
                        button.addEventListener('click', onUninstallClick.bind(null, this.offering, this.catalogue_view));
                    }
                } else if (!this.is_details_view) {
                    button = new StyledElements.StyledButton({
                        'text': gettext('Details')
                    });

                    button.addEventListener('click', this.catalogue_view.createUserCommand('showDetails', this.offering));
                } else {
                    return null;
                }
                button.addClassName('mainbutton btn-primary');
                return button;
            }.bind({catalogue_view: this.catalogue_view, offering: offering, is_details_view: this.is_details_view}),
            'image': function () {
                var image = document.createElement('img');
                image.onerror = function (event) {
                    event.target.src = '/static/images/noimage.png';
                };
                image.src = offering.image;
                return image;
            },
            'tags': function (options) {
                return this.painter.renderTagList(this.offering, options.max);
            }.bind({painter: this, offering: offering})
        });

        offering_element = this.builder.parse(this.structure_template, context);

        // TODO "Show details"
        for (i = 0; i < offering_element.elements.length; i += 1) {
            if (!Wirecloud.Utils.XML.isElement(offering_element.elements[i])) {
                continue;
            }
            this.create_simple_command(offering_element.elements[i], '.click_for_details', 'click', this.catalogue_view.createUserCommand('showDetails', offering));
            if (offering_element.elements[i].classList.contains('click_for_details')) {
                offering_element.elements[i].addEventListener('click', this.catalogue_view.createUserCommand('showDetails', offering));
            }
        }

        return offering_element;
    };

    OfferingPainter.prototype.create_simple_command = function (element, selector, _event, handler, required) {
        var i, elements = element.querySelectorAll(selector);

        if (required && elements.length < 1) {
            throw new Error();
        }

        for (i = 0; i < elements.length; i += 1) {
            elements[i].addEventListener(_event, handler);
        }
    };

    OfferingPainter.prototype.get_popularity_html = function (popularity) {
        var on_stars, md_star, off_stars, stars, star, i;

        if (popularity == null || popularity < 1) {
            popularity = 0;
        }

        on_stars = Math.floor(popularity);
        md_star = popularity - on_stars;
        off_stars = 5 - popularity;

        stars = document.createElement('div');
        stars.className = 'rating';

        if (popularity === 0) {
            stars.classList.add('disabled');
        }

        // "On" stars
        for (i = 0; i < on_stars; i += 1) {
            star = document.createElement('span');
            star.className = 'on star';
            stars.appendChild(star);
        }

        if (md_star) {
            star = document.createElement('span');
            star.className = 'middle star';
            stars.appendChild(star);
        }

        // "Off" stars
        for (i = 0; i < Math.floor(off_stars); i += 1) {
            star = document.createElement('span');
            star.className = 'off star';
            stars.appendChild(star);
        }

        return stars;
    };

    Wirecloud.FiWare.ui.OfferingPainter = OfferingPainter;
})();
