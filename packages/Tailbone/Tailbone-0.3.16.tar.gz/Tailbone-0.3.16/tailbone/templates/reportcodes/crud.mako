## -*- coding: utf-8 -*-
<%inherit file="/crud.mako" />

<%def name="context_menu_items()">
  <li>${h.link_to(u"Back to Report Codes", url(u'reportcodes'))}</li>
  % if form.readonly:
      <li>${h.link_to(u"Edit this Report Code", url(u'reportcode.update', uuid=form.fieldset.model.uuid))}</li>
  % elif form.updating:
      <li>${h.link_to(u"View this Report Code", url(u'reportcode.read', uuid=form.fieldset.model.uuid))}</li>
  % endif
</%def>

${parent.body()}
