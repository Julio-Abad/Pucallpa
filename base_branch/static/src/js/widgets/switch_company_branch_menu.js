odoo.define('base_branch.SwitchCompanyBranchMenu', function(require) {
"use strict";


var config = require('web.config');
var core = require('web.core');
var session = require('web.session');
var SystrayMenu = require('web.SystrayMenu');
var Widget = require('web.Widget');

var _t = core._t;

var SwitchCompanyBranchMenu = Widget.extend({
    template: 'SwitchCompanyBranchMenu',
    events: {
        'click .dropdown-item[data-menu] div.log_into': '_onSwitchCompanyBranchClick',
        'keydown .dropdown-item[data-menu] div.log_into': '_onSwitchCompanyBranchClick',
        'click .dropdown-item[data-menu] div.toggle_branch': '_onToggleCompanyBranchClick',
        'keydown .dropdown-item[data-menu] div.toggle_branch': '_onToggleCompanyBranchClick',
    },
    // force this item to be the first one to the left of the UserMenu in the systray
    sequence: 1,
    /**
     * @override
     */
    init: function () {
        this._super.apply(this, arguments);
        this.isMobile = config.device.isMobile;
        this._onSwitchCompanyBranchClick = _.debounce(this._onSwitchCompanyBranchClick, 1500, true);
    },

    /**
     * @override
     */
    willStart: function () {
        var self = this;
        this.allowed_branch_ids = String(session.user_context.allowed_branch_ids)
                                    .split(',')
                                    .map(function (id) {return parseInt(id);});
        this.user_branches = session.user_branches.allowed_companies;
        this.current_branch = this.allowed_branch_ids[0];
        this.current_branch_name = _.find(session.user_branches.allowed_companies, function (branch) {
            return branch[0] === self.current_branch;
        })[1];
        return this._super.apply(this, arguments);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent|KeyEvent} ev
     */
    _onSwitchCompanyBranchClick: function (ev) {
        if (ev.type == 'keydown' && ev.which != $.ui.keyCode.ENTER && ev.which != $.ui.keyCode.SPACE) {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        var dropdownItem = $(ev.currentTarget).parent();
        var dropdownMenu = dropdownItem.parent();
        var branchID = dropdownItem.data('branch-id');
        var allowed_branch_ids = this.allowed_branch_ids;
        if (dropdownItem.find('.fa-square-o').length) {
            // 1 enabled branch: Stay in single branch mode
            if (this.allowed_branch_ids.length === 1) {
                if (this.isMobile) {
                    dropdownMenu = dropdownMenu.parent();
                }
                dropdownMenu.find('.fa-check-square').removeClass('fa-check-square').addClass('fa-square-o');
                dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
                allowed_branch_ids = [branchID];
            } else { // Multi branch mode
                allowed_branch_ids.push(branchID);
                dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
            }
        }
        $(ev.currentTarget).attr('aria-pressed', 'true');
        session.setCompanies(branchID, allowed_branch_ids);
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent|KeyEvent} ev
     */
    _onToggleCompanyBranchClick: function (ev) {
        if (ev.type == 'keydown' && ev.which != $.ui.keyCode.ENTER && ev.which != $.ui.keyCode.SPACE) {
            return;
        }
        ev.preventDefault();
        ev.stopPropagation();
        var dropdownItem = $(ev.currentTarget).parent();
        var branchID = dropdownItem.data('branch-id');
        var allowed_branch_ids = this.allowed_branch_ids;
        var current_branch_id = allowed_branch_ids[0];
        if (dropdownItem.find('.fa-square-o').length) {
            allowed_branch_ids.push(branchID);
            dropdownItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
            $(ev.currentTarget).attr('aria-checked', 'true');
        } else {
            allowed_branch_ids.splice(allowed_branch_ids.indexOf(ID), 1);
            dropdownItem.find('.fa-check-square').addClass('fa-square-o').removeClass('fa-check-square');
            $(ev.currentTarget).attr('aria-checked', 'false');
        }
        session.setCompanies(current_branch_id, allowed_branch_ids);
    },

});

if (session.display_switch_branch_menu) {
    SystrayMenu.Items.push(SwitchCompanyBranchMenu);
}

return SwitchCompanyBranchMenu;

});
