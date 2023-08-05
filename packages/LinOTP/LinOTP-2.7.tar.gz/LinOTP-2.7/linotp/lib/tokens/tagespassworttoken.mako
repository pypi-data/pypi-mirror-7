# -*- coding: utf-8 -*-
<!--
 *
 *   LinOTP - the open source solution for two factor authentication
 *   Copyright (C) 2010 - 2014 LSE Leading Security Experts GmbH
 *
 *   This file is part of LinOTP server.
 *
 *   This program is free software: you can redistribute it and/or
 *   modify it under the terms of the GNU Affero General Public
 *   License, version 3, as published by the Free Software Foundation.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU Affero General Public License for more details.
 *
 *   You should have received a copy of the
 *              GNU Affero General Public License
 *   along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 *
 *    E-mail: linotp@lsexperts.de
 *    Contact: www.linotp.org
 *    Support: www.lsexperts.de
 *
 * contains the tagespasswort token web interface
-->


%if c.scope == 'enroll.title' :
${_("Day OTP Token / Tagespasswort")}
%endif

%if c.scope == 'enroll' :

<script>
/*
 * 'typ'_get_enroll_params()
 *
 * this method is called, when the token  is submitted
 * - it will return a hash of parameters for admin/init call
 *
 */

function dpw_get_enroll_params(){
    var params = {};
    params['type'] = 'dpw';
    //params['serial'] = create_serial('DOTP');
    params['otpkey'] 	= $('#dpw_key').val();
	params['description'] =  $('#enroll_dpw_desc').val();

	jQuery.extend(params, add_user_data());

    return params;
}
</script>

<p>${_("Here you can define the 'Tagespasswort' token, that changes every day.")}</p>
<table>
<tr>
	<td><label for="dpw_key">${_("DPW key")}</label></td>
	<td><input type="text" name="dpw_key" id="dpw_key" value="" class="text ui-widget-content ui-corner-all" /></td>
</tr>
<tr>
    <td><label for="enroll_dpw_desc" id='enroll_dpw_desc_label'>${_("Description")}</label></td>
    <td><input type="text" name="enroll_dpw_desc" id="enroll_dpw_desc" value="webGUI_generated" class="text" /></td>
</tr>
</table>


%endif
