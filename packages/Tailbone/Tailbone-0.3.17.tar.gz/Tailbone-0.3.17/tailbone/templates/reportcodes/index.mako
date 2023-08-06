## -*- coding: utf-8 -*-
<%inherit file="/grid.mako" />

<%def name="title()">Report Codes</%def>

<%def name="context_menu_items()">
  % if request.has_perm(u'reportcodes.create'):
      <li>${h.link_to(u"Create a new Report Code", url(u'reportcode.create'))}</li>
  % endif
</%def>

${parent.body()}
